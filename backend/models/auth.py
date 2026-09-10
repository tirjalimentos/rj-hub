"""
Modelo de dados do Usuário Autenticado.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class UsuarioAutenticado(BaseModel):
    email: str
    nome: str
    foto: str | None = None
