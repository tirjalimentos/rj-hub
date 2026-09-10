# RJ HUB — Contexto Completo do Projeto

> Este documento existe para ser colado no início de uma nova conversa com
> uma IA (Claude ou outra), para que ela entenda o projeto inteiro sem
> precisar reexplicar nada do zero. Leia tudo antes de sugerir qualquer
> mudança, e trate as regras da seção 3 como inegociáveis.

---

## 1. O que é o projeto

O **RJ HUB** é uma plataforma corporativa de Inteligência Artificial para a
**RJ Alimentos**. Não é um "ChatGPT genérico": é um HUB onde o usuário
conversa com **especialistas da empresa** — cada um representando uma área
ou departamento.

Cada especialista tem, conceitualmente:
- conhecimento próprio (documentos reais indexados)
- contexto próprio (system prompt dedicado)
- histórico próprio
- controle de quem pode acessá-lo (RBAC — ver seção 5.3)

O fluxo de uso é:

```
usuário entra (login com Google Workspace corporativo)
  ↓
vê a casca completa: sidebar fixa (navegação + histórico de conversas) +
topbar com seletor de Workspace persistente + área central
  ↓
vê só os Especialistas que seu grupo de acesso libera
  ↓
conversa com ele (view de chat integrada na mesma casca, não modal — com IA real por trás)
  ↓
consulta documentos (Biblioteca)
  ↓
possui histórico (Conversas)
  ↓
possui dashboard (indicadores)
  ↓
favorita especialistas direto no card (sem seção separada)
  ↓
(Super-Admin, se aplicável) gerencia grupos, usuários e base de conhecimento pelo próprio portal
```

**Estado atual:** tudo isso já existe funcionalmente, com backend real
(FastAPI + SQLite), IA real (Anthropic/Claude), autenticação real (SSO
Google), controle de acesso real (RBAC) e **interface própria para o
painel de Super-Admin**. Não há mais nenhum dado inventado — o que resta
de "mock" é só o fallback de segurança (seção 5), não a fonte primária de
dado. O redesign visual (Parte B, ver seção 8) também está concluído: sai
o modelo antigo de cards + modal de chat por cima; entra a casca definitiva
descrita acima, com a identidade vinho/dourado aplicada de verdade em
todas as views.

**Decisão de escopo (importante, difere do plano original):** a ideia
original previa lançar já com 12 especialistas departamentais (Comercial,
Fiscal, Financeiro, RH, PCP, Compras, Estoque, TI, Diretoria, Produção,
Logística, Pricing, Contabilidade). O lançamento **não** vai sair assim.
Hoje existe só **1 especialista institucional/geral** ("Especialista RJ"),
modelo validado numa variante de teste isolada antes de entrar aqui (ver
seção 2). A arquitetura já suporta múltiplos especialistas com controle de
acesso por grupo — adicionar o próximo é questão de conteúdo, não de
código. Quantos/quais especialistas entram no lançamento oficial ainda não
foi decidido.

---

## 2. Histórico — por que esse projeto foi recomeçado do zero

Existia uma versão anterior, feita com outra ferramenta de IA (ChatGPT).
Ela acumulou uma dívida técnica grave:

- HTML sendo editado em uma pasta (`workspace/landing_v2/`) enquanto o
  JavaScript correspondente era criado em outra (`app/frontend/js/`).
- Um protótipo de teste (`landing_v2`) acabou virando, na prática, o
  "frontend mais atualizado", enquanto o frontend "oficial" ficava
  desatualizado e desconectado.
- Módulos JavaScript pensados para serem modulares (`data.js`, `ui.js`,
  `workspace.js` etc.) existiam como arquivos vazios (0 bytes) ou como
  stubs truncados com `...` no lugar de dados reais.
- Toda a lógica de verdade (renderização de views, chat, favoritos,
  dashboard) estava concentrada em um único `<script>` gigante dentro de
  um HTML monolítico — o oposto do que a arquitetura pretendida exigia.

**Decisão tomada:** apagar tudo e recomeçar do zero, mas **reaproveitando o
visual** já validado (identidade vinho/dourado, sidebar, cards de
especialistas, modal de chat) — só a base técnica foi reconstruída, agora
seguindo modularização de verdade desde o primeiro arquivo.

**Capítulo mais recente — a variante "Especialista Único":** antes de
investir em escalar para os 12 especialistas, o projeto foi testado numa
cópia isolada (`D:\rjhub-especialista-unico\...`, regra 2 da seção 3) com
1 especialista genérico, pra validar se a hipótese central (assistente de
IA corporativo com conhecimento próprio) funcionava na prática. A partir
daí, o escopo daquela variante cresceu para incluir RBAC e um painel de
Super-Admin. Validado tudo isso, foi portado de volta para este projeto
principal — é o que está descrito no resto deste documento.

---

## 3. Regras de arquitetura (sempre respeitar)

1. **Nunca criar arquivos gigantes.** Cada módulo/arquivo tem uma única
   responsabilidade clara.
2. **Nunca misturar código de protótipo/teste com o código oficial.** Se
   for prototipar algo, isole em uma pasta explicitamente separada (ex:
   `sandbox/`, ou uma cópia completa do projeto em outro diretório, como
   foi feito com a variante "Especialista Único") — nunca deixe ambíguo
   qual é o código "de verdade".
3. **Nunca colocar dados dentro da interface** (HTML) nem regras de negócio
   dentro de `app.js` (frontend) ou das rotas do backend (`api/routes/`).
4. **Sempre modularizar.** Se um arquivo cresce demais ou passa a fazer
   mais de uma coisa, divida.
5. **Justifique mudanças arquiteturais** antes de aplicá-las — não troque
   uma decisão estrutural silenciosamente.
6. **Entre duas soluções técnicas equivalentes, escolha a mais simples.**
7. **Evite dependências desnecessárias entre módulos.**
8. **O contrato entre frontend e backend é a API.** O frontend nunca deve
   depender de detalhes internos do backend (nem vice-versa).
9. **Todo endpoint novo do backend segue sempre a mesma camada:**
   `models/` (schema Pydantic, só estrutura) → `services/` (regra de
   negócio / fonte dos dados) → `api/routes/` (só recebe requisição e
   chama o service). Nunca pule uma camada.
10. **Todo dado novo do frontend segue sempre o mesmo padrão "mock com
    fallback"** — ver seção 5, é o padrão mais importante deste projeto e
    se repete em cada nova funcionalidade. **Exceção deliberada:** o chat
    (seção 5.2) não usa fallback simulado — ver justificativa lá.
11. **Controle de acesso nega por padrão.** Qualquer sistema de permissão
    novo (RBAC, admin, etc.) começa assumindo que ninguém tem acesso a
    nada, e a liberação é sempre explícita — nunca o contrário.
12. **Segredos (chaves de API, client secrets) nunca ficam hardcoded nem
    em texto puro fora do `.env`.** Se uma chave real for exposta por
    engano (colada em chat, commitada, etc.), o procedimento é regenerar
    a chave, não só trocar onde ela é guardada.

---

## 4. Estrutura de arquivos atual

```
rj-hub/
├── CLAUDE.md                        (contexto original, mais curto)
├── CONTEXTO_PROJETO.md              (este arquivo)
├── README.md
├── .gitignore
│
├── frontend/
│   ├── index.html                   (casca completa: sidebar fixa + topbar, views de Início, Especialistas, Biblioteca, Conversas, Dashboard, Configurações, Super-Admin, e a view de chat integrada — não modal)
│   ├── css/
│   │   ├── style.css                identidade visual vinho `#AB0F15` / dourado `#E7C311` / sidebar escura `#171718`, todos os componentes (hero, card, grid, toolbar, kpi-grid, painel admin)
│   │   └── chat-view.css            layout de 2 colunas da view de chat (painel de conversa + painel de contexto) e "Nova conversa"/"Conversas recentes" da sidebar
│   └── js/
│       ├── data.js                  dados + fallback mock de tudo (ver seção 5)
│       ├── ui.js                    sidebar, navegação entre views, breadcrumb da topbar, menu mobile, botão de busca
│       ├── workspace.js             seletor de workspace (workspace-pill da topbar), saudação, card de especialista, grid da Home
│       ├── especialistas.js         listagem completa, busca/filtro, toggle de favoritos (estrela direto no card)
│       ├── biblioteca.js            renderização da lista de documentos
│       ├── conversas.js             histórico de conversas, "Conversas recentes" da sidebar, card "Continue de onde parou" da Home
│       ├── dashboard.js             indicadores (KPIs) e gráfico de barras verticais
│       ├── chat.js                  view de chat integrada (não modal) — conectado à IA real (ver seção 5.2), mensagens com avatar
│       ├── config.js                tema, idioma, workspace padrão
│       ├── admin.js                 painel de Super-Admin: Grupos, Usuários, Base de Conhecimento (ver seção 5.3)
│       ├── auth.js                  login Google, guarda/lê o token JWT, getToken(), estaLogado()
│       ├── api.js                   TODAS as chamadas HTTP ao backend, centralizadas aqui (inclui as funções admin*)
│       └── app.js                   só inicialização: carregarDadosIniciais() + init() orquestrando os outros módulos, incluindo initAdminPanel()
│
└── backend/
    ├── main.py                      cria o FastAPI app, CORS, SessionMiddleware, registra as rotas — nada de lógica
    ├── promover_admin.py            script utilitário: promove um e-mail a Super-Admin (insere na tabela `administradores`) sem precisar editar o seed — ver seção 5.3
    ├── requirements.txt             fastapi, uvicorn[standard], pydantic, sqlalchemy, anthropic, authlib, pyjwt, itsdangerous, httpx, python-dotenv, pdfplumber, python-docx, python-multipart
    ├── rjhub.db                     arquivo do banco SQLite (criado pelo db/seed.py, não versionar)
    ├── .env                         chaves e segredos (não versionar) — ver seção 6
    ├── core/
    │   └── config.py                nome do app, versão, CORS_ORIGINS, leitura do .env (caminho absoluto), chaves de API/JWT/OAuth
    ├── db/                          camada de acesso ao banco de dados (SQLite via SQLAlchemy)
    │   ├── database.py              engine, SessionLocal, Base, get_db()
    │   ├── models_db.py             modelos de TABELA (SQLAlchemy) — inclui RBAC/admin (GrupoDB, GrupoEspecialistaDB, UsuarioGrupoDB, AdministradorDB)
    │   └── seed.py                  popula o banco (idempotente) — inclui especialista único, grupo "geral", usuários e admin
    ├── models/                      schemas Pydantic — formato dos dados que trafegam pela API
    │   ├── especialista.py
    │   ├── workspace.py
    │   ├── documento.py             (CategoriaDocumento + Documento)
    │   ├── conversa.py
    │   ├── dashboard.py             (DashboardStat + DashboardBar)
    │   ├── chat.py                  (ChatMessage + ChatRequest + ChatResponse)
    │   ├── conhecimento.py          (DocumentoConhecimento)
    │   ├── auth.py                  (UsuarioAutenticado)
    │   └── admin.py                 schemas do painel de Super-Admin (GrupoCriar, GrupoOut, UsuarioOut etc.)
    ├── services/                    regra de negócio; consultam o banco via SQLAlchemy (ver seção 5.1)
    │   ├── especialistas_service.py
    │   ├── workspaces_service.py
    │   ├── biblioteca_service.py
    │   ├── conversas_service.py
    │   ├── dashboard_service.py
    │   ├── ia_service.py            motor de IA real (Anthropic) — ver seção 5.2
    │   ├── conhecimento_service.py  base de conhecimento (busca de contexto relevante + CRUD de documentos) — ver seção 5.2
    │   ├── auth_service.py          OAuth Google + emissão/decodificação do JWT próprio
    │   ├── permissoes_service.py    RBAC — quem pode ver o quê (ver seção 5.3)
    │   ├── admin_service.py         CRUD de grupos/atribuições, usado só pelo painel de Super-Admin
    │   └── extracao_texto.py        extrai texto de PDF/.docx enviados pelo Super-Admin
    └── api/
        ├── deps.py                  get_current_user (valida o JWT)
        ├── deps_admin.py            get_current_admin (get_current_user + checa se é Super-Admin)
        └── routes/                  endpoints HTTP; só recebem requisição e chamam o service
            ├── especialistas.py     GET /especialistas · GET /especialistas/{id} — exige login, filtra por RBAC
            ├── workspaces.py        GET /workspaces · GET /workspaces/{id} — exige login, filtra por RBAC
            ├── biblioteca.py        GET /biblioteca/categorias · GET /biblioteca/recentes
            ├── conversas.py         GET /conversas · GET /conversas/favoritas
            ├── dashboard.py         GET /dashboard/stats · GET /dashboard/bars
            ├── chat.py              POST /chat — exige login + checa RBAC do especialista
            ├── auth.py              GET /auth/login · GET /auth/callback · GET /auth/me
            └── admin.py             GET/POST/PUT/DELETE /admin/... — painel de Super-Admin, ver seção 5.3
```

---

## 5. O padrão mais importante do projeto: "mock com fallback"

Esse padrão foi estabelecido com `/especialistas` e replicado, **exatamente
igual**, para `/workspaces`, `/biblioteca` e `/conversas`. Qualquer endpoint
novo deve seguir o mesmo molde.

### No backend

- `services/<recurso>_service.py` consulta o banco (ver seção 5.1) e expõe
  funções `listar_xxx()` / `buscar_xxx(id)`.
- `api/routes/<recurso>.py` só expõe os endpoints HTTP chamando o service.

### No frontend

Para cada tipo de dado (ex: especialistas), existem **duas variáveis**:

```js
const SPECIALISTS_MOCK = [ ...dados fixos... ];   // fallback, nunca muda
let SPECIALISTS = SPECIALISTS_MOCK.slice();        // usada pela interface, é sobrescrita depois
```

- Todo o resto do código (`workspace.js`, `especialistas.js` etc.) **só lê
  `SPECIALISTS`**, nunca o `_MOCK`.
- `api.js` tem uma função `buscarXxx()` que faz o `fetch` (com
  `_authHeaders()` incluído nas rotas que exigem login — ver seção 5.4) e
  retorna `null` em caso de erro (nunca deixa a exceção estourar pra fora).
- `app.js` tem `carregarDadosIniciais()`, que roda **todas as chamadas em
  paralelo** com `Promise.all`, e para cada uma:
  - se a API respondeu com dados → sobrescreve a variável mutável
    (`SPECIALISTS = especialistasApi`)
  - se falhou → mantém o valor mockado que já estava lá, e loga um aviso
    `⚠️ API indisponível para X — usando X_MOCK.`
- **Importante:** `init()` em `app.js` é `async`. A ordem é sempre:
  1. Inicializações que não dependem de dados (`initAuth()`, `initUI()`,
     `setGreetingDate()`, `initChat()` etc.)
  2. `await carregarDadosIniciais()`
  3. Só então: inicializações e renderizações que dependem dos dados

Esse padrão garante que **a interface nunca quebra**, mesmo com o backend
fora do ar — ela só volta a mostrar dados de exemplo, silenciosamente, com
aviso no console.

**Cuidado conhecido:** se uma rota passar a exigir login (como aconteceu
com `/especialistas` e `/workspaces` quando o RBAC entrou), e a função
correspondente em `api.js` não for atualizada para mandar o header
`Authorization`, a chamada falha com 403 mesmo com o usuário logado, e cai
silenciosamente no mock — o que pode mascarar dados desatualizados sem
nenhum erro óbvio na tela. Sempre que uma rota mudar de pública para
autenticada, checar se a função correspondente em `api.js` já usa
`_authHeaders()`.

### Recursos já migrados para esse padrão
- ✅ Especialistas / Workspaces / Categorias e documentos da biblioteca /
  Conversas e favoritas / Indicadores e gráfico do dashboard

Todos os recursos do frontend já seguem o padrão "mock com fallback". Não
há mais nenhum dado 100% mockado sem endpoint por trás.

---

## 5.1 Padrão de banco de dados (backend) — SQLAlchemy + SQLite

O backend guarda os dados num arquivo SQLite (`backend/rjhub.db`) acessado
via SQLAlchemy.

### Dois "mundos" de modelo, propositalmente separados

- `models/*.py` → schemas **Pydantic**, formato que trafega pela API.
- `db/models_db.py` → modelos de **tabela SQLAlchemy**, formato que mora
  no banco. Nomeados com sufixo `DB` (`EspecialistaDB`, `WorkspaceDB`,
  `GrupoDB`, `AdministradorDB` etc.) pra nunca confundir com o schema
  Pydantic equivalente.

Quem converte de um formato pro outro é sempre o `service` (função
`_para_schema(row)` ou equivalente).

### `db/database.py`
Só a conexão: `engine`, `SessionLocal` (fábrica de sessões), `Base`
(classe base dos modelos) e `get_db()`. `DATABASE_URL` é a única linha que
muda se um dia trocar SQLite por Postgres.

### `db/models_db.py`
Uma classe por tabela. Padrões já estabelecidos:
- Quando o schema Pydantic não tem um `id` natural, a tabela ganha uma
  chave interna `id`/`pk` autoincremento **que nunca aparece na resposta
  da API** — é só controle do banco.
- Relações um-para-muitos com ordem importam (ex: membros de um workspace)
  usam uma tabela de associação própria com uma coluna `ordem`
  (`WorkspaceMembroDB`).
- Quando um campo do schema representa uma referência a outro recurso, a
  coluna no banco tem um nome mais descritivo (`especialista_id`) pra não
  confundir com a chave primária da própria tabela.
- Sistemas de permissão (RBAC, admin) usam tabelas de associação
  muitos-para-muitos dedicadas (`GrupoEspecialistaDB`, `UsuarioGrupoDB`) em
  vez de FK direta — uma pessoa/grupo pode ter mais de uma associação.

### `db/seed.py`
Script único que cria todas as tabelas (`Base.metadata.create_all`) e
insere os dados iniciais. **Idempotente**: cada recurso verifica se o
registro já existe antes de inserir. Estratégia de dedupe varia conforme o
recurso tem ou não um identificador natural (por `id`, ou pelo campo mais
único disponível quando não há um).

Rodar (sempre a partir de `backend/`, com o venv ativado):
```bash
python -m db.seed
```
Precisa rodar de novo sempre que uma tabela nova for adicionada — nesse
caso, geralmente é mais simples apagar o `rjhub.db` e rodar o seed do
zero (`del rjhub.db` no Windows).

### `services/*.py`
Cada service abre uma sessão (`SessionLocal()`), consulta, converte cada
linha pro schema Pydantic correspondente, e sempre fecha a sessão num
`finally`.

### Se for adicionar um recurso novo daqui pra frente
1. Tabela em `db/models_db.py`.
2. Seed em `db/seed.py`.
3. Service correspondente consultando o banco.
4. `models/` e `api/routes/` só entram em cena se o recurso for
   totalmente novo.

---

## 5.2 Motor de IA real (chat) + Base de Conhecimento — Anthropic (Claude)

```
POST /chat
Body: { "especialista_id": "especialista-rj", "mensagens": [{"role": "user"|"assistant", "content": "..."}] }
Resposta: { "resposta": "texto gerado pela IA" }
```
Exige login (`get_current_user`) e checa RBAC (`usuario_tem_acesso`) antes
de gerar qualquer resposta — ver seção 5.3.

### Como funciona

- `services/ia_service.py` monta um **system prompt** dinâmico com base no
  especialista (`nome` + `desc`) e nos documentos relevantes da base de
  conhecimento (`conhecimento_service.buscar_contexto_relevante`), e chama
  a API da Anthropic com o histórico da conversa.
- O modelo usado é `ANTHROPIC_MODEL` (hoje `"claude-sonnet-5"`), definido
  em `core/config.py`.
- A chave da API (`ANTHROPIC_API_KEY`) **nunca fica no código** — é lida
  do `.env` via `core/config.py`. Se não estiver definida, o service lança
  um erro claro em vez de travar o backend inteiro na subida.
- O `client` da Anthropic só é criado na primeira chamada ao chat (lazy).
- **Tratamento de erro robusto:** `_extrair_texto()` percorre todos os
  blocos de `resposta.content` e junta só os do tipo `"text"` — necessário
  porque, com extended thinking, `content[0]` pode ser um bloco de
  raciocínio sem `.text`, o que quebrava a resposta antes dessa correção.
  Erro 529 (Anthropic sobrecarregada) e falha de conexão são tratados
  especificamente, devolvendo 503 com mensagem clara em vez de um erro
  genérico confuso.

### Base de Conhecimento (`conhecimento_service.py`)

- Tabela `documentos_conhecimento` (`especialista_id`, `titulo`,
  `conteudo`) — o texto de verdade por trás de cada especialista.
- `buscar_contexto_relevante(especialista_id, pergunta, limite)`: relevância
  por contagem de palavras-chave em comum entre a pergunta e o documento
  (título pesa mais que o corpo) — **sem embeddings/busca vetorial**, por
  decisão consciente: o volume esperado (dezenas de documentos por
  especialista) não justifica essa complexidade extra. Se nada for
  relevante, o especialista é instruído a ser honesto sobre a limitação em
  vez de inventar.
- `criar_documento` / `deletar_documento`: usadas pelo painel de
  Super-Admin (seção 5.3), com upload de arquivo (PDF/.docx) e extração
  automática de texto via `services/extracao_texto.py`.

### No frontend (`chat.js`)

- View de chat integrada na mesma casca (sidebar e topbar continuam
  visíveis) — não é modal/overlay. Layout em 2 colunas (`chat-view.css`):
  painel de conversa + painel de contexto lateral ("Base consultada" com
  os documentos usados na última resposta).
- Mensagens exibidas com avatar (ícone do especialista pro bot, iniciais
  do usuário) — `addMessage()` monta avatar + bolha via `innerHTML`, com
  `escapeHtml()` próprio pra manter a mesma segurança que `textContent`
  já dava antes.
- `currentMessages` mantém o histórico da conversa atual em memória, pra
  dar contexto ao modelo entre mensagens.
- `sendReply()` é `async`: chama `enviarMensagemChat()` (em `api.js`), que
  já inclui o header de autenticação.
- **Sem fallback simulado (exceção à regra 10 da seção 3, deliberada):**
  diferente dos outros recursos, se a chamada ao `/chat` falhar, o chat
  **não** cai de volta para respostas simuladas (`REPLIES`/`QA_REPLIES`) —
  mostra uma mensagem de erro clara ("Não consegui falar com o especialista
  agora..."). Simular uma resposta de IA convincente quando a IA de
  verdade está fora do ar seria enganoso para quem está usando um
  assistente corporativo pra tomar decisões reais — melhor um erro visível
  do que uma resposta falsa parecendo real.

### Configuração necessária

`ANTHROPIC_API_KEY` precisa estar no `.env` — ver seção 6.

---

## 5.3 Sistema de permissões (RBAC) + Painel de Super-Admin

Camada de acesso **independente** do Workspace (que continua sendo só
agrupamento de navegação, não controla quem vê o quê).

### Modelo de dados
- `GrupoDB` — id, nome.
- `GrupoEspecialistaDB` — quais especialistas um grupo libera.
- `UsuarioGrupoDB` — a quais grupos um e-mail pertence.
- `AdministradorDB` — e-mails com acesso de Super-Admin. Eixo **separado**
  de Grupo: alguém pode ser admin sem estar em nenhum grupo de chat, e
  vice-versa.

### Regra: negar por padrão (regra 11 da seção 3)
E-mail sem grupo = sem acesso a nenhum especialista.

### Onde é aplicado
- `services/permissoes_service.py` — `especialistas_visiveis_para(email)`
  e `usuario_tem_acesso(email, especialista_id)`.
- `GET /especialistas` e `GET /workspaces` — exigem login, filtram pelo
  e-mail logado. Um workspace sem nenhum membro visível some da lista.
- `POST /chat` — barra (403) tentativa de conversar com um especialista
  fora do grupo do usuário, mesmo que descubram o ID por fora da
  interface. Essa é a segurança de verdade; a filtragem na listagem é só
  UX.
- Ao negar acesso a um especialista específico (`GET
  /especialistas/{id}`), a resposta é 404 (não 403) — não revela nem que
  o especialista existe, pra não vazar informação sobre o que tem no
  sistema.

### Painel de Super-Admin (`/admin/...`)
Gerencia grupos, atribuições de usuário e documentos **pelo próprio
portal**, sem depender de editar `seed.py` e recriar o banco a cada
mudança.
- Toda rota protegida por `get_current_admin` (`api/deps_admin.py`,
  composto sobre `get_current_user`).
- `GET/POST /admin/grupos`, `DELETE /admin/grupos/{id}`,
  `PUT /admin/grupos/{id}/especialistas`, `GET /admin/usuarios`,
  `PUT /admin/usuarios/{email}/grupos`,
  `GET /admin/especialistas/{id}/documentos`,
  `POST /admin/especialistas/{id}/documentos/upload` (aceita PDF/.docx,
  extrai texto automaticamente), `DELETE /admin/documentos/{id}`.

**Interface própria — CONCLUÍDA** (`frontend/js/admin.js`). Item
"Super-Admin" na sidebar, visível só se `/admin/grupos` responder com
sucesso no carregamento — não existe endpoint dedicado "sou admin?"; em
vez de criar um só pra isso, `initAdminPanel()` reaproveita a própria
tentativa de leitura pra decidir se mostra o item (se vier `null` = 403
ou API offline, o item continua com `display:none`, que já é o padrão no
HTML). 3 abas, mesmo padrão visual do resto do app (`hero`/`card`/
`toolbar`):
- **Grupos** — criar (id + nome), excluir, e por grupo um checklist
  (`admin-checklist`) pra escolher quais especialistas ele libera
  (`PUT /admin/grupos/{id}/especialistas`).
- **Usuários** — adicionar um e-mail novo escolhendo os grupos dele,
  editar os grupos de quem já está na lista, ou "Remover acesso"
  (equivale a mandar uma lista vazia de grupos — não existe endpoint de
  exclusão de usuário, porque usuário não é uma entidade própria no
  banco, só existe via linhas em `usuario_grupos`).
- **Base de Conhecimento** — escolhe o especialista num `<select>`, lista
  os documentos dele, sobe um PDF/.docx novo (extração automática via
  `extrair_texto`, ver seção 5.2) ou exclui um existente.

Todas as chamadas de escrita usam `alert()` pra erro e simplesmente
recarregam a lista em caso de sucesso — não há um sistema de toast/
notificação ainda; se isso incomodar no uso do dia a dia, é uma melhoria
futura de baixo risco.

### Promover um e-mail a Super-Admin
Além do seed inicial (abaixo), existe `backend/promover_admin.py` —
script standalone que insere um e-mail na tabela `administradores` sem
precisar mexer no `seed.py` nem recriar o banco:
```bash
python promover_admin.py seu.email@rjalimentos.com.br
```
Idempotente (roda `Base.metadata.create_all()` antes, e avisa sem
duplicar se o e-mail já for admin). É o caminho recomendado pra promover
alguém depois que o banco já está em uso — editar o seed só faz sentido
pra popular do zero.

### Estado atual do seed
Grupo `geral` libera o `especialista-rj`. O seed cadastra um Super-Admin
inicial de exemplo — qualquer e-mail adicional (ou substituição) deve ser
feito via `promover_admin.py` (acima), não editando o seed depois que o
banco já está em uso.

---

## 5.4 Autenticação (SSO Google Workspace)

Login real com e-mail corporativo (`@rjalimentos.com.br`).
- Backend: Authlib (OAuth) + JWT próprio (`api/routes/auth.py`,
  `services/auth_service.py`). `GET /auth/login` inicia o fluxo, `GET
  /auth/callback` processa o retorno do Google e emite o JWT, `GET
  /auth/me` retorna os dados do usuário logado.
- `api/deps.py` (`get_current_user`) valida o JWT em qualquer rota
  protegida (`Depends(get_current_user)`).
- Frontend: `js/auth.js` guarda/lê o token (`getToken()`, `estaLogado()`).
  `api.js` tem `_authHeaders()`, que qualquer função que bate numa rota
  protegida deve incluir no `fetch`.
- Hoje protegidas: `/chat`, `/especialistas`, `/workspaces`, `/admin/*`
  (estas últimas exigem login **e** ser Super-Admin — ver seção 5.3).
  Ainda públicas: `/biblioteca`, `/conversas`, `/dashboard`.

---

## 6. Como rodar o projeto localmente

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Configuração via `.env`** (na pasta `backend/`, nunca versionar):
```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
JWT_SECRET_KEY=qualquer-string-nao-vazia
SESSION_SECRET_KEY=qualquer-outra-string-nao-vazia
```
`core/config.py` carrega o `.env` a partir do **caminho absoluto do
próprio arquivo** (`Path(__file__).resolve().parent.parent / ".env"`),
não por descoberta automática — isso evita um bug já visto em que o
`.env` não era encontrado de dentro do processo do `uvicorn --reload`
mesmo existindo e sendo válido. `JWT_SECRET_KEY`/`SESSION_SECRET_KEY` têm
um valor padrão de fallback no código, mas devem ser trocados antes de
expor a API fora da máquina local. Se um segredo real for exposto por
engano em algum lugar (chat, print, etc.), regenerar em vez de só trocar
onde está guardado (regra 12 da seção 3).

**Criar/atualizar o banco:**
```bash
python -m db.seed
```
Idempotente — seguro rodar de novo. Se uma tabela nova foi adicionada,
apagar `rjhub.db` antes e rodar de novo do zero.

**Subir o servidor:**
```bash
uvicorn main:app --reload
```
API em `http://127.0.0.1:8000`, documentação automática em
`http://127.0.0.1:8000/docs`.

**Frontend:**
```bash
cd frontend
python -m http.server 8080
```
Nunca abrir `index.html` direto com `file://` (por causa do CORS). Acesse
`http://127.0.0.1:8080`.

**Como validar que tudo está integrado:** faça login com um e-mail
corporativo. Com o backend rodando, o Console (F12) deve mostrar os
especialistas/workspaces carregados da API (não do mock), sem avisos de
`⚠️ API indisponível`. Testando o chat, a resposta deve vir baseada nos
documentos reais do especialista (não um template genérico) — se aparecer
algo genérico demais e descolado da pergunta, suspeitar que o `chat.js`
está caindo em algum caminho de simulação antigo, não na API real.

---

## 7. Estado atual (checkpoint)

- **Frontend:** todas as views implementadas e funcionando, view de chat
  integrada (não modal) conectada à IA real. Redesign visual (Parte B) —
  **CONCLUÍDO**: sidebar fixa escura (`#171718`) + topbar com breadcrumb e
  workspace-pill + área central, identidade vinho `#AB0F15`/dourado
  `#E7C311` aplicada em todas as views (Início, Especialistas, Biblioteca,
  Conversas, Dashboard, Configurações, Super-Admin).
- **Backend:** FastAPI com todos os recursos reais (especialistas,
  workspaces, biblioteca, conversas, dashboard, chat, admin, auth).
- **Banco de dados (SQLite + SQLAlchemy) — CONCLUÍDO**, incluindo as
  tabelas de RBAC/admin.
- **Motor de IA real (Anthropic/Claude) — CONCLUÍDO**, com tratamento de
  erro robusto (extended thinking, sobrecarga da API) e base de
  conhecimento real injetada no contexto.
- **Autenticação corporativa (SSO Google) — CONCLUÍDO.**
- **Controle de acesso por grupo (RBAC) + painel de Super-Admin —
  CONCLUÍDO, com interface visual própria** (`frontend/js/admin.js`):
  Grupos, Usuários e Base de Conhecimento, ver seção 5.3. Promoção de
  novos admins via `backend/promover_admin.py`, sem precisar editar o
  seed.
- **Modelo de especialistas — reduzido deliberadamente** para 1
  especialista institucional no lançamento inicial (ver seção 1), com a
  arquitetura já pronta para expandir.
- **Fonte de dados — só documentos estáticos por enquanto.** Decisão
  consciente de não conectar direto ao Oracle/ERP por segurança de dados;
  Power BI é o caminho cogitado para dado dinâmico no futuro (empresa já
  tem licenciamento Pro/Premium), ainda não implementado.

---

## 8. Próximos passos (em ordem sugerida)

Nenhuma decisão tomada ainda entre as frentes abaixo — dependem de
prioridade de negócio, não de bloqueio técnico:

1. **Definir o(s) próximo(s) especialista(s) de verdade.** A
   infraestrutura de RBAC já suporta múltiplos; falta decidir qual área
   entra em seguida e reunir/curar os documentos reais dela. Com o painel
   de Super-Admin pronto, cadastrar o especialista, criar o grupo dele e
   subir os documentos já pode ser feito pelo próprio portal, sem editar
   `seed.py`.
2. **Polimento de UX pendente, baixa prioridade:**
   - Busca de verdade na topbar (hoje o botão "⌕ Busca" só leva pra
     Especialistas com o campo em foco — não busca em documentos/
     conversas ainda).
   - Feedback visual além de `alert()` no painel de Super-Admin (toast/
     notificação em vez de recarregar a lista silenciosamente).
   - `LIB_CATS`/`CONVERSATIONS_FAVORITAS` ainda são buscados da API em
     `app.js` mas não são mais exibidos em nenhuma view (perderam a seção
     na Home/Biblioteca/Conversas durante o reskin) — ou remover a
     chamada, ou trazer essas seções de volta, a decidir.

Mais adiante, sem prioridade definida ainda:
3. **Dado dinâmico via Power BI** (não Oracle direto — ver seção 7) para
   métricas/indicadores em tempo real.
4. **Migrar de SQLite para PostgreSQL** se o projeto for para produção com
   acesso concorrente — a única mudança necessária é a `DATABASE_URL` em
   `db/database.py`.
5. **Hospedar em servidor/ambiente web real**, tirando a dependência da
   máquina local do usuário ficar ligada.

Não pule etapas — cada uma dessas deve nascer seguindo exatamente os
mesmos padrões já estabelecidos nas seções 3, 5, 5.1, 5.2, 5.3 e 5.4.

---

## 9. Como devo agir, se eu for a IA continuando esse projeto

- Leia este documento inteiro antes de sugerir qualquer código.
- Sempre que for adicionar um novo recurso de dados, siga o padrão da
  seção 5 sem inventar uma variação nova — e lembre que o chat é a
  exceção deliberada ao fallback simulado (seção 5.2).
- Sempre que for adicionar uma rota no backend, siga a camada
  `models → services → api/routes` da seção 3, regra 9. Se a rota exigir
  login e/ou permissão, siga o padrão de `Depends(get_current_user)` /
  `Depends(get_current_admin)` e `permissoes_service.py` (seção 5.3) —
  nunca invente um mecanismo de auth paralelo.
- Sempre que for adicionar uma tabela/recurso novo no banco, siga o
  padrão da seção 5.1 (`db/models_db.py` → `db/seed.py` → `service`).
- Qualquer sistema de permissão novo nega por padrão (regra 11).
- Nunca proponha guardar uma chave/segredo fora do `.env`, nem imprimir
  seu valor completo em nenhum lugar desnecessariamente (regra 12).
- Antes de alterar uma rota de pública para autenticada, verifique se a
  função correspondente em `api.js` já usa `_authHeaders()` — senão a
  troca quebra silenciosamente, caindo no mock sem erro óbvio.
- Se for prototipar algo fora do que já está validado, isole em cópia
  separada (regra 2) — nunca misture com este projeto até estar validado
  e deliberadamente portado.
- Se for adicionar uma view/tela nova no frontend, reaproveite os
  componentes visuais já estabelecidos no redesign (Parte B, concluída) —
  `.hero`, `.card`, `.grid`, `.toolbar`, `.kpi-grid`, `.admin-*` — em vez
  de criar padrão visual novo. `style.css` tem tudo comentado por bloco.
- Valide sintaxe (JS: `node --check arquivo.js`; Python:
  `python3 -m py_compile arquivo.py`) antes de entregar qualquer arquivo.
- Entregue mudanças arquivo por arquivo (a pessoa não está usando Claude
  Code, está copiando os arquivos manualmente para a pasta local em
  `D:\RJ HUB\rjhub-v2\`) — não assuma que ela vai rodar comandos de
  automação além dos que já usa (`uvicorn`, `python -m http.server`,
  `python -m db.seed`).
- Depois de qualquer mudança, oriente exatamente como testar (o que
  esperar no console do navegador, o que checar em `/docs`).
