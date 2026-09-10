"""
Modelo de dados de um Workspace.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class Workspace(BaseModel):
    id: str
    nome: str
    icone: str
    membros: list[str]  # ids de especialistas que pertencem a este workspace
