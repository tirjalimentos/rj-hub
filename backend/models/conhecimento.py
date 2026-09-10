"""
Modelo de dados de um Documento da Base de Conhecimento.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class DocumentoConhecimento(BaseModel):
    id: int
    especialista_id: str
    titulo: str
    conteudo: str
