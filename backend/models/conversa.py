"""
Modelo de dados de Conversa.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class Conversa(BaseModel):
    icon: str
    nome: str
    id: str  # id do especialista relacionado
    preview: str
    quando: str
