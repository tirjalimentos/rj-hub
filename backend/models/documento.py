"""
Modelos de dados da Biblioteca de Documentos.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class CategoriaDocumento(BaseModel):
    icon: str
    nome: str
    qtd: str  # texto pronto para exibição, ex: "42 documentos"


class Documento(BaseModel):
    icon: str
    nome: str
    area: str
    tag: str
    quando: str  # texto pronto para exibição, ex: "Atualizado há 2 dias"
