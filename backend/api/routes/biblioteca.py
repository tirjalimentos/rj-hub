"""
Rotas HTTP da Biblioteca de Documentos.
Responsável apenas por receber a requisição e delegar ao service —
nenhuma regra de negócio deve viver aqui.

Protegida por get_current_admin: a Biblioteca foi unificada com a
Base de Conhecimento (mesmos documentos que alimentam o chat dos
especialistas, ver services/biblioteca_service.py) — o conteúdo pode
ser sensível, então só Super-Admin acessa, mesma proteção usada nas
rotas /admin/*.
"""

from fastapi import APIRouter, Depends

from api.deps_admin import get_current_admin
from models.documento import CategoriaDocumento, Documento
from services.biblioteca_service import listar_categorias, listar_documentos_recentes

router = APIRouter(
    prefix="/biblioteca",
    tags=["biblioteca"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/categorias", response_model=list[CategoriaDocumento])
def get_categorias():
    return listar_categorias()


@router.get("/recentes", response_model=list[Documento])
def get_documentos_recentes():
    return listar_documentos_recentes()
