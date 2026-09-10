"""
Schemas Pydantic usados pelas rotas de Super-Admin.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from pydantic import BaseModel


class GrupoCriar(BaseModel):
    id: str
    nome: str


class GrupoOut(BaseModel):
    id: str
    nome: str
    especialistas: list[str]


class GrupoEspecialistasAtualizar(BaseModel):
    especialista_ids: list[str]


class UsuarioOut(BaseModel):
    email: str
    grupos: list[str]


class UsuarioGruposAtualizar(BaseModel):
    grupos: list[str]


class AdministradorOut(BaseModel):
    email: str


class AdministradorCriar(BaseModel):
    email: str
