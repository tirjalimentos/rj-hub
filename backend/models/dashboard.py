"""
Modelos de dados do Dashboard.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class DashboardStat(BaseModel):
    icon: str
    bg: str
    num: str
    lab: str


class DashboardBar(BaseModel):
    nome: str
    val: int
