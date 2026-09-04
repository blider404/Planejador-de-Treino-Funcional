# utils/helpers.py
from typing import List
from database.models import ItemCircuito

def formatar_tempo(segundos: int) -> str:
    """Formata o tempo em h, min e s."""
    segundos = int(round(max(0, segundos)))
    m, s = divmod(segundos, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}min {s:02d}s"
    if m:
        return f"{m}min {s:02d}s"
    return f"{s}s"

def calcular_totais_circuito(itens: List[ItemCircuito], rounds: int, descanso_round: int):
    """Calcula o tempo de trabalho e descanso total de um circuito estruturado."""
    if not itens or rounds <= 0:
        return 0, 0, 0

    trabalho_por_round = sum(i.tempo for i in itens)
    # Considera o descanso individual ou assume 0 se for o último do round
    descanso_por_round = sum(i.descanso_individual for i in itens[:-1])
    
    tempo_trabalho_total = trabalho_por_round * rounds
    tempo_descanso_total = (descanso_por_round * rounds) + (descanso_round * max(0, rounds - 1))
    tempo_total = tempo_trabalho_total + tempo_descanso_total

    return tempo_trabalho_total, tempo_descanso_total, tempo_total