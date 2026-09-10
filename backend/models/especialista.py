"""
Modelo de dados de um Especialista.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class Especialista(BaseModel):
    id: str
    nome: str
    icone: str
    desc: str
    docs: int
    proc: int
    atualizado: str
    favorito: bool = False
    status: str = "ok"  # "ok" | "review"


class EspecialistaCriar(BaseModel):
    """Usado só pelo painel de Super-Admin (POST /admin/especialistas)."""
    id: str
    nome: str
    icone: str
    desc: str
