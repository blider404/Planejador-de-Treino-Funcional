# ui/tabs.py
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import webbrowser
import os
import sys

from database.models import Exercicio, ItemCircuito
from utils.helpers import formatar_tempo, calcular_totais_circuito
from services.export_service import ExportService

# Constantes Visuais
COR_FUNDO = "#101418"
COR_CARD = "#181d24"
COR_DESTAQUE = "#00c2a8"
COR_DESTAQUE_HOVER = "#00a390"
COR_ALERTA = "#ff5d5d"
COR_TEXTO_SEC = "#8a95a5"

# Metadados
TIPOS = ["Força", "Cardio", "Mobilidade", "Core", "Potência", "Resistência", "Flexibilidade"]
NIVEIS = ["Iniciante", "Intermediário", "Avançado"]
EQUIPAMENTOS = ["Peso corporal", "Halter", "Barra", "Kettlebell", "Elástico", "Corda", "Caixa", "Máquina", "Outro"]
PADROES = ["Agachar", "Empurrar", "Puxar", "Saltar", "Correr", "Rotacionar", "Locomoção", "Estabilização", "Outro"]
GRUPOS = ["Corpo inteiro", "Membros inferiores", "Membros superiores", "Core / Abdômen", "Cardio", "Mobilidade", "Costas", "Peito", "Ombros"]
TIPOS_TREINO = ["Circuito", "HIIT", "Tabata", "AMRAP", "EMOM", "For Time", "Treino Livre"]

class DashboardTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._montar()
        
    def _montar(self):
        title = ctk.CTkLabel(self, text="SOLDIER ACADEMIA\nPLANEJADOR DE TREINO FUNCIONAL", 
                             font=ctk.CTkFont(size=24, weight="bold"), text_color=COR_DESTAQUE)
        title.pack(pady=(20, 40))

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=40)
        
        self.lbl_ex = self._criar_card("EXERCÍCIOS", "0")
        self.lbl_circ = self._criar_card("CIRCUITOS", "0")
        self.lbl_grp = self._criar_card("GRUPOS", "0")
        
        self.recentes_frame = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=10)
        self.recentes_frame.pack(fill="both", expand=True, padx=40, pady=30)
        ctk.CTkLabel(self.recentes_frame, text="Últimos Circuitos Criados:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.lbl_recentes = ctk.CTkLabel(self.recentes_frame, text="", text_color=COR_TEXTO_SEC)
        self.lbl_recentes.pack()

    def _criar_card(self, titulo, valor):
        card = ctk.CTkFrame(self.cards_frame, fg_color=COR_CARD, corner_radius=10, width=200, height=120)
        card.pack(side="left", expand=True, padx=10)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14), text_color=COR_TEXTO_SEC).pack(pady=(20,5))
        lbl_val = ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=36, weight="bold"))
        lbl_val.pack()
        return lbl_val

    def atualizar_dados(self):
        ex_cnt, circ_cnt, grp_cnt, recentes = self.app.db.get_estatisticas()
        self.lbl_ex.configure(text=str(ex_cnt))
        self.lbl_circ.configure(text=str(circ_cnt))
        self.lbl_grp.configure(text=str(grp_cnt))
        self.lbl_recentes.configure(text="\n".join(recentes) if recentes else "Nenhum circuito cadastrado.")


class ExerciciosTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.exercicio_id_atual = None
        self._montar()
        
    def _montar(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Formulário Expandido
        form = ctk.CTkScrollableFrame(self, fg_color=COR_CARD, corner_radius=12)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=4)
        
        ctk.CTkLabel(form, text="Cadastrar / Editar Exercício", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.entries = {}
        def add_combo(label, values):
            ctk.CTkLabel(form, text=label, text_color=COR_TEXTO_SEC).pack(anchor="w", padx=10)
            cb = ctk.CTkComboBox(form, values=values)
            cb.pack(fill="x", padx=10, pady=(0, 10))
            return cb
            
        def add_entry(label, placeholder):
            ctk.CTkLabel(form, text=label, text_color=COR_TEXTO_SEC).pack(anchor="w", padx=10)
            e = ctk.CTkEntry(form, placeholder_text=placeholder)
            e.pack(fill="x", padx=10, pady=(0, 10))
            return e

        self.entries['nome'] = add_entry("Nome do exercício *", "Ex: Agachamento")
        self.entries['grupo'] = add_combo("Grupo muscular", GRUPOS)
        self.entries['tipo'] = add_combo("Tipo", TIPOS)
        self.entries['equipamento'] = add_combo("Equipamento", EQUIPAMENTOS)
        self.entries['nivel'] = add_combo("Nível", NIVEIS)
        self.entries['padrao'] = add_combo("Padrão de Movimento", PADROES)
        self.entries['tempo'] = add_entry("Tempo padrão (segundos)", "40")
        self.entries['tempo'].insert(0, "40")
        
        ctk.CTkLabel(form, text="Vídeo", text_color=COR_TEXTO_SEC).pack(anchor="w", padx=10)
        vid_frame = ctk.CTkFrame(form, fg_color="transparent")
        vid_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.entries['video'] = ctk.CTkEntry(vid_frame)
        self.entries['video'].pack(side="left", fill="x", expand=True, padx=(0,5))
        ctk.CTkButton(vid_frame, text="📁", width=30, command=self._selecionar_video).pack(side="right")
        
        ctk.CTkButton(form, text="Salvar Exercício", fg_color=COR_DESTAQUE, hover_color=COR_DESTAQUE_HOVER,
                      command=self._salvar).pack(fill="x", padx=10, pady=15)
        ctk.CTkButton(form, text="Limpar", fg_color="transparent", border_width=1, 
                      command=self._limpar).pack(fill="x", padx=10)

        # Filtros e Lista
        direita = ctk.CTkFrame(self, fg_color="transparent")
        direita.grid(row=0, column=1, sticky="nsew", pady=4)
        direita.grid_rowconfigure(1, weight=1)
        direita.grid_columnconfigure(0, weight=1)
        
        filtros = ctk.CTkFrame(direita, fg_color="transparent")
        filtros.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.busca_nome = ctk.CTkEntry(filtros, placeholder_text="🔎 Buscar por nome...")
        self.busca_nome.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.busca_nome.bind("<KeyRelease>", lambda e: self.atualizar_lista())
        
        self.busca_grupo = ctk.CTkComboBox(filtros, values=["Todos"] + GRUPOS, command=lambda v: self.atualizar_lista())
        self.busca_grupo.set("Todos")
        self.busca_grupo.pack(side="left")

        self.lista = ctk.CTkScrollableFrame(direita, fg_color="transparent")
        self.lista.grid(row=1, column=0, sticky="nsew")

    def _selecionar_video(self):
        caminho = filedialog.askopenfilename(title="Selecione o vídeo")
        if caminho:
            self.entries['video'].delete(0, "end")
            self.entries['video'].insert(0, caminho)

    def _limpar(self):
        self.exercicio_id_atual = None
        for k, w in self.entries.items():
            if isinstance(w, ctk.CTkEntry):
                w.delete(0, "end")
        self.entries['tempo'].insert(0, "40")

    def _salvar(self):
        nome = self.entries['nome'].get().strip()
        if not nome:
            messagebox.showwarning("Erro", "Nome é obrigatório.")
            return
        try:
            tempo = int(self.entries['tempo'].get())
            if tempo <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Erro", "Tempo deve ser numérico e positivo.")
            return

        ex = Exercicio(
            id=self.exercicio_id_atual, nome=nome, grupo_muscular=self.entries['grupo'].get(),
            descricao="", video=self.entries['video'].get(), tempo_padrao=tempo,
            tipo=self.entries['tipo'].get(), equipamento=self.entries['equipamento'].get(),
            nivel=self.entries['nivel'].get(), padrao_movimento=self.entries['padrao'].get()
        )
        self.app.db.salvar_exercicio(ex)
        self._limpar()
        self.atualizar_lista()
        self.app.tabs['circuitos'].atualizar_disponiveis()
        self.app.tabs['dashboard'].atualizar_dados()

    def atualizar_lista(self):
        for w in self.lista.winfo_children(): w.destroy()
        filtros = {"nome": self.busca_nome.get(), "grupo_muscular": self.busca_grupo.get()}
        exercicios = self.app.db.listar_exercicios(filtros)
        
        for ex in exercicios:
            card = ctk.CTkFrame(self.lista, fg_color=COR_CARD, corner_radius=8)
            card.pack(fill="x", pady=4, padx=2)
            lbl = ctk.CTkLabel(card, text=f"{ex['nome']} | {ex['grupo_muscular']} | {ex['tipo']}", anchor="w")
            lbl.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            
            ctk.CTkButton(card, text="Editar", width=60, fg_color="transparent", border_width=1,
                          command=lambda e=ex: self._editar(e)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="Excluir", width=60, fg_color="transparent", border_width=1, 
                          text_color=COR_ALERTA, border_color=COR_ALERTA,
                          command=lambda i=ex['id']: self._excluir(i)).pack(side="right", padx=5)

    def _editar(self, ex):
        self._limpar()
        self.exercicio_id_atual = ex['id']
        self.entries['nome'].insert(0, ex['nome'])
        self.entries['grupo'].set(ex['grupo_muscular'])
        self.entries['tipo'].set(ex['tipo'])
        self.entries['equipamento'].set(ex['equipamento'])
        self.entries['nivel'].set(ex['nivel'])
        self.entries['padrao'].set(ex['padrao_movimento'])
        self.entries['tempo'].delete(0, "end")
        self.entries['tempo'].insert(0, str(ex['tempo_padrao']))
        self.entries['video'].insert(0, ex['video'] or "")

    def _excluir(self, ex_id):
        if messagebox.askyesno("Confirmar", "Excluir exercício?"):
            self.app.db.deletar_exercicio(ex_id)
            self.atualizar_lista()
            self.app.tabs['circuitos'].atualizar_disponiveis()


class CircuitosTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.itens_circuito = []
        self.num_colunas = 2  # Padrão de 2 colunas
        self._montar()
        
    def _montar(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        # Header
        topo = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=12)
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(topo, text="Nome:").pack(side="left", padx=10)
        self.entry_nome = ctk.CTkEntry(topo, width=200)
        self.entry_nome.pack(side="left", pady=10)
        
        ctk.CTkLabel(topo, text="Tipo:").pack(side="left", padx=(20, 10))
        self.combo_tipo = ctk.CTkComboBox(topo, values=TIPOS_TREINO, width=120)
        self.combo_tipo.pack(side="left", pady=10)
        
        ctk.CTkButton(topo, text="💾 Salvar Circuito", fg_color=COR_DESTAQUE, hover_color=COR_DESTAQUE_HOVER,
                      command=self._salvar).pack(side="left", padx=20)
        ctk.CTkButton(topo, text="Limpar", fg_color="transparent", border_width=1, command=self.limpar_circuito).pack(side="left")

        # Exercícios Disponíveis (Esquerda)
        esq = ctk.CTkFrame(self, fg_color="transparent")
        esq.grid(row=1, column=0, sticky="nsew", padx=(0,10))
        ctk.CTkLabel(esq, text="Disponíveis", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.scroll_disp = ctk.CTkScrollableFrame(esq, fg_color=COR_CARD)
        self.scroll_disp.pack(fill="both", expand=True, pady=(5,0))

        # Montador de Circuito (Direita)
        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.grid(row=1, column=1, sticky="nsew")
        
        # Cabeçalho da área do montador (Título + Controle de colunas)
        header_dir = ctk.CTkFrame(dir_frame, fg_color="transparent")
        header_dir.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header_dir, text="Circuito Montado", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        ctk.CTkLabel(header_dir, text="Layout:", text_color=COR_TEXTO_SEC).pack(side="left", padx=(20, 5))
        self.combo_colunas = ctk.CTkComboBox(header_dir, values=["1 Coluna", "2 Colunas", "3 Colunas", "4 Colunas", "5 Colunas"], 
                                             width=110, command=self._alterar_colunas)
        self.combo_colunas.set("2 Colunas")
        self.combo_colunas.pack(side="left")

        self.scroll_circ = ctk.CTkScrollableFrame(dir_frame, fg_color=COR_CARD)
        self.scroll_circ.pack(fill="both", expand=True)
        
        # Rodapé (Parâmetros Globais)
        rodape = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=12)
        rodape.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        def add_param(label, default):
            f = ctk.CTkFrame(rodape, fg_color="transparent")
            f.pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(f, text=label).pack(anchor="w")
            e = ctk.CTkEntry(f, width=70)
            e.insert(0, str(default))
            e.pack()
            e.bind("<KeyRelease>", lambda ev: self._atualizar_rodape())
            return e
            
        self.entry_rounds = add_param("Rounds", 3)
        self.entry_desc_global = add_param("Descanso Padrão (s)", 10)
        self.entry_desc_round = add_param("Desc. entre Rounds (s)", 60)
        
        self.lbl_totais = ctk.CTkLabel(rodape, text="⏱ TEMPO TOTAL: 0s", font=ctk.CTkFont(size=18, weight="bold"), text_color=COR_DESTAQUE)
        self.lbl_totais.pack(side="right", padx=20, pady=15)
        
        self.atualizar_disponiveis()

    def _alterar_colunas(self, escolha):
        self.num_colunas = int(escolha.split()[0])
        self.atualizar_montador()

    def _ler_ints(self):
        try:
            r = max(1, int(self.entry_rounds.get() or 1))
            dg = max(0, int(self.entry_desc_global.get() or 0))
            dr = max(0, int(self.entry_desc_round.get() or 0))
            return r, dg, dr
        except ValueError:
            return 1, 10, 60

    def atualizar_disponiveis(self):
        for w in self.scroll_disp.winfo_children(): w.destroy()
        for ex in self.app.db.listar_exercicios({}):
            f = ctk.CTkFrame(self.scroll_disp, fg_color=COR_FUNDO)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=ex['nome']).pack(side="left", padx=5)
            ctk.CTkButton(f, text="+", width=30, fg_color=COR_DESTAQUE, hover_color=COR_DESTAQUE_HOVER,
                          command=lambda e=ex: self._add_item(e)).pack(side="right", padx=5, pady=5)

    def _add_item(self, ex):
        _, desc_global, _ = self._ler_ints()
        self.itens_circuito.append(ItemCircuito(
            exercicio_id=ex['id'], nome=ex['nome'], tempo=ex['tempo_padrao'],
            descanso_individual=desc_global, grupo=ex['grupo_muscular'],
            tipo=ex['tipo'], nivel=ex['nivel']
        ))
        self.atualizar_montador()

    def _remover_item(self, idx):
        self.itens_circuito.pop(idx)
        self.atualizar_montador()

    def _mover_item(self, idx, direcao):
        n_idx = idx + direcao
        if 0 <= n_idx < len(self.itens_circuito):
            self.itens_circuito[idx], self.itens_circuito[n_idx] = self.itens_circuito[n_idx], self.itens_circuito[idx]
            self.atualizar_montador()

    def _update_val(self, idx, attr, val):
        try:
            v = int(val)
            setattr(self.itens_circuito[idx], attr, max(0, v))
            self._atualizar_rodape()
        except ValueError:
            pass

    def atualizar_montador(self):
        for w in self.scroll_circ.winfo_children(): 
            w.destroy()
            
        # Limpa o mapeamento de colunas antigo e aplica o novo layout grid dinâmico
        for c in range(5):
            self.scroll_circ.grid_columnconfigure(c, weight=0)
        for c in range(self.num_colunas):
            self.scroll_circ.grid_columnconfigure(c, weight=1)
        
        for i, it in enumerate(self.itens_circuito):
            row = i // self.num_colunas
            col = i % self.num_colunas
            
            card = ctk.CTkFrame(self.scroll_circ, fg_color=COR_FUNDO, corner_radius=8, border_width=1, border_color="#333")
            card.grid(row=row, column=col, sticky="ew", pady=4, padx=5)
            
            # Header do Card (Ordem, Setas e Fechar)
            top_card = ctk.CTkFrame(card, fg_color="transparent")
            top_card.pack(fill="x", padx=8, pady=(8, 0))
            
            ctk.CTkLabel(top_card, text=f"{i+1:02d}", text_color=COR_DESTAQUE, font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkButton(top_card, text="↑", width=25, fg_color="transparent", border_width=1, command=lambda idx=i: self._mover_item(idx, -1)).pack(side="left", padx=(10,2))
            ctk.CTkButton(top_card, text="↓", width=25, fg_color="transparent", border_width=1, command=lambda idx=i: self._mover_item(idx, 1)).pack(side="left")
            ctk.CTkButton(top_card, text="✕", width=25, fg_color="transparent", text_color=COR_ALERTA, hover_color=COR_ALERTA, command=lambda idx=i: self._remover_item(idx)).pack(side="right")
            
            # Nome do Exercício
            ctk.CTkLabel(card, text=it.nome, font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=10, pady=5)
            
            # Entradas de Tempo e Descanso Compactadas
            tempos = ctk.CTkFrame(card, fg_color="transparent")
            tempos.pack(pady=(0, 10))
            
            ctk.CTkLabel(tempos, text="Tempo:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0,5))
            e_t = ctk.CTkEntry(tempos, width=40, height=24, justify="center")
            e_t.insert(0, str(it.tempo))
            e_t.pack(side="left")
            e_t.bind("<KeyRelease>", lambda ev, idx=i: self._update_val(idx, "tempo", ev.widget.get()))
            
            ctk.CTkLabel(tempos, text="Desc:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(15,5))
            e_d = ctk.CTkEntry(tempos, width=40, height=24, justify="center")
            e_d.insert(0, str(it.descanso_individual))
            e_d.pack(side="left")
            e_d.bind("<KeyRelease>", lambda ev, idx=i: self._update_val(idx, "descanso_individual", ev.widget.get()))

        self._atualizar_rodape()

    def _atualizar_rodape(self):
        r, _, dr = self._ler_ints()
        t_trab, t_desc, total = calcular_totais_circuito(self.itens_circuito, r, dr)
        self.lbl_totais.configure(text=f"Trabalho: {formatar_tempo(t_trab)} | Descanso: {formatar_tempo(t_desc)} | ⏱ TOTAL: {formatar_tempo(total)}")
        
        # Sincronizar Análise
        if 'analise' in self.app.tabs:
            self.app.tabs['analise'].atualizar_analise(self.itens_circuito, r, dr)

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        if not nome or not self.itens_circuito:
            messagebox.showwarning("Aviso", "Informe o nome e adicione exercícios.")
            return
        r, _, dr = self._ler_ints()
        self.app.db.salvar_circuito(nome, r, dr, self.combo_tipo.get(), self.itens_circuito)
        messagebox.showinfo("Sucesso", "Circuito salvo!")
        self.app.tabs['biblioteca'].atualizar_lista()
        self.app.tabs['dashboard'].atualizar_dados()

    def limpar_circuito(self):
        self.entry_nome.delete(0, "end")
        self.itens_circuito.clear()
        self.atualizar_montador()

    def carregar_para_edicao(self, circ_id):
        circuito, itens = self.app.db.carregar_circuito(circ_id)
        self.limpar_circuito()
        self.entry_nome.insert(0, circuito['nome'])
        self.combo_tipo.set(circuito['tipo_treino'])
        self.entry_rounds.delete(0, "end"); self.entry_rounds.insert(0, str(circuito['rounds']))
        self.entry_desc_round.delete(0, "end"); self.entry_desc_round.insert(0, str(circuito['descanso_rounds']))
        self.itens_circuito = itens
        self.atualizar_montador()

class AnaliseTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._montar()
        
    def _montar(self):
        ctk.CTkLabel(self, text="ANÁLISE DO CIRCUITO ATUAL", font=ctk.CTkFont(size=20, weight="bold"), text_color=COR_DESTAQUE).pack(pady=20)
        
        self.painel = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=12)
        self.painel.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        # Resumo
        self.lbl_resumo = ctk.CTkLabel(self.painel, text="Monte um circuito na aba anterior para ver a análise.", font=ctk.CTkFont(size=14))
        self.lbl_resumo.pack(pady=20)
        
        # Barras
        self.frame_barras = ctk.CTkFrame(self.painel, fg_color="transparent")
        self.frame_barras.pack(fill="x", padx=40, pady=10)
        
        self.lbl_trab_desc = ctk.CTkLabel(self.frame_barras, text="TRABALHO x DESCANSO", font=ctk.CTkFont(weight="bold"))
        self.lbl_trab_desc.pack(anchor="w")
        self.prog_trab = ctk.CTkProgressBar(self.frame_barras, fg_color=COR_TEXTO_SEC, progress_color=COR_DESTAQUE)
        self.prog_trab.pack(fill="x", pady=5)
        self.lbl_perc = ctk.CTkLabel(self.frame_barras, text="")
        self.lbl_perc.pack(anchor="w")

        # Didático
        self.lbl_foco = ctk.CTkLabel(self.painel, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_foco.pack(pady=20)
        
        ctk.CTkLabel(self.painel, text="* Os índices apresentados são estimativas didáticas do aplicativo.", text_color=COR_TEXTO_SEC).pack(side="bottom", pady=10)

    def atualizar_analise(self, itens, rounds, dr):
        if not itens:
            self.lbl_resumo.configure(text="Circuito Vazio.")
            self.prog_trab.set(0)
            self.lbl_perc.configure(text="")
            self.lbl_foco.configure(text="")
            return

        t_trab, t_desc, total = calcular_totais_circuito(itens, rounds, dr)
        
        resumo = f"EXERCÍCIOS: {len(itens)}   |   ROUNDS: {rounds}\n\n"
        resumo += f"TEMPO DE TRABALHO: {formatar_tempo(t_trab)}\n"
        resumo += f"TEMPO DE DESCANSO: {formatar_tempo(t_desc)}\n\n"
        resumo += f"TEMPO TOTAL: {formatar_tempo(total)}"
        self.lbl_resumo.configure(text=resumo)
        
        if total > 0:
            pct_trab = t_trab / total
            self.prog_trab.set(pct_trab)
            self.lbl_perc.configure(text=f"Trabalho: {int(pct_trab*100)}%   |   Descanso: {int((1-pct_trab)*100)}%")
            
        # Analise Didática Simples
        grupos = {}
        for it in itens:
            g = it.grupo or "Outro"
            grupos[g] = grupos.get(g, 0) + 1
            
        foco = max(grupos, key=grupos.get) if grupos else "Misto"
        self.lbl_foco.configure(text=f"FOCO PRINCIPAL: {foco.upper()}\nEQUILÍBRIO: {'BOM' if len(grupos)>2 else 'MUITO FOCADO'}")


class BibliotecaTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._montar()
        
    def _montar(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(topo, text="MEUS CIRCUITOS", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=10)
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")

    def atualizar_lista(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        circuitos = self.app.db.listar_circuitos()
        if not circuitos:
            ctk.CTkLabel(self.scroll, text="Nenhum circuito salvo.", text_color=COR_TEXTO_SEC).pack(pady=20)
            return
            
        for c in circuitos:
            card = ctk.CTkFrame(self.scroll, fg_color=COR_CARD, corner_radius=10)
            card.pack(fill="x", pady=6, padx=10)
            
            esq = ctk.CTkFrame(card, fg_color="transparent")
            esq.pack(side="left", padx=15, pady=15, fill="both", expand=True)
            ctk.CTkLabel(esq, text=c['nome'], font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(esq, text=f"{c['tipo_treino']} • Rounds: {c['rounds']} • Descanso Rounds: {c['descanso_rounds']}s", text_color=COR_TEXTO_SEC, anchor="w").pack(fill="x")
            
            dir_f = ctk.CTkFrame(card, fg_color="transparent")
            dir_f.pack(side="right", padx=15, pady=15)
            
            ctk.CTkButton(dir_f, text="Abrir / Editar", width=100, fg_color=COR_DESTAQUE, hover_color=COR_DESTAQUE_HOVER,
                          command=lambda id=c['id']: self._abrir(id)).pack(side="left", padx=5)
            ctk.CTkButton(dir_f, text="Duplicar", width=80, fg_color="transparent", border_width=1,
                          command=lambda id=c['id'], nome=c['nome']: self._duplicar(id, nome)).pack(side="left", padx=5)
            ctk.CTkButton(dir_f, text="Exportar", width=80, fg_color="transparent", border_width=1,
                          command=lambda id=c['id']: self._exportar(id)).pack(side="left", padx=5)
            ctk.CTkButton(dir_f, text="Excluir", width=80, fg_color="transparent", border_width=1, text_color=COR_ALERTA, border_color=COR_ALERTA,
                          command=lambda id=c['id']: self._excluir(id)).pack(side="left", padx=5)

    def _abrir(self, circ_id):
        self.app.tabs['circuitos'].carregar_para_edicao(circ_id)
        self.app.tabview.set("🧩  Circuitos")

    def _duplicar(self, circ_id, nome):
        circ, itens = self.app.db.carregar_circuito(circ_id)
        novo_nome = f"{nome} - Cópia"
        self.app.db.salvar_circuito(novo_nome, circ['rounds'], circ['descanso_rounds'], circ['tipo_treino'], itens)
        self.atualizar_lista()
        self.app.tabs['dashboard'].atualizar_dados()

    def _excluir(self, circ_id):
        if messagebox.askyesno("Confirmar", "Excluir circuito permanentemente?"):
            self.app.db.deletar_circuito(circ_id)
            self.atualizar_lista()
            self.app.tabs['dashboard'].atualizar_dados()
            
    def _exportar(self, circ_id):
        circ, itens = self.app.db.carregar_circuito(circ_id)
        caminho = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf"), ("Texto", "*.txt"), ("JSON", "*.json")], title="Exportar Ficha de Treino")
        if caminho:
            ext = os.path.splitext(caminho)[1].lower()
            if ext == ".pdf": ExportService.exportar_pdf(circ['nome'], circ['rounds'], circ['descanso_rounds'], itens, caminho)
            elif ext == ".json": ExportService.exportar_json(circ['nome'], circ['rounds'], circ['descanso_rounds'], itens, caminho)
            else: ExportService.exportar_txt(circ['nome'], circ['rounds'], circ['descanso_rounds'], itens, caminho)
            messagebox.showinfo("Sucesso", f"Arquivo exportado: {caminho}")


class ConfiguracoesTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._montar()
        
    def _montar(self):
        f = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=12)
        f.pack(pady=40, padx=40, fill="both", expand=True)
        
        ctk.CTkLabel(f, text="BACKUP DO SISTEMA", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 20))
        ctk.CTkLabel(f, text="O backup salva todo o banco de dados SQLite contendo exercícios e circuitos.", text_color=COR_TEXTO_SEC).pack(pady=(0, 20))
        
        ctk.CTkButton(f, text="Fazer Backup Agora", fg_color=COR_DESTAQUE, hover_color=COR_DESTAQUE_HOVER, command=self._backup).pack(pady=10)
        ctk.CTkButton(f, text="Restaurar Backup", fg_color="transparent", border_width=1, command=self._restaurar).pack(pady=10)

    def _backup(self):
        dir_dest = filedialog.askdirectory(title="Selecione onde salvar o backup")
        if dir_dest:
            path = self.app.db.backup(dir_dest)
            messagebox.showinfo("Backup", f"Backup realizado com sucesso em:\n{path}")

    def _restaurar(self):
        if messagebox.askyesno("Aviso Crítico", "A restauração APAGARÁ os dados atuais.\nTem certeza absoluta?"):
            file = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
            if file:
                self.app.db.restaurar(file)
                messagebox.showinfo("Restauração", "Sistema restaurado. Reinicie o aplicativo.")
                sys.exit()