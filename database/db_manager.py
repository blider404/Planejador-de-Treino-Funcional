# database/db_manager.py
import sqlite3
import os
import shutil
from datetime import datetime
from database.models import Exercicio, ItemCircuito

class DatabaseManager:
    def __init__(self, db_dir: str):
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        self.path = os.path.join(self.db_dir, "treino_funcional.db")
        self._criar_e_migrar_tabelas()

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _criar_e_migrar_tabelas(self):
        """Garante a estrutura inicial e faz migrações para novas colunas."""
        with self._conn() as conn:
            # Estrutura Base
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS exercicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    grupo_muscular TEXT,
                    descricao TEXT,
                    video TEXT,
                    tempo_padrao INTEGER DEFAULT 40
                );
                CREATE TABLE IF NOT EXISTS circuitos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    rounds INTEGER DEFAULT 1,
                    descanso_rounds INTEGER DEFAULT 60,
                    tipo_treino TEXT DEFAULT 'Circuito'
                );
                CREATE TABLE IF NOT EXISTS circuito_exercicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    circuito_id INTEGER NOT NULL,
                    exercicio_id INTEGER NOT NULL,
                    ordem INTEGER NOT NULL,
                    tempo INTEGER NOT NULL,
                    descanso_individual INTEGER DEFAULT 10,
                    FOREIGN KEY (circuito_id) REFERENCES circuitos(id) ON DELETE CASCADE,
                    FOREIGN KEY (exercicio_id) REFERENCES exercicios(id) ON DELETE CASCADE
                );
            """)
            
            # Mapeamento de migrações: (tabela, coluna, tipo, default)
            migracoes = [
                ("exercicios", "tipo", "TEXT", "'Força'"),
                ("exercicios", "equipamento", "TEXT", "'Peso corporal'"),
                ("exercicios", "nivel", "TEXT", "'Iniciante'"),
                ("exercicios", "padrao_movimento", "TEXT", "'Outro'"),
                ("circuitos", "tipo_treino", "TEXT", "'Circuito'"),
                ("circuito_exercicios", "descanso_individual", "INTEGER", "10"),
                ("circuito_exercicios", "coluna", "INTEGER", "1")  # <-- Nova coluna para o controle do layout
            ]
            
            for tabela, coluna, tipo, default in migracoes:
                cursor = conn.execute(f"PRAGMA table_info({tabela})")
                colunas = [row["name"] for row in cursor.fetchall()]
                if coluna not in colunas:
                    conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo} DEFAULT {default}")

    # --- Exercícios ---
    def salvar_exercicio(self, ex: Exercicio):
        with self._conn() as conn:
            if ex.id:
                conn.execute("""
                    UPDATE exercicios SET nome=?, grupo_muscular=?, descricao=?, video=?, 
                    tempo_padrao=?, tipo=?, equipamento=?, nivel=?, padrao_movimento=? WHERE id=?
                """, (ex.nome, ex.grupo_muscular, ex.descricao, ex.video, ex.tempo_padrao,
                      ex.tipo, ex.equipamento, ex.nivel, ex.padrao_movimento, ex.id))
            else:
                conn.execute("""
                    INSERT INTO exercicios (nome, grupo_muscular, descricao, video, tempo_padrao, tipo, equipamento, nivel, padrao_movimento) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ex.nome, ex.grupo_muscular, ex.descricao, ex.video, ex.tempo_padrao, ex.tipo, ex.equipamento, ex.nivel, ex.padrao_movimento))

    def deletar_exercicio(self, ex_id):
        with self._conn() as conn:
            conn.execute("DELETE FROM exercicios WHERE id=?", (ex_id,))

    def listar_exercicios(self, filtros: dict):
        query = "SELECT * FROM exercicios WHERE 1=1"
        params = []
        for key, val in filtros.items():
            if val and val != "Todos":
                if key == "nome":
                    query += " AND nome LIKE ?"
                    params.append(f"%{val}%")
                else:
                    query += f" AND {key} = ?"
                    params.append(val)
        query += " ORDER BY nome COLLATE NOCASE"
        with self._conn() as conn:
            return conn.execute(query, params).fetchall()

    def get_estatisticas(self):
        with self._conn() as conn:
            ex_count = conn.execute("SELECT COUNT(*) FROM exercicios").fetchone()[0]
            circ_count = conn.execute("SELECT COUNT(*) FROM circuitos").fetchone()[0]
            grupos = conn.execute("SELECT COUNT(DISTINCT grupo_muscular) FROM exercicios").fetchone()[0]
            recentes = conn.execute("SELECT nome FROM circuitos ORDER BY id DESC LIMIT 5").fetchall()
            return ex_count, circ_count, grupos, [r[0] for r in recentes]

    # --- Circuitos ---
    def salvar_circuito(self, nome, rounds, descanso_round, tipo_treino, itens: list):
        with self._conn() as conn:
            existente = conn.execute("SELECT id FROM circuitos WHERE nome=?", (nome,)).fetchone()
            if existente:
                circuito_id = existente["id"]
                conn.execute(
                    "UPDATE circuitos SET rounds=?, descanso_rounds=?, tipo_treino=? WHERE id=?",
                    (rounds, descanso_round, tipo_treino, circuito_id),
                )
                conn.execute("DELETE FROM circuito_exercicios WHERE circuito_id=?", (circuito_id,))
            else:
                cur = conn.execute(
                    "INSERT INTO circuitos (nome, rounds, descanso_rounds, tipo_treino) VALUES (?, ?, ?, ?)",
                    (nome, rounds, descanso_round, tipo_treino)
                )
                circuito_id = cur.lastrowid

            for ordem, item in enumerate(itens):
                # Inclui o parâmetro 'coluna' no salvamento do banco
                conn.execute(
                    "INSERT INTO circuito_exercicios (circuito_id, exercicio_id, ordem, tempo, descanso_individual, coluna) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (circuito_id, item.exercicio_id, ordem, item.tempo, item.descanso_individual, item.coluna),
                )
            return circuito_id

    def listar_circuitos(self):
        with self._conn() as conn:
            return conn.execute("SELECT * FROM circuitos ORDER BY nome COLLATE NOCASE").fetchall()

    def carregar_circuito(self, circuito_id):
        with self._conn() as conn:
            circuito = conn.execute("SELECT * FROM circuitos WHERE id=?", (circuito_id,)).fetchone()
            # Busca a coluna configurada para cada exercício
            itens_db = conn.execute("""
                    SELECT ce.tempo, ce.descanso_individual, ce.coluna, e.id as ex_id, e.nome, e.grupo_muscular, e.tipo, e.nivel
                    FROM circuito_exercicios ce
                    JOIN exercicios e ON e.id = ce.exercicio_id
                    WHERE ce.circuito_id = ? ORDER BY ce.ordem
                """, (circuito_id,)).fetchall()
            itens = [ItemCircuito(
                exercicio_id=r["ex_id"], nome=r["nome"], tempo=r["tempo"],
                descanso_individual=r["descanso_individual"], grupo=r["grupo_muscular"],
                tipo=r["tipo"], nivel=r["nivel"], coluna=r["coluna"] # Adicionado aqui para resgatar a coluna correta
            ) for r in itens_db]
            return circuito, itens

    def deletar_circuito(self, circuito_id):
        with self._conn() as conn:
            conn.execute("DELETE FROM circuitos WHERE id=?", (circuito_id,))

    def backup(self, dest_dir: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_treino_funcional_{timestamp}.db"
        dest_path = os.path.join(dest_dir, backup_name)
        shutil.copy2(self.path, dest_path)
        return dest_path
        
    def restaurar(self, backup_path: str):
        shutil.copy2(backup_path, self.path)