"""
Script de seed — RJ HUB (projeto principal).

Modelo "Especialista Único" validado na variante de teste: começa
com 1 especialista genérico/institucional ("Especialista RJ") em vez
dos 12 departamentais, mas já com toda a infraestrutura de grupos de
acesso (RBAC) e painel de Super-Admin prontos — assim, adicionar
novos especialistas mais pra frente é só questão de conteúdo, sem
mudar tabela, service ou rota nenhuma.

Uso:
    cd backend
    python -m db.seed

Rodar de novo é seguro: cada recurso só insere o que ainda não
existe no banco (checa pelo id), então não duplica linhas.
"""

from db.database import Base, SessionLocal, engine
from db.models_db import (
    AdministradorDB,
    CategoriaDocumentoDB,
    ConversaDB,
    ConversaFavoritaDB,
    DashboardBarDB,
    DashboardStatDB,
    DocumentoConhecimentoDB,
    DocumentoDB,
    EspecialistaDB,
    GrupoDB,
    GrupoEspecialistaDB,
    UsuarioGrupoDB,
    WorkspaceDB,
    WorkspaceMembroDB,
)

_ESPECIALISTAS_SEED = [
    dict(
        id="especialista-rj",
        nome="Especialista RJ",
        icone="🏢",
        desc="Assistente geral da RJ Alimentos — dúvidas institucionais, processos e informações gerais da empresa.",
        docs=2,
        proc=2,
        atualizado="agora",
        favorito=True,
        status="ok",
    ),
]

_WORKSPACES_SEED = [
    dict(id="geral", nome="Geral", icone="🏢", membros=["especialista-rj"]),
]

# Grupos de acesso — cada grupo libera um ou mais especialistas para
# quem pertence a ele. Independente do Workspace (ver nota em
# models_db.py). Por enquanto só existe "geral", liberando o único
# especialista ativo; novos grupos entram conforme novos
# especialistas forem adicionados, sem precisar mudar nenhum código.
_GRUPOS_SEED = [
    dict(id="geral", nome="Geral", especialistas=["especialista-rj"]),
]

# Quem pertence a quais grupos. Ajuste/expanda esta lista conforme
# a empresa for integrando mais pessoas ao piloto.
_USUARIO_GRUPOS_SEED = [
    dict(email="pedro.santos@rjalimentos.com.br", grupos=["geral"]),
    dict(email="bruno.santos@rjalimentos.com.br", grupos=["geral"]),
]

_ADMINISTRADORES_SEED = [
    "pedro.santos@rjalimentos.com.br",
]

# Biblioteca — mínima, só pra tela não ficar vazia.
_CATEGORIAS_SEED = [
    dict(icon="🏢", nome="Institucional", qtd="0 documentos"),
    dict(icon="📜", nome="Políticas Gerais", qtd="0 documentos"),
]

_DOCUMENTOS_RECENTES_SEED = []

# Conversas — vazio de propósito: começa sem histórico simulado, só
# o que for gerado de verdade pelo uso real.
_CONVERSAS_SEED = []
_CONVERSAS_FAVORITAS_SEED = []

_DASHBOARD_STATS_SEED = [
    dict(icon="🤖", bg="#FBEFEF", num="1", lab="Especialista ativo"),
    dict(icon="📄", bg="var(--gold-soft)", num="2", lab="Documentos indexados"),
    dict(icon="💬", bg="#EAF1FB", num="0", lab="Conversas nesta semana"),
]

_DASHBOARD_BARS_SEED = [
    dict(nome="Especialista RJ", val=0),
]

# Base de conhecimento — documentos reais da RJ Alimentos. Continue
# colando novos POPs/manuais aqui, com o especialista_id certo.
_DOCUMENTOS_CONHECIMENTO_SEED = [
    dict(
        especialista_id="especialista-rj",
        titulo="Guia Prático — Como abrir formulários RAC (GLPI)",
        conteudo=(
            "Este guia prático foi elaborado para ajudar a abrir formulários RAC "
            "no GLPI 11.0.2.\n\n"
            "1- Com o GLPI aberto e logado com seu usuário, clique no ícone do "
            "seu perfil, localizado no canto superior direito da tela.\n\n"
            "2- Após clicar no ícone, será aberta uma aba de configuração de "
            "perfis. Nessa área, é possível visualizar todos os perfis aos "
            "quais o usuário possui acesso. Localize e selecione o perfil "
            "\"RAC\". Após selecionar, basta fechar a aba de configurações "
            "para retornar ao fluxo normal de uso.\n\n"
            "3- Em seguida, acesse a janela \"Assistência\" e selecione a "
            "opção \"Catálogo de Serviços\". É nessa área que se visualiza e "
            "gerencia as categorias e serviços disponíveis para abertura de "
            "chamados, garantindo que o perfil esteja configurado "
            "corretamente para acessar o catálogo desejado.\n\n"
            "4- Com o Catálogo de Serviços aberto, localize e selecione o "
            "formulário \"RAC\" (formulário destinado ao registro de "
            "reclamações relacionadas a pedidos, produtos, entregas ou "
            "divergências comerciais). Preencha todas as informações "
            "solicitadas no formulário e, após revisar os dados inseridos, "
            "clique em \"Enviar\" para registrar a solicitação."
        ),
    ),
    dict(
        especialista_id="especialista-rj",
        titulo="Cadastro de RCA — Rotina 517 (WinThor)",
        conteudo=(
            "Todo cadastro de RCA é feito na rotina 517 do WinThor "
            "(Distribuição e Varejo — Linha WinThor).\n\n"
            "1- Para realizar o cadastro do RCA, primeiro abrir a rotina 517 "
            "no WinThor.\n\n"
            "2- Após abrir a rotina, ir na aba \"Cadastro\" e clicar em "
            "\"Incluir\".\n\n"
            "3- Com a janela de inclusão aberta, inserir as informações "
            "básicas do usuário nos campos destacados (nome, data de "
            "nascimento, supervisor, filial, tipo pessoa, CPF, CI, etc.).\n"
            "3.1- O campo \"Supervisor\" pode ser preenchido diretamente com "
            "o código do supervisor padrão (ex: 8 - EQUIPE FOOD SERVICE).\n"
            "3.2- Alternativamente, clicar no botão \"...\" ao lado do campo, "
            "clicar em \"Pesquisar\", localizar o supervisor desejado na "
            "lista (ex: 8 - EQUIPE FOOD SERVICE, 1 - EXECUTIVOS DE VENDAS, "
            "2 - EQUIPE VAREJO, entre outros) e confirmar.\n\n"
            "4- Após preencher as informações básicas, ir na aba \"Endereço\" "
            "e preencher os campos de endereço do colaborador (endereço, "
            "bairro, cidade, estado, CEP, e-mail, telefone).\n"
            "4.1- No campo \"E-mail\" preencher com o e-mail corporativo do "
            "colaborador (formato nome.sobrenome@rjalimentos.com.br).\n\n"
            "5- Na aba \"Vendas/Comissão\", selecionar: Tipo de venda "
            "\"I - Interna\"; marcar a opção \"Usa Débito/Crédito RCA\"; e "
            "Tipo de comissão \"Ambas\" (Liquidez e Venda).\n\n"
            "6- Em seguida, ir na aba \"Financeiro\" e clicar em "
            "\"Confirmar\" para gravar o registro.\n\n"
            "7- Após preencher todas as abas e confirmar o cadastro, "
            "retornar à tela inicial da rotina 517: clicar em \"Pesquisar\", "
            "escolher a opção \"RCA\" para organizar em ordem alfabética, e "
            "localizar, selecionar e abrir o RCA recém-cadastrado para "
            "conferir o código gerado.\n\n"
            "8- Em seguida, ir na aba \"Numeradores\": copiar o código do "
            "campo \"Próximo N° Pedido\", apagar o conteúdo após a vírgula, "
            "e colar o código resultante no campo \"Prox. N° Ped. Força "
            "Venda\".\n\n"
            "9- Após finalizar todos os processos, clicar em \"Confirmar\" "
            "para concluir o cadastro do RCA.\n\n"
            "Referência: TOTVS Central de Atendimento — WINT: Como realizar "
            "a importação de um arquivo com preços de venda pela rotina 201."
        ),
    ),
]


def _seed_especialistas(db) -> int:
    criados = 0
    for dados in _ESPECIALISTAS_SEED:
        if db.get(EspecialistaDB, dados["id"]):
            continue
        db.add(EspecialistaDB(**dados))
        criados += 1
    db.commit()
    return criados


def _seed_workspaces(db) -> int:
    criados = 0
    for dados in _WORKSPACES_SEED:
        if db.get(WorkspaceDB, dados["id"]):
            continue
        db.add(WorkspaceDB(id=dados["id"], nome=dados["nome"], icone=dados["icone"]))
        for ordem, especialista_id in enumerate(dados["membros"]):
            db.add(WorkspaceMembroDB(
                workspace_id=dados["id"],
                especialista_id=especialista_id,
                ordem=ordem,
            ))
        criados += 1
    db.commit()
    return criados


def _seed_grupos(db) -> int:
    criados = 0
    for dados in _GRUPOS_SEED:
        if db.get(GrupoDB, dados["id"]):
            continue
        db.add(GrupoDB(id=dados["id"], nome=dados["nome"]))
        for especialista_id in dados["especialistas"]:
            db.add(GrupoEspecialistaDB(
                grupo_id=dados["id"],
                especialista_id=especialista_id,
            ))
        criados += 1
    db.commit()
    return criados


def _seed_usuario_grupos(db) -> int:
    criados = 0
    for dados in _USUARIO_GRUPOS_SEED:
        for grupo_id in dados["grupos"]:
            existe = (
                db.query(UsuarioGrupoDB)
                .filter_by(usuario_email=dados["email"], grupo_id=grupo_id)
                .first()
            )
            if existe:
                continue
            db.add(UsuarioGrupoDB(usuario_email=dados["email"], grupo_id=grupo_id))
            criados += 1
    db.commit()
    return criados


def _seed_administradores(db) -> int:
    criados = 0
    for email in _ADMINISTRADORES_SEED:
        if db.get(AdministradorDB, email):
            continue
        db.add(AdministradorDB(usuario_email=email))
        criados += 1
    db.commit()
    return criados


def _seed_biblioteca(db) -> int:
    criados = 0
    for dados in _CATEGORIAS_SEED:
        existe = db.query(CategoriaDocumentoDB).filter_by(nome=dados["nome"]).first()
        if existe:
            continue
        db.add(CategoriaDocumentoDB(**dados))
        criados += 1
    for dados in _DOCUMENTOS_RECENTES_SEED:
        existe = db.query(DocumentoDB).filter_by(nome=dados["nome"]).first()
        if existe:
            continue
        db.add(DocumentoDB(**dados))
        criados += 1
    db.commit()
    return criados


def _seed_conversas(db) -> int:
    criados = 0
    for dados in _CONVERSAS_SEED:
        existe = db.query(ConversaDB).filter_by(especialista_id=dados["especialista_id"]).first()
        if existe:
            continue
        db.add(ConversaDB(**dados))
        criados += 1
    for label in _CONVERSAS_FAVORITAS_SEED:
        existe = db.query(ConversaFavoritaDB).filter_by(label=label).first()
        if existe:
            continue
        db.add(ConversaFavoritaDB(label=label))
        criados += 1
    db.commit()
    return criados


def _seed_dashboard(db) -> int:
    criados = 0
    for dados in _DASHBOARD_STATS_SEED:
        existe = db.query(DashboardStatDB).filter_by(lab=dados["lab"]).first()
        if existe:
            continue
        db.add(DashboardStatDB(**dados))
        criados += 1
    for dados in _DASHBOARD_BARS_SEED:
        existe = db.query(DashboardBarDB).filter_by(nome=dados["nome"]).first()
        if existe:
            continue
        db.add(DashboardBarDB(**dados))
        criados += 1
    db.commit()
    return criados


def _seed_conhecimento(db) -> int:
    criados = 0
    for dados in _DOCUMENTOS_CONHECIMENTO_SEED:
        existe = (
            db.query(DocumentoConhecimentoDB)
            .filter_by(especialista_id=dados["especialista_id"], titulo=dados["titulo"])
            .first()
        )
        if existe:
            continue
        db.add(DocumentoConhecimentoDB(**dados))
        criados += 1
    db.commit()
    return criados


def seed():
    # Cria as tabelas que ainda não existem (não apaga nada existente).
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        n_especialistas = _seed_especialistas(db)
        n_workspaces = _seed_workspaces(db)
        n_grupos = _seed_grupos(db)
        n_usuario_grupos = _seed_usuario_grupos(db)
        n_administradores = _seed_administradores(db)
        n_biblioteca = _seed_biblioteca(db)
        n_conversas = _seed_conversas(db)
        n_dashboard = _seed_dashboard(db)
        n_conhecimento = _seed_conhecimento(db)

        print(f"✅ Especialistas: {n_especialistas} inserido(s).")
        print(f"✅ Workspaces: {n_workspaces} inserido(s).")
        print(f"✅ Grupos: {n_grupos} inserido(s).")
        print(f"✅ Usuário-Grupos: {n_usuario_grupos} inserido(s).")
        print(f"✅ Administradores: {n_administradores} inserido(s).")
        print(f"✅ Biblioteca (categorias + documentos): {n_biblioteca} inserido(s).")
        print(f"✅ Conversas (+ favoritas): {n_conversas} inserido(s).")
        print(f"✅ Dashboard (stats + bars): {n_dashboard} inserido(s).")
        print(f"✅ Base de conhecimento: {n_conhecimento} inserido(s).")
        totais = [
            n_especialistas, n_workspaces, n_grupos, n_usuario_grupos, n_administradores,
            n_biblioteca, n_conversas, n_dashboard, n_conhecimento,
        ]
        if sum(totais) == 0:
            print("ℹ️  Nenhum novo registro — o banco já estava populado.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
