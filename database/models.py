# database/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Exercicio:
    id: Optional[int]
    nome: str
    grupo_muscular: str
    descricao: str
    video: str
    tempo_padrao: int
    tipo: str
    equipamento: str
    nivel: str
    padrao_movimento: str

@dataclass
class ItemCircuito:
    exercicio_id: int
    nome: str
    tempo: int
    descanso_individual: int
    grupo: str = ""
    tipo: str = ""
    nivel: str = ""