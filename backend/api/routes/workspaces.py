"""
Rotas HTTP de Workspaces.
Responsável apenas por receber a requisição e delegar ao service —
nenhuma regra de negócio deve viver aqui.

Exige login: assim como /especialistas, o campo `membros` devolvido
aqui é filtrado pelo que o usuário logado pode ver (ver
services/permissoes_service.py) — quem não tem acesso a um
especialista não vê o id dele nem listado dentro de um workspace.
"""

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_current_user
from models.auth import UsuarioAutenticado
from models.workspace import Workspace
from services.permissoes_service import especialistas_visiveis_para
from services.workspaces_service import buscar_workspace, listar_workspaces

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def _filtrar_membros(workspace: Workspace, visiveis: set[str]) -> Workspace:
    return workspace.model_copy(
        update={"membros": [m for m in workspace.membros if m in visiveis]}
    )


@router.get("", response_model=list[Workspace])
def get_workspaces(usuario: UsuarioAutenticado = Depends(get_current_user)):
    visiveis = set(especialistas_visiveis_para(usuario.email))
    filtrados = [_filtrar_membros(w, visiveis) for w in listar_workspaces()]
    # Um workspace sem nenhum membro visível pra essa pessoa não tem
    # razão de aparecer na navegação — fica "vazio" e some da lista.
    return [w for w in filtrados if w.membros]


@router.get("/{workspace_id}", response_model=Workspace)
def get_workspace(
    workspace_id: str, usuario: UsuarioAutenticado = Depends(get_current_user)
):
    workspace = buscar_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    visiveis = set(especialistas_visiveis_para(usuario.email))
    return _filtrar_membros(workspace, visiveis)
