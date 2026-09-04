# services/export_service.py
import json
import os
from fpdf import FPDF
from utils.helpers import formatar_tempo, calcular_totais_circuito

class ExportService:
    @staticmethod
    def exportar_txt(nome, rounds, desc_round, itens, path):
        _, _, total = calcular_totais_circuito(itens, rounds, desc_round)
        with open(path, 'w', encoding='utf-8') as f:
            f.write("========================================\n")
            f.write("            SOLDIER ACADEMIA            \n")
            f.write("        PLANEJAMENTO DE CIRCUITO        \n")
            f.write("========================================\n\n")
            f.write(f"TREINO: {nome.upper()}\n")
            f.write(f"ROUNDS: {rounds}\n")
            f.write(f"TEMPO TOTAL: {formatar_tempo(total)}\n\n")
            f.write("----------------------------------------\n")
            f.write(f"{'#':<4} {'EXERCÍCIO':<25} {'TEMPO':<6} {'DESC'}\n")
            f.write("----------------------------------------\n")
            for i, item in enumerate(itens, 1):
                f.write(f"{i:02d}   {item.nome:<25} {item.tempo}s    {item.descanso_individual}s\n")
            f.write("----------------------------------------\n\n")
            f.write("DESCANSO:\n")
            f.write(f"Entre rounds: {desc_round}s\n")
            f.write("========================================\n")

    @staticmethod
    def exportar_json(nome, rounds, desc_round, itens, path):
        dados = {
            "academia": "Soldier Academia",
            "treino": nome,
            "configuracoes": {"rounds": rounds, "descanso_rounds_segundos": desc_round},
            "exercicios": [
                {"ordem": i+1, "nome": it.nome, "tempo_segundos": it.tempo, "descanso_apos_segundos": it.descanso_individual}
                for i, it in enumerate(itens)
            ]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    @staticmethod
    def exportar_pdf(nome, rounds, desc_round, itens, path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "SOLDIER ACADEMIA", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "PLANEJAMENTO DE CIRCUITO FUNCIONAL", ln=True, align="C")
        pdf.ln(10)
        
        _, _, total = calcular_totais_circuito(itens, rounds, desc_round)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"TREINO: {nome.upper()}", ln=True)
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, f"ROUNDS: {rounds}  |  TEMPO ESTIMADO: {formatar_tempo(total)}", ln=True)
        pdf.cell(0, 8, f"DESCANSO ENTRE ROUNDS: {desc_round}s", ln=True)
        pdf.ln(5)
        
        # Tabela
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(15, 10, "#", border=1, fill=True, align="C")
        pdf.cell(100, 10, "Exercício", border=1, fill=True)
        pdf.cell(35, 10, "Tempo", border=1, fill=True, align="C")
        pdf.cell(40, 10, "Descanso (Após)", border=1, fill=True, align="C")
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 11)
        for i, item in enumerate(itens, 1):
            pdf.cell(15, 10, f"{i:02d}", border=1, align="C")
            pdf.cell(100, 10, item.nome, border=1)
            pdf.cell(35, 10, f"{item.tempo}s", border=1, align="C")
            pdf.cell(40, 10, f"{item.descanso_individual}s", border=1, align="C")
            pdf.ln()
            
        pdf.output(path)