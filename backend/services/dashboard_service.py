"""
Regras de negócio relacionadas ao Dashboard.

Dado real agora, calculado em cima de conversas_service (conversas
de verdade) e das tabelas já existentes — não mais linhas semeadas
manualmente (DashboardStatDB/DashboardBarDB continuam existindo no
banco só como resquício, não são mais lidas aqui).

Escopo por permissão: Super-Admin vê o agregado de TODOS os usuários;
usuário comum só vê o próprio uso. Quem decide isso é a rota
(api/routes/dashboard.py), que passa `eh_admin` pra cá.
"""

from db.database import SessionLocal
from db.models_db import DocumentoConhecimentoDB, EspecialistaDB
from models.dashboard import DashboardBar, DashboardStat
from services.conversas_service import contar_conversas_na_semana, contar_mensagens_por_especialista
from services.permissoes_service import especialistas_visiveis_para


def listar_stats(usuario_email: str, eh_admin: bool) -> list[DashboardStat]:
    db = SessionLocal()
    try:
        if eh_admin:
            n_especialistas = db.query(EspecialistaDB).count()
            n_documentos = db.query(DocumentoConhecimentoDB).count()
        else:
            visiveis = especialistas_visiveis_para(usuario_email)
            n_especialistas = len(visiveis)
            n_documentos = (
                db.query(DocumentoConhecimentoDB)
                .filter(DocumentoConhecimentoDB.especialista_id.in_(visiveis))
                .count()
                if visiveis
                else 0
            )
    finally:
        db.close()

    n_conversas_semana = contar_conversas_na_semana(None if eh_admin else usuario_email)

    return [
        DashboardStat(
            icon="🤖", bg="#FBEFEF",
            num=str(n_especialistas),
            lab="Especialistas ativos" if eh_admin else "Especialistas disponíveis",
        ),
        DashboardStat(
            icon="📄", bg="var(--gold-soft)",
            num=str(n_documentos),
            lab="Documentos indexados",
        ),
        DashboardStat(
            icon="💬", bg="#EAF1FB",
            num=str(n_conversas_semana),
            lab="Conversas nesta semana" if eh_admin else "Suas conversas nesta semana",
        ),
    ]


def listar_bars(usuario_email: str, eh_admin: bool) -> list[DashboardBar]:
    contagem = contar_mensagens_por_especialista(None if eh_admin else usuario_email)
    if not contagem:
        return []

    db = SessionLocal()
    try:
        especialistas = {e.id: e for e in db.query(EspecialistaDB).all()}
    finally:
        db.close()

    maximo = max(contagem.values())
    bars = []
    for especialista_id, total in sorted(contagem.items(), key=lambda item: item[1], reverse=True):
        nome = especialistas[especialista_id].nome if especialista_id in especialistas else especialista_id
        # Normalizado pro maior valor virar 100% — o frontend usa
        # `val` direto como altura da barra em %, então precisa vir
        # já numa escala 0-100, não na contagem bruta de mensagens.
        val = round((total / maximo) * 100) if maximo else 0
        bars.append(DashboardBar(nome=nome, val=val))
    return bars
