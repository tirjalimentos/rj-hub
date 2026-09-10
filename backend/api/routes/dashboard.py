"""
Rotas HTTP do Dashboard.
Responsável apenas por receber a requisição e chamar o service —
nenhuma regra de negócio deve viver aqui.

Exige login: o resultado depende de quem está perguntando (Super-Admin
vê o agregado de todos; usuário comum só o próprio uso) — ver
services/dashboard_service.py.
"""

from fastapi import APIRouter, Depends

from api.deps import get_current_user
from models.auth import UsuarioAutenticado
from models.dashboard import DashboardBar, DashboardStat
from services.admin_service import eh_administrador
from services.dashboard_service import listar_bars, listar_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=list[DashboardStat])
def get_stats(usuario: UsuarioAutenticado = Depends(get_current_user)):
    return listar_stats(usuario.email, eh_administrador(usuario.email))


@router.get("/bars", response_model=list[DashboardBar])
def get_bars(usuario: UsuarioAutenticado = Depends(get_current_user)):
    return listar_bars(usuario.email, eh_administrador(usuario.email))
