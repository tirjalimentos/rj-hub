"""
Rotas HTTP de Especialistas.
Responsável apenas por receber a requisição e delegar ao service —
nenhuma regra de negócio deve viver aqui.

Exige login: a partir do sistema de permissões por grupo, o que essa
rota devolve depende de quem está perguntando, então não dá mais pra
responder sem saber quem é o usuário (ver services/permissoes_service.py).
"""

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_current_user
from models.auth import UsuarioAutenticado
from models.especialista import Especialista
from services.especialistas_service import buscar_especialista, listar_especialistas
from services.permissoes_service import especialistas_visiveis_para

router = APIRouter(prefix="/especialistas", tags=["especialistas"])


@router.get("", response_model=list[Especialista])
def get_especialistas(usuario: UsuarioAutenticado = Depends(get_current_user)):
    visiveis = set(especialistas_visiveis_para(usuario.email))
    return [e for e in listar_especialistas() if e.id in visiveis]


@router.get("/{especialista_id}", response_model=Especialista)
def get_especialista(
    especialista_id: str, usuario: UsuarioAutenticado = Depends(get_current_user)
):
    # Checa a permissão ANTES de buscar o especialista: se a pessoa não
    # tem acesso, a resposta é a mesma de "não existe" (404) — não
    # revela nem que o especialista existe, evita vazar informação
    # sobre o que tem no sistema pra quem não deveria ver.
    if especialista_id not in especialistas_visiveis_para(usuario.email):
        raise HTTPException(status_code=404, detail="Especialista não encontrado")

    especialista = buscar_especialista(especialista_id)
    if especialista is None:
        raise HTTPException(status_code=404, detail="Especialista não encontrado")
    return especialista
