"""
Rotas HTTP de Conversas.
Responsável apenas por receber a requisição e delegar ao service —
nenhuma regra de negócio deve viver aqui.

Exige login: conversa é dado pessoal (o histórico de chat de cada
um), nunca deve ser possível ver o de outra pessoa — listar_conversas()
já filtra pelo e-mail de quem está logado, ver services/conversas_service.py.
"""

from fastapi import APIRouter, Depends, Query

from api.deps import get_current_user
from models.auth import UsuarioAutenticado
from models.conversa import Conversa
from services.conversas_service import listar_conversas, listar_conversas_favoritas

router = APIRouter(prefix="/conversas", tags=["conversas"])


@router.get("", response_model=list[Conversa])
def get_conversas(
    limit: int | None = Query(default=None, ge=1),
    usuario: UsuarioAutenticado = Depends(get_current_user),
):
    """
    `limit` é opcional e existe pra sidebar da Parte B, que só precisa
    das N conversas mais recentes (não a lista inteira que a view
    "Conversas" mostra). listar_conversas() já devolve ordenado do
    mais recente pro mais antigo, então o corte é só um slice — sem
    duplicar a lógica de ordenação aqui.
    """
    conversas = listar_conversas(usuario.email)
    if limit is not None:
        return conversas[:limit]
    return conversas


@router.get("/favoritas", response_model=list[str])
def get_conversas_favoritas():
    return listar_conversas_favoritas()
