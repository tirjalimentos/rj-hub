# RJ HUB — Contexto do Projeto

Leia este arquivo antes de qualquer alteração. Ele resume as regras e o
estado do projeto; o detalhamento completo (decisões, padrões, histórico
de bugs, deploy) está em **`CONTEXTO_PROJETO.md`** — consulte a seção
correspondente antes de mexer em uma área. Em caso de dúvida sobre uma
decisão, preserve a arquitetura atual em vez de assumir.

## O que é o projeto

O RJ HUB é uma plataforma corporativa de Inteligência Artificial para a
RJ Alimentos. Não é um "ChatGPT genérico": é um HUB onde o usuário
conversa com **especialistas da empresa** (Comercial, Fiscal, Financeiro,
RH, PCP, Compras, Estoque, TI, e outros no futuro). Cada especialista
tem conhecimento, documentos, contexto e histórico próprios. O usuário
escolhe um workspace, escolhe um especialista, e conversa apenas com ele.

O projeto foi recomeçado do zero para eliminar a dívida técnica de uma
versão anterior (HTML e JS editados em pastas diferentes, protótipos
misturados com código oficial, módulos vazios). **O visual (identidade
vinho `#AB0F15` / dourado `#E7C311`, sidebar escura, cards de
especialistas) foi reaproveitado** — só a base técnica foi reconstruída.

## Regras de arquitetura (sempre respeitar)

1. Nunca criar arquivos gigantes. Cada módulo tem uma responsabilidade.
2. Nunca misturar código de protótipo/teste com o oficial. Prototipar em
   pasta separada (ex: `sandbox/`) com nome que deixe isso explícito.
3. Nunca colocar dados dentro da interface (HTML) nem regras de negócio
   dentro de `app.js` ou das rotas do backend.
4. Sempre modularizar — se um arquivo cresce demais ou faz mais de uma
   coisa, divida.
5. Antes de mudar uma decisão arquitetural, justifique por escrito.
6. Entre duas soluções equivalentes, escolha a mais simples.
7. Evite dependências desnecessárias entre módulos.
8. O contrato entre front e back é a API — nenhum lado depende de
   detalhes internos do outro.
9. Todo endpoint novo segue a camada `models/` (Pydantic) → `services/`
   (regra de negócio) → `api/routes/` (só recebe e chama o service).
10. Todo dado novo do frontend segue o padrão **"mock com fallback"**
    (abaixo). Exceção deliberada: o chat não simula resposta se a IA
    falhar — mostra erro.
11. Controle de acesso **nega por padrão**; liberação é sempre explícita.
12. Segredos só no `.env` (nunca hardcoded nem versionados). Segredo
    exposto por engano deve ser **regenerado**, não só movido.

## Estrutura do projeto

```
RJ_HUB/
├── CLAUDE.md                 ← este arquivo (resumo)
├── CONTEXTO_PROJETO.md       ← contexto completo e detalhado
├── frontend/                 servido pelo próprio backend (StaticFiles)
│   ├── index.html            casca: sidebar + topbar + todas as views + view de chat
│   ├── css/
│   │   ├── style.css          identidade visual, componentes, temas Padrão/Escuro
│   │   └── chat-view.css      layout da view de chat e Markdown das respostas
│   └── js/
│       ├── data.js            dados + fallback mock (sem lógica)
│       ├── ui.js              sidebar, navegação, menu mobile, tema
│       ├── workspace.js       seletor de workspace, saudação, home, dados do usuário logado
│       ├── especialistas.js   listagem, busca, favoritos
│       ├── biblioteca.js      biblioteca de documentos (só Super-Admin)
│       ├── conversas.js       histórico de conversas
│       ├── dashboard.js       indicadores e gráficos
│       ├── chat.js            view de chat integrada (IA real, Markdown via marked + DOMPurify)
│       ├── config.js          configurações (tema, idioma, workspace padrão)
│       ├── admin.js           painel de Super-Admin (Grupos, Usuários, Base de Conhecimento, Especialistas, Administradores)
│       ├── auth.js            login Google, token JWT (getToken, estaLogado)
│       ├── api.js             TODAS as chamadas HTTP; API = "" (caminho relativo)
│       └── app.js             só inicialização — orquestra init()/render() dos módulos
└── backend/
    ├── main.py                cria o app, CORS, sessão, registra rotas, create_all,
    │                          garante INITIAL_ADMIN_EMAIL, serve o frontend (mount "/" sempre por último)
    ├── core/config.py         configurações e leitura do .env (caminho absoluto)
    ├── db/                    SQLAlchemy + SQLite (rjhub.db, não versionado)
    │   ├── database.py         engine, SessionLocal, Base, get_db()
    │   ├── models_db.py        tabelas (classes com sufixo DB)
    │   └── seed.py             dados iniciais (idempotente): python -m db.seed
    ├── models/                schemas Pydantic — só estrutura de dados
    ├── services/              regra de negócio (consultam o banco)
    │   ├── ia_service.py       motor de IA (Anthropic, modelo em ANTHROPIC_MODEL)
    │   ├── conhecimento_service.py  base de conhecimento (busca por palavras-chave, sem embeddings)
    │   ├── extracao_texto.py   texto de PDF/.docx enviados no painel
    │   ├── auth_service.py     OAuth Google + JWT próprio
    │   ├── permissoes_service.py  RBAC (quem vê qual especialista)
    │   ├── admin_service.py    CRUD do painel de Super-Admin
    │   └── especialistas / workspaces / biblioteca / conversas / dashboard
    ├── api/
    │   ├── deps.py             get_current_user (valida JWT)
    │   ├── deps_admin.py       get_current_admin (exige Super-Admin)
    │   └── routes/             endpoints HTTP; só recebem e chamam o service
    └── scripts/
        └── migrar_schema_v2.py  migração pontual de schema (já aplicada)
```

## Padrões que mais causam bug se ignorados

- **Mock com fallback (frontend):** cada dado tem `XXX_MOCK` (fixo) e
  `XXX` (mutável, o único lido pela interface). `api.js` retorna `null` em
  erro; `carregarDadosIniciais()` em `app.js` sobrescreve com a API ou
  mantém o mock com aviso `⚠️ API indisponível`. Se uma rota passar a
  exigir login, a função em `api.js` precisa usar `_authHeaders()` — senão
  cai no mock silenciosamente.
- **Duas listas de especialistas no admin:** `SPECIALISTS` é filtrada por
  RBAC (experiência do usuário); `ADMIN_ESPECIALISTAS_TODOS` é sem filtro
  (só dentro do painel de Super-Admin). Telas do painel usam sempre a
  segunda.
- **Super-Admin ≠ Grupo:** ser admin não libera nenhum especialista para
  conversar; isso depende de o e-mail estar em um grupo (aba Usuários).
- **Chat síncrono:** `post_chat` é `def` (roda em threadpool). Não tornar
  `async def` sem trocar o client da Anthropic para assíncrono.
- **Schema do banco:** `create_all()` só cria tabelas que faltam; alterar
  tabela existente exige script de migração em `backend/scripts/`.
- **CSS:** fundo de card/painel = `var(--surface)`, nunca `var(--white)`
  (quebra o tema escuro). Reaproveitar `.hero`, `.card`, `.grid`,
  `.toolbar`, `.kpi-grid`, `.admin-*` em vez de criar padrão visual novo.

## Rotas e proteção

- Públicas: `/health`, `/auth/login`, `/auth/callback`, arquivos estáticos.
- Login: `/auth/me`, `/especialistas`, `/workspaces`, `/conversas`
  (sempre só do próprio usuário), `/dashboard` (admin vê agregado; usuário
  comum só o próprio uso), `/chat` (também checa RBAC; 403 se sem acesso).
- Login + Super-Admin: `/biblioteca/*` e `/admin/*`.

## Como rodar localmente

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m db.seed              # cria/atualiza o banco (idempotente)
uvicorn main:app --reload
```

- Precisa de `backend/.env` (modelo em `.env.example`): `ANTHROPIC_API_KEY`,
  `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET_KEY`,
  `SESSION_SECRET_KEY` (≥ 32 bytes), `FRONTEND_URL=http://localhost:8000`,
  `INITIAL_ADMIN_EMAIL` (opcional: `GOOGLE_ALLOWED_DOMAIN`).
- App completo (frontend + API) em `http://localhost:8000/`; docs em
  `/docs`. **Não rodar servidor separado para o frontend.**
- Acessar sempre pelo mesmo host cadastrado no Google Console
  (`localhost` ≠ `127.0.0.1`) e igual ao `FRONTEND_URL`.
- Validar sintaxe antes de entregar: `node --check arquivo.js` /
  `python -m py_compile arquivo.py`.

## Estado atual

Implementado e funcionando:
- Todas as views (Início, Especialistas, Biblioteca, Conversas, Dashboard,
  Configurações, Super-Admin) e a view de chat integrada.
- Backend com banco SQLite real; todos os recursos do frontend já
  consomem a API (com fallback mock).
- Login SSO Google Workspace + JWT próprio.
- RBAC por grupos + painel de Super-Admin completo (incluindo upload de
  PDF/.docx, exportar documentos em `.zip`, excluir especialista com
  bloqueio por dependência).
- Chat com IA real (Anthropic) usando a base de conhecimento do
  especialista, respostas em Markdown.
- Conversas gravadas de verdade; Dashboard calculado a partir do uso real.
- Tema Padrão / Escuro / Sistema (escuro ainda aguardando ajuste visual).
- Deploy de teste validado na Render (plano Free). Produção decidida:
  VPS Linux na Locaweb (ainda não contratada/configurada).

## Próximos passos (em ordem sugerida)

1. Produção na Locaweb VPS (Ubuntu, Nginx + HTTPS, systemd, firewall,
   backup do `rjhub.db`, domínio, redirect URI no Google, chaves novas).
2. Antes de abrir para usuários: SQLite em modo WAL + `busy_timeout` em
   `db/database.py` (**lembrar a pessoa disso na migração**), setar
   `GOOGLE_ALLOWED_DOMAIN`, recriar especialistas/documentos no banco novo.
3. Perfis Admin / Supervisor / Usuário (definir escopo do Supervisor).
4. Configurações da plataforma editáveis pelo Super-Admin.
5. Integração com DataLake / Power BI via *tool use* (sem prazo).
6. Definir os próximos especialistas reais (e vinculá-los a grupos).
7. Polimento de UX: tema escuro, busca real na topbar, toasts no lugar de
   `alert()`, remover ou exibir `CONVERSATIONS_FAVORITAS`.
8. PostgreSQL só se houver múltiplas instâncias ou necessidade do DataLake.

Não pule etapas — cada uma deve seguir os padrões acima e os detalhados
no `CONTEXTO_PROJETO.md`.

## Ambiente de trabalho

- Repositório oficial: `C:\Users\plosantos\Documents\RJ_HUB`, editado
  diretamente pelo Claude Code. Commit/push só quando a pessoa pedir.
- Para promover um Super-Admin: aba Administradores do painel ou
  `INITIAL_ADMIN_EMAIL` no `.env` (não existe script `promover_admin.py`).
