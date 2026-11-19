# RJ HUB — Contexto Completo do Projeto

> Este documento existe para ser colado no início de uma nova conversa com
> uma IA (Claude ou outra), para que ela entenda o projeto inteiro sem
> precisar reexplicar nada do zero. Leia tudo antes de sugerir qualquer
> mudança, e trate as regras da seção 3 como inegociáveis.
>
> Última atualização: novembro/2026 (inclui deploy de teste na Render, decisão
> pela Locaweb, Markdown no chat e tema Padrão/Escuro/Sistema).

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
│   ├── index.html                   (casca completa: sidebar fixa + topbar, views de Início, Especialistas, Biblioteca, Conversas, Dashboard, Configurações, Super-Admin, e a view de chat integrada — não modal). Carrega `marked` + `DOMPurify` por CDN (Markdown nas respostas do chat) e tem um script inline no `<head>` que aplica o tema salvo antes do CSS (evita "piscar")
│   ├── css/
│   │   ├── style.css                identidade visual vinho `#AB0F15` / dourado `#E7C311` / sidebar escura `#171718`, todos os componentes (hero, card, grid, toolbar, kpi-grid, painel admin). Temas: `:root` = Padrão, `[data-theme="escuro"]` = Escuro (seção 5.7). `--surface` = fundo de card/painel; `--white` = só texto/ícone branco sobre vinho/dourado
│   │   └── chat-view.css            layout de 2 colunas da view de chat (painel de conversa + painel de contexto) e "Nova conversa"/"Conversas recentes" da sidebar, mais os estilos do Markdown dentro das bolhas do especialista (`.msg.bot .bubble ...`)
│   └── js/
│       ├── data.js                  dados + fallback mock de tudo (ver seção 5)
│       ├── ui.js                    sidebar, navegação entre views, breadcrumb da topbar, menu mobile, botão de busca, tema (Padrão/Escuro/Sistema — `initThemeSwitcher`, seção 5.7)
│       ├── workspace.js             seletor de workspace (workspace-pill da topbar), saudação, card de especialista, grid da Home
│       ├── especialistas.js         listagem completa, busca/filtro, toggle de favoritos (estrela direto no card)
│       ├── biblioteca.js            renderização da lista de documentos
│       ├── conversas.js             histórico de conversas, "Conversas recentes" da sidebar, card "Continue de onde parou" da Home
│       ├── dashboard.js             indicadores (KPIs) e gráfico de barras verticais
│       ├── chat.js                  view de chat integrada (não modal) — conectado à IA real (ver seção 5.2), mensagens com avatar, respostas do especialista renderizadas como Markdown (`renderMarkdown`)
│       ├── config.js                tema, idioma, workspace padrão
│       ├── admin.js                 painel de Super-Admin: Grupos, Usuários, Base de Conhecimento, Especialistas, Administradores — 5 abas (ver seção 5.3). verificarAdmin() roda cedo no init(); inicializarPainelAdmin() monta as abas depois.
│       ├── auth.js                  login Google, guarda/lê o token JWT, getToken(), estaLogado()
│       ├── api.js                   TODAS as chamadas HTTP ao backend, centralizadas aqui (inclui as funções admin*). `API = ""` (caminho relativo, mesma origem — seção 5.6)
│       └── app.js                   só inicialização: carregarDadosIniciais() + init() orquestrando os outros módulos, incluindo initAdminPanel()
│
└── backend/
    ├── main.py                      cria o FastAPI app, CORS, SessionMiddleware, registra as rotas, cria as tabelas que faltam (`create_all`), garante o admin inicial (`INITIAL_ADMIN_EMAIL`) e serve o frontend (`StaticFiles` em "/", sempre por último) — ver seção 5.6
    ├── promover_admin.py            script utilitário: promove um e-mail a Super-Admin (insere na tabela `administradores`) sem precisar editar o seed — ver seção 5.3
    ├── scripts/
    │   └── migrar_schema_v2.py      script pontual: atualiza o schema de `conversas`/`documentos_conhecimento` sem apagar dado existente — ver seção 5.5. Já rodado uma vez neste projeto; só roda de novo se `db/models_db.py` mudar de formato outra vez.
    ├── requirements.txt             fastapi, uvicorn[standard], pydantic, sqlalchemy, anthropic, authlib, pyjwt, itsdangerous, httpx, python-dotenv, pdfplumber, python-docx, python-multipart
    ├── rjhub.db                     arquivo do banco SQLite (criado pelo db/seed.py, não versionar)
    ├── .env                         chaves e segredos (não versionar) — ver seção 6
    ├── core/
    │   └── config.py                nome do app, versão, CORS_ORIGINS, leitura do .env (caminho absoluto), chaves de API/JWT/OAuth, `FRONTEND_URL`, `INITIAL_ADMIN_EMAIL`
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
Resposta: { "resposta": "texto gerado pela IA (em Markdown)", "documentos_usados": [{ "id": 1, "titulo": "..." }] }
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

- **Formatação em Markdown:** o system prompt (`_montar_system_prompt`)
  instrui o modelo a usar `###` para seções, listas, `**negrito**` e
  blocos de código quando o conteúdo tiver passos/itens/seções — e a NÃO
  forçar estrutura em respostas curtas ou conversacionais.
- **Concorrência:** `post_chat` em `api/routes/chat.py` é `def` comum (não
  `async def`), então o FastAPI o executa em threadpool — várias pessoas
  conversam ao mesmo tempo sem uma travar esperando a Anthropic da outra
  (limite padrão ≈ 40 simultâneos, suficiente para a meta de 30). **Não
  transformar em `async def` sem trocar o client da Anthropic por
  assíncrono**, senão passa a bloquear.

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
- **Markdown nas respostas do especialista:** `renderMarkdown()` converte
  com `marked` e sanitiza com `DOMPurify` antes de inserir (HTML gerado por
  IA nunca vai direto no `innerHTML`). Só vale para mensagens do bot — as
  do usuário continuam sempre texto puro via `escapeHtml()`. Se os scripts
  do CDN não carregarem, cai para texto escapado (sem formatação, mas sem
  quebrar o chat).
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
Gerencia especialistas, grupos, atribuições de usuário, administradores e
documentos **pelo próprio portal**, sem depender de editar `seed.py` e
recriar o banco a cada mudança.
- Toda rota protegida por `get_current_admin` (`api/deps_admin.py`,
  composto sobre `get_current_user`).
- `GET/POST /admin/especialistas`, `GET/POST /admin/grupos`,
  `DELETE /admin/grupos/{id}`, `PUT /admin/grupos/{id}/especialistas`,
  `GET /admin/usuarios`, `PUT /admin/usuarios/{email}/grupos`,
  `GET/POST /admin/administradores`, `DELETE /admin/administradores/{email}`
  (bloqueado se `email` for o do próprio usuário logado — sem essa
  checagem um Super-Admin sozinho poderia se trancar fora do painel),
  `GET /admin/especialistas/{id}/documentos`,
  `POST /admin/especialistas/{id}/documentos/upload` (aceita PDF/.docx,
  extrai texto automaticamente), `DELETE /admin/documentos/{id}`,
  `DELETE /admin/especialistas/{id}` (bloqueia se houver dependência —
  ver "Excluir especialista" abaixo),
  `GET /admin/especialistas/{id}/documentos/exportar` (baixa `.zip` de
  backup, ver abaixo).

**Interface própria — CONCLUÍDA** (`frontend/js/admin.js`). Itens
"Super-Admin" e "Biblioteca" na sidebar, visíveis só se `/admin/grupos`
responder com sucesso no carregamento — não existe endpoint dedicado "sou
admin?"; em vez de criar um só pra isso, `verificarAdmin()` (chamada BEM
CEDO no `init()`, antes de `carregarDadosIniciais()`) reaproveita a
própria tentativa de leitura pra decidir. Se vier `null` (403 ou API
offline), `window.IS_ADMIN` fica `false` e os itens continuam com
`display:none`, que já é o padrão no HTML. Chamar isso cedo importa:
`carregarDadosIniciais()` só busca a Biblioteca se `window.IS_ADMIN` for
`true` — evita uma chamada 403 desperdiçada pra quem não é admin.

Depois disso, `inicializarPainelAdmin()` monta as 5 abas (mesmo padrão
visual do resto do app — `hero`/`card`/`toolbar`):
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
- **Especialistas** — cria especialista novo (id, ícone, nome,
  descrição). **Não vincula a nenhum grupo automaticamente** — criar aqui
  não dá acesso a ninguém, isso continua sendo feito na aba Grupos, de
  propósito (evita liberar acesso sem querer). Cada card tem dois botões:
  **"Exportar documentos"** (baixa um `.zip` com um `.txt` por documento —
  só leitura, não apaga nada, serve como backup manual) e **"Excluir"**
  (bloqueia — não exclui em cascata — se o especialista tiver qualquer
  dependência viva: documentos na Base de Conhecimento, vínculo com
  grupo, presença em workspace, ou conversas registradas; a mensagem de
  erro diz exatamente qual dependência está bloqueando).
- **Administradores** — lista quem é Super-Admin, promove um
  e-mail novo, remove (exceto a si mesmo — ver acima).

**Importante, e é a causa mais provável de confusão ao testar:** ser
Super-Admin (tabela `administradores`) e pertencer a um Grupo (tabela
`usuario_grupos`, o que libera especialista pra conversar) são **eixos
separados de propósito** desde o início do RBAC. Um e-mail promovido a
admin via `promover_admin.py` ou pela aba Administradores **não** entra
automaticamente em nenhum grupo — se aparecer com "Especialistas: 0" ou
a Home vazia logado como admin, o mais provável é que esse e-mail nunca
foi adicionado a um grupo pela aba Usuários (não é bug, é o design).

Todas as chamadas de escrita usam `alert()` pra erro e simplesmente
recarregam a lista em caso de sucesso — não há um sistema de toast/
notificação ainda; se isso incomodar no uso do dia a dia, é uma melhoria
futura de baixo risco.

### Ponto de atenção: duas listas de especialistas no frontend, propositalmente diferentes
`admin.js` mantém **duas variáveis globais** de especialistas, e usar a
errada num lugar novo já causou um bug real (ver seção 7):
- `SPECIALISTS` — populada por `buscarEspecialistas()` (`GET
  /especialistas`), **filtrada por RBAC**: só traz o que o grupo do
  usuário logado libera. Usada em Home, Dashboard, busca de
  especialistas, chat — tudo que é experiência de usuário comum.
- `ADMIN_ESPECIALISTAS_TODOS` — populada por `adminListarEspecialistas()`
  (`GET /admin/especialistas`), **sem filtro nenhum**. Usada só dentro do
  próprio painel de Admin: `renderAdminEspecialistas()`,
  `populateAdminEspecialistaSelect()` (select da Base de Conhecimento) e
  o checklist de vínculo da aba Grupos.

**Por que a distinção existe:** um especialista recém-criado ainda não
pertence a grupo nenhum — se o painel de Admin usasse `SPECIALISTS`
(filtrada), o especialista novo nunca apareceria em lugar nenhum do
próprio painel, incluindo o checklist de Grupos, que é justamente onde
ele precisaria aparecer pra ser vinculado a um grupo pela primeira vez.
**Qualquer tela nova do painel de Admin que precise listar especialistas
deve usar `ADMIN_ESPECIALISTAS_TODOS`, nunca `SPECIALISTS`.**
`recarregarEspecialistasGlobal()` recarrega as duas de uma vez, sempre
que um especialista é criado ou excluído.

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
pra popular do zero. (A aba Administradores do próprio painel faz a
mesma coisa, sem precisar de terminal — ver acima.)

### Estado atual do seed
Grupo `geral` libera o `especialista-rj`. O seed cadastra um Super-Admin
inicial de exemplo — qualquer e-mail adicional (ou substituição) deve ser
feito via `promover_admin.py` ou a aba Administradores (acima), não
editando o seed depois que o banco já está em uso.

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
- Hoje protegidas: `/chat`, `/especialistas`, `/workspaces`, `/conversas`,
  `/dashboard` (login; escopo por permissão — seção 5.5), e `/biblioteca` +
  `/admin/*` (login **e** Super-Admin — seção 5.3). Públicas: só `/health`,
  `/auth/login`, `/auth/callback` e os arquivos estáticos do frontend.
- **`FRONTEND_URL` (variável de ambiente):** para onde o backend redireciona
  depois do login (`FRONTEND_URL/#token=...`). Como o backend agora serve o
  frontend, ela deve ser a URL pública do próprio app (local:
  `http://localhost:8000`; teste: `https://rj-hub-1.onrender.com`; produção:
  o domínio final). O padrão no código (`http://127.0.0.1:8080`) é herança do
  modelo antigo de 2 servidores e está ERRADO hoje — sempre definir. Se
  faltar, o login "funciona" nos bastidores mas manda o navegador para um
  endereço que não existe.
- **Google Cloud Console → "URIs de redirecionamento autorizados":** um por
  ambiente, no formato exato `<origem>/auth/callback` (ex:
  `http://localhost:8000/auth/callback`, `https://rj-hub-1.onrender.com/auth/callback`).
  Pode haver vários ao mesmo tempo. Para o Google, `localhost` e `127.0.0.1`
  são endereços diferentes — acessar sempre pelo mesmo que foi cadastrado.
  Erro `redirect_uri_mismatch` = o URI usado não está na lista (já aconteceu
  tanto na Render quanto no local).
- **Chaves JWT/Session:** pelo menos 32 bytes (gerar com
  `python -c "import secrets; print(secrets.token_urlsafe(32))"`). O aviso
  `InsecureKeyLengthWarning` nos logs indica chave curta. Chaves que já
  apareceram em conversa de chat (como as usadas no teste da Render) devem
  ser regeneradas, não reaproveitadas, na produção (regra 12).

---

## 5.5 Dado real: Conversas, Dashboard, Biblioteca e identidade do usuário

Até esta rodada, Conversas/Dashboard/Biblioteca liam de tabelas
**semeadas manualmente** (`ConversaDB`/`DashboardStatDB`/`DashboardBarDB`/
`DocumentoDB` antigos) — nunca refletiam uso de verdade. Isso mudou:

### Conversas — gravação real
`ConversaDB` foi reformulada: 1 linha por par (usuário, especialista),
não mais 1 por mensagem nem linhas semeadas. `services/conversas_
service.py::registrar_interacao(email, especialista_id, pergunta)` é
chamada por `api/routes/chat.py` a cada resposta **bem-sucedida** do
motor de IA (upsert: cria se não existe, senão atualiza preview,
`total_mensagens` e `atualizado_em`). Uma pergunta que deu erro 503/502
não vira conversa — não distorce Dashboard/histórico com tentativas sem
resposta de verdade.

`GET /conversas` exige login e **sempre filtra pelo e-mail de quem
pede** — conversa é dado pessoal, ninguém vê o histórico de outra
pessoa (isso vale pra Admin também, diferente do Dashboard abaixo). O
texto "há 18 minutos"/"Ontem" é calculado a partir de `atualizado_em`
real (`_humanizar_quando()`), não mais texto fixo.

### Dashboard — calculado, com escopo por permissão
`services/dashboard_service.py` não lê mais tabela nenhuma semeada —
calcula em cima de `conversas_service` (`contar_mensagens_por_
especialista`, `contar_conversas_na_semana`) e contagens diretas
(`EspecialistaDB`, `DocumentoConhecimentoDB`). `GET /dashboard/stats` e
`/bars` exigem login e recebem `eh_administrador(usuario.email)`:
- **Super-Admin** vê agregado de **todos** os usuários.
- **Usuário comum** só vê o próprio uso (especialistas visíveis pra ele,
  documentos dos especialistas que ele acessa, conversas dele).

O gráfico de barras (`val`, 0-100) é normalizado pelo maior valor entre
os especialistas do escopo — o frontend usa `val` direto como altura em
%, então a normalização tem que acontecer no backend antes de responder.

### Biblioteca — unificada com a Base de Conhecimento, só Admin
Decisão tomada nesta rodada: a Biblioteca (`Documento`/`CategoriaDocumento`)
passou a ler `DocumentoConhecimentoDB` — os **mesmos** documentos que
alimentam o chat, não mais uma tabela desconectada (`DocumentoDB`/
`CategoriaDocumentoDB` antigos continuam existindo no banco, só não são
mais lidos). "Categoria" virou "especialista", com a contagem real de
documentos dele. `DocumentoConhecimentoDB` ganhou a coluna `criado_em`
(usada pro "Atualizado há X dias" real).

`GET /biblioteca/categorias` e `/recentes` agora exigem `get_current_admin`
(mesma proteção das rotas `/admin/*`) — o conteúdo pode ser sensível.
Item "Biblioteca" escondido da sidebar por padrão (`display:none` no
HTML), revelado por `verificarAdmin()` em `admin.js` só se o usuário for
Super-Admin.

### Identidade real do usuário logado
Todo o "Pedro Almeida"/"PA" hardcoded que existia em `index.html`
(sidebar, Configurações, saudação da Home) foi substituído por dado real
de `GET /auth/me`. `aplicarUsuarioNaInterface(usuario)`
(`workspace.js`), chamada bem cedo no `init()` de `app.js`, preenche:
saudação da Home (`Bom dia/Boa tarde/Boa noite, {primeiro nome}`),
rodapé da sidebar (avatar com iniciais + nome + e-mail), card de Perfil
em Configurações. Também expõe `window.USUARIO_ATUAL` globalmente, que
`chat.js::getUserInitials()` usa pro avatar das mensagens do usuário no
chat (substituiu a constante fixa `USER_INITIALS = 'PA'`).

`UsuarioAutenticado` só tem e-mail/nome/foto — os campos "Cargo" e
"Departamento" no card de Perfil mostram "Não informado" em vez de
inventar um valor (antes eram fixos: "Analista de Processos"/"TI").

### Migração de schema necessária
As mudanças em `ConversaDB` e `DocumentoConhecimentoDB` (acima) alteram
tabelas que já existiam — `Base.metadata.create_all()` (usado no seed e
em `promover_admin.py`) **não** cobre isso, só cria tabela que ainda não
existe. Por isso existe `backend/scripts/migrar_schema_v2.py`: recria só
`conversas` (sempre esteve vazia, nada se perde) e adiciona `criado_em`
em `documentos_conhecimento` via `ALTER TABLE` (sem apagar nada).

**Ordem de execução importa — já causou um bug real nesta rodada:** o
script lê `db/models_db.py` pra saber o formato novo. Se rodar **antes**
de substituir esse arquivo, ele recria `conversas` no formato **antigo**
de novo, e o servidor quebra (500) assim que sobe com o `models_db.py`
novo esperando colunas que não existem de verdade no banco. A ordem
certa é: **substituir todos os arquivos do backend primeiro → parar o
servidor → rodar o script → subir o servidor de novo.** O script é
idempotente, seguro rodar de novo quantas vezes precisar.

---

## 5.6 Hospedagem, deploy e como o frontend é servido

### Arquitetura atual: um único processo serve tudo
- O `uvicorn` serve **API + frontend na mesma porta/origem.** `main.py`
  monta `StaticFiles(directory="../frontend", html=True)` em `"/"`,
  **sempre como o último registro do app** (um mount em "/" captura
  qualquer caminho não reconhecido; se viesse antes, "roubaria" as rotas
  de API). A antiga rota `GET /` (JSON de status) virou `GET /health`.
- `frontend/js/api.js` usa `const API = ""` (caminho relativo): resolve
  sempre contra a origem de onde a página foi carregada — funciona local,
  na Render e em qualquer domínio futuro. (Antes era `http://127.0.0.1:8000`
  fixo, o que quebra em qualquer lugar que não seja a máquina do
  desenvolvedor: o navegador tentava falar com o `127.0.0.1` de quem está
  usando o site.)
- **Não existe mais servidor separado de frontend.** Rodar
  `python -m http.server` na pasta `frontend` junto com o `uvicorn` faz as
  chamadas de API caírem num servidor de arquivos que devolve 404 para tudo
  (e no Windows os dois conseguem "dividir" a mesma porta, IPv4 vs IPv6,
  mascarando o erro).
- No startup, `main.py` chama `Base.metadata.create_all()` (só cria tabela
  que falta; nunca altera nem apaga existente — seguro sempre) e, se
  `INITIAL_ADMIN_EMAIL` estiver definido, garante esse e-mail em
  `administradores` (idempotente). Resolve o "ovo e galinha" de precisar já
  ser admin para promover alguém, e é essencial em ambiente de disco
  temporário. Pode ser desligado deixando a variável em branco.

### Teste na Render (plano Free) — validado, serviu de aprendizado
- Repositório GitHub privado `tirjalimentos/rj-hub` (pasta local
  `D:\RJ HUB\rjhub-v2\`; o `.gitignore` já exclui `.env`, `*.db`, `venv/`).
- Configuração: Root Directory `backend`; Build `pip install -r
  requirements.txt`; Start `uvicorn main:app --host 0.0.0.0 --port $PORT`
  (a porta vem da variável `$PORT`, não é fixa). URL de teste:
  `https://rj-hub-1.onrender.com`. A Render usa Python 3.14 por padrão
  (local: 3.12) — funcionou sem ajustes.
- Variáveis de ambiente (no painel, não em arquivo): `ANTHROPIC_API_KEY`,
  `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET_KEY`,
  `SESSION_SECRET_KEY`, `FRONTEND_URL`, `INITIAL_ADMIN_EMAIL` (opcional:
  `GOOGLE_ALLOWED_DOMAIN=rjalimentos.com.br`).
- O auto-deploy por `git push` às vezes não disparou: sempre conferir no log
  a linha `Checking out commit <hash>` e, se necessário, usar Manual Deploy
  → Deploy latest commit. Um log só com "Shutting down → Running uvicorn"
  é o serviço acordando, NÃO um deploy novo.
- No plano Free o serviço dorme e o disco é temporário: o banco SQLite
  nasce vazio a cada restart (tabelas recriadas, mas sem especialistas nem
  documentos — recriar pelo painel). **Isso é efeito só do plano Free.**
  Todas as correções de código acima (URL relativa, StaticFiles, chaves
  fortes, FRONTEND_URL, create_all, INITIAL_ADMIN_EMAIL) valem para
  qualquer hospedagem e não precisam ser desfeitas.

### Decisão: produção na Locaweb (VPS Linux)
- O plano de hospedagem que a RJ já tem na Locaweb (sites ilimitados,
  MySQL/PostgreSQL, e-mail; pilha LAMP, sem root) **não roda o backend**
  (precisa de processo Python persistente). Serve para o **domínio** (ex:
  `hub.rjalimentos.com.br`, via DNS) e já inclui 3 bancos PostgreSQL.
- Produto escolhido: **VPS Linux (Ubuntu)**. Opções avaliadas, ambas com 2
  vCPU: 2 GB RAM / 60 GB SSD (R$ 382,80/ano ≈ R$ 31,90/mês) e 4 GB RAM /
  70 GB SSD (R$ 742,80/ano ≈ R$ 61,90/mês). Recomendação: **4 GB** (meta de
  30 usuários simultâneos; evita upgrade com reboot depois). Disco não é
  fator (projeto < 1 GB hoje). Valor/escolha final a alinhar com o diretor.
- Por que Locaweb e não Render: custo (Render com RAM equivalente: Standard
  ≈ US$ 25 e Pro ≈ US$ 85 por mês), já são clientes, suporte em português
  24/7, cobrança em Real, dado no Brasil. Contra: a manutenção do servidor
  passa a ser nossa.
- Windows Server 2012 R2 da empresa: **descartado para produção** (fim do
  suporte ESU em 13/10/2026; sem patches de segurança depois disso).
- A configurar no VPS: Ubuntu, Nginx como proxy reverso + HTTPS (Let's
  Encrypt), `systemd` mantendo o `uvicorn` de pé, deploy via `git pull`,
  firewall, atualizações de segurança automáticas, backup do `rjhub.db`.
  Confirmar com o suporte se o VPS com cPanel suporta app Python/ASGI
  (poderia simplificar).
- **Pendência marcada para a migração de produção:** em
  `backend/db/database.py`, habilitar SQLite em modo WAL + `busy_timeout`
  (30 pessoas gravando conversas ao mesmo tempo podem gerar "database is
  locked"). A pessoa pediu para ser lembrada disso nesse momento.

---

## 5.7 Tema visual: Padrão / Escuro / Sistema

- Escolha na aba **Configurações → Aparência** (`.theme-opt`, com
  `data-theme="padrao|escuro|sistema"`). Guardada em `localStorage`
  (`rjhub_tema`) — é preferência do navegador/dispositivo, não da conta.
- `ui.js`: `aplicarTema()` resolve a preferência e seta/remove
  `data-theme="escuro"` no `<html>`. "Sistema" decide na hora via
  `matchMedia('(prefers-color-scheme: dark)')` e reage se o SO mudar; Padrão
  e Escuro escolhidos manualmente ignoram o SO. Um script inline no `<head>`
  do `index.html` aplica o tema salvo antes do CSS, evitando "piscar".
- CSS: `:root` = **Padrão**, idêntico ao visual original (identidade
  vinho/dourado — não alterar sem pedido). `[data-theme="escuro"]` redefine
  as variáveis e traz poucos ajustes pontuais para cores hex fixas (header
  translúcido, fundo do chat, ícones, avatar do usuário, botão "danger").
  A sidebar já era escura por design e não muda entre temas.
- **Regra para componentes novos:** fundo de card/painel = `var(--surface)`,
  NUNCA `var(--white)` (que é só texto/ícone branco sobre fundo colorido e
  fica igual nos dois temas). Evitar cores hex fixas; se inevitável, criar o
  override no bloco `[data-theme="escuro"]`.
- Estado: primeiro passe feito sem ver o resultado renderizado (as cores
  escuras são estimativa) — esperar feedback visual da pessoa e ajustar.

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
JWT_SECRET_KEY=<token_urlsafe(32)>
SESSION_SECRET_KEY=<outro token_urlsafe(32)>
FRONTEND_URL=http://localhost:8000
INITIAL_ADMIN_EMAIL=seu.email@rjalimentos.com.br
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

**Subir (um único processo, uma única janela de CMD):**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```
O app completo (frontend + API) fica em `http://localhost:8000/`; docs
automáticas em `/docs`. **Não rodar servidor separado do frontend** (ver
seção 5.6). Acessar sempre pelo mesmo endereço cadastrado no Google Console
(`localhost` ≠ `127.0.0.1`) e com `FRONTEND_URL` igual a ele no `.env`.
Ao subir, o app cria as tabelas que faltam e garante `INITIAL_ADMIN_EMAIL`
como Super-Admin.

**Como validar que tudo está integrado:** faça login com um e-mail
corporativo. Com o backend rodando, o Console (F12) deve mostrar os
especialistas/workspaces carregados da API (não do mock), sem avisos de
`⚠️ API indisponível`. Testando o chat, a resposta deve vir baseada nos
documentos reais do especialista (não um template genérico) — se aparecer
algo genérico demais e descolado da pergunta, suspeitar que o `chat.js`
está caindo em algum caminho de simulação antigo, não na API real.

---

## 7. Estado atual (checkpoint)

### ✅ Sessão mais recente (set–nov/2026)
- **Respostas do especialista em Markdown** (títulos, listas, negrito) —
  prompt + `renderMarkdown` + CSS (seção 5.2). Testado com um caso real
  (cadastro de RCA na rotina 517): ficou legível e organizado.
- **Deploy de teste na Render validado** (seção 5.6): GitHub → auto-deploy,
  login Google e chat funcionando na URL pública. Bugs encontrados e
  corrigidos no caminho: URL da API fixa em `127.0.0.1`; frontend não era
  servido pelo backend; `FRONTEND_URL` com padrão errado (login redirecionava
  para o localhost de quem logava); chaves JWT/sessão curtas; banco sem
  tabelas (`create_all`); ninguém admin no banco novo (`INITIAL_ADMIN_EMAIL`).
- **Rodar local de novo com servidor único** (porta 8000, sem `http.server`) e
  login local restaurado depois de cadastrar `http://localhost:8000/auth/callback`
  no Google Console (`redirect_uri_mismatch`).
- **Tema Padrão / Escuro / Sistema** na aba Configurações (seção 5.7) —
  funcionando; ajuste fino de cores do escuro pode ser necessário.
- **Decisão de hospedagem tomada: Locaweb VPS Linux** (seção 5.6); falta
  contratar/configurar e fechar 2 GB vs 4 GB com o diretor.
- **Direções novas pedidas** (ainda não desenhadas/implementadas): perfis
  Admin / Supervisor / Usuário; plataforma editável pelo Super-Admin dentro
  dela mesma (sem mexer no código); conexão com o DataLake (ver seção 8).
- Nenhuma apresentação à diretoria marcada — sem prazo.

### Histórico anterior (ago/2026)

### ✅ RESOLVIDO — painel de Super-Admin não abria nenhuma aba
Sintoma original: logado como Super-Admin (`pedro.santos@rjalimentos.com.br`),
clicar em "Super-Admin" e depois em qualquer uma das 5 abas não abria
nada, nenhuma informação aparecia. Logado como usuário comum
(`bruno.santos@rjalimentos.com.br`), tudo funcionava normalmente.

**Causa raiz confirmada via log do Console (F12):** `buscarCategoriasBiblioteca`
tinha sumido do `api.js` do usuário (mesma função já corrigida numa
sessão anterior, aparentemente perdida de novo numa edição/cópia
manual). Como `app.js` chama essa função dentro de `await
carregarDadosIniciais()`, o `ReferenceError` interrompia a execução
**antes** de `initAdminEvents()` conseguir registrar os cliques das
abas — por isso nada respondia, mesmo o painel parecendo carregado.

**Correção:** função reintroduzida em `api.js`, no mesmo padrão de
`buscarDocumentosRecentes` (mesmo tratamento de erro, mesma exigência de
Super-Admin). Confirmado pelo usuário: todas as 5 abas abrem normalmente
agora.

**2 bugs reais adicionais, encontrados e corrigidos durante essa mesma
investigação** (antes da causa raiz acima ser encontrada): (1)
`buscarDashboardStats`/`buscarDashboardBars` nunca tinham sido conectadas
no `app.js` reescrito (Dashboard sempre mostrava mock antigo) —
corrigido, `DASH_STATS`/`DASH_BARS` viraram `let` com fallback `_MOCK`
no padrão do resto do projeto; (2) ver bug seguinte, encontrado na
sequência.

### ✅ RESOLVIDO — especialista criado não aparecia no painel de Admin
Sintoma: especialista criado pela aba Especialistas era salvo de
verdade no backend (confirmado via `GET /admin/especialistas`), mas não
aparecia na própria aba Especialistas nem no checklist de vínculo da
aba Grupos, mesmo com hard refresh e novo login.

**Causa:** `admin.js` usava `SPECIALISTS` (lista filtrada por RBAC) em
vez de uma lista sem filtro em três lugares do painel — e como um
especialista recém-criado ainda não pertence a grupo nenhum, ele nunca
aparecia. Pior: como o checklist de vínculo da aba Grupos também lia a
lista filtrada, era impossível vinculá-lo por ali — um ciclo (precisa
de grupo pra aparecer, precisa aparecer pra ganhar um grupo).

**Correção:** nova variável `ADMIN_ESPECIALISTAS_TODOS` (sem filtro, via
`GET /admin/especialistas`), usada em todo o painel de Admin —
`SPECIALISTS` (RBAC filtrada) continua intocada pro resto da interface.
Ver seção 5.3, "Ponto de atenção", para o detalhe completo — importante
lembrar disso ao adicionar qualquer tela nova ao painel de Admin.
Confirmado pelo usuário: funcionando.

### ✅ Novas funcionalidades desta sessão: excluir especialista + exportar documentos
- **Excluir especialista** — bloqueia (não exclui em cascata, decisão
  deliberada) se houver documentos, vínculo com grupo, presença em
  workspace, ou conversas registradas; mensagem de erro específica por
  tipo de bloqueio.
- **Exportar documentos** — baixa um `.zip` com um `.txt` por documento
  do especialista, como backup manual (não apaga nada do banco). Serve
  de passo intermediário antes de limpar a Base de Conhecimento pra
  desbloquear a exclusão.

Detalhes técnicos completos (rotas, services, decisões de design) na
seção 5.3. Confirmado pelo usuário: funcionando.

---

- **Frontend:** todas as views implementadas e funcionando, view de chat
  integrada (não modal) conectada à IA real. Redesign visual (Parte B) —
  **CONCLUÍDO**: sidebar fixa escura (`#171718`) + topbar com breadcrumb e
  workspace-pill + área central, identidade vinho `#AB0F15`/dourado
  `#E7C311` aplicada em todas as views (Início, Especialistas, Biblioteca,
  Conversas, Dashboard, Configurações, Super-Admin).
- **Backend:** FastAPI com todos os recursos reais (especialistas,
  workspaces, biblioteca, conversas, dashboard, chat, admin, auth).
- **Banco de dados (SQLite + SQLAlchemy) — CONCLUÍDO**, incluindo as
  tabelas de RBAC/admin e o schema novo de `conversas`/`documentos_
  conhecimento` (ver seção 5.5 — migrado via `scripts/migrar_schema_v2.py`).
- **Motor de IA real (Anthropic/Claude) — CONCLUÍDO**, com tratamento de
  erro robusto (extended thinking, sobrecarga da API) e base de
  conhecimento real injetada no contexto.
- **Autenticação corporativa (SSO Google) — CONCLUÍDO**, incluindo
  identidade real do usuário aplicada em toda a interface (seção 5.5) —
  chega de nome/e-mail hardcoded.
- **Controle de acesso por grupo (RBAC) + painel de Super-Admin —
  CONCLUÍDO, com interface visual própria** (`frontend/js/admin.js`), 5
  abas: Grupos, Usuários, Base de Conhecimento, Especialistas,
  Administradores (ver seção 5.3). Promoção de novos admins via
  `backend/promover_admin.py` ou pela própria aba Administradores.
  Excluir especialista (bloqueia por dependência) e exportar documentos
  em `.zip` (backup) — **adicionados e testados nesta sessão**.
- **Conversas, Dashboard e Biblioteca com dado real — CONCLUÍDO** (ver
  seção 5.5): conversas gravadas de verdade a cada troca de mensagem no
  chat, Dashboard calculado com escopo por permissão (Admin vê tudo,
  usuário comum só o próprio uso), Biblioteca unificada com a Base de
  Conhecimento e restrita a Super-Admin.
- **Modelo de especialistas — reduzido deliberadamente** para 1
  especialista institucional no lançamento inicial (ver seção 1), com a
  arquitetura já pronta pra expandir — inclusive pelo próprio painel
  (aba Especialistas), sem precisar editar `seed.py`.
- **Fonte de dados — só documentos estáticos por enquanto.** Decisão
  consciente de não conectar direto ao Oracle/ERP por segurança de dados;
  Power BI é o caminho cogitado para dado dinâmico (empresa já tem
  licenciamento Pro/Premium) e, mais adiante, o **DataLake** da empresa
  (provavelmente via API própria, ainda sem confirmação) — nada disso
  implementado ainda; ver seção 8.
- **Hospedagem em servidor/nuvem — decidido: Locaweb VPS Linux** (teste
  prévio na Render concluído; ver seção 5.6 e seção 8).

---

## 8. Próximos passos (em ordem sugerida)

1. **Locaweb VPS (produção).** Fechar o plano com o diretor (2 GB vs 4 GB;
   recomendado 4 GB), contratar, configurar (Ubuntu, Nginx + HTTPS, systemd,
   firewall, atualizações automáticas, backup do `rjhub.db`), apontar o
   domínio (ex: `hub.rjalimentos.com.br`, DNS na Locaweb), cadastrar o novo
   redirect URI no Google Console, definir as variáveis de ambiente (com
   chaves NOVAS) e `FRONTEND_URL` = domínio final. Perguntar ao suporte se o
   VPS com cPanel suporta app Python/ASGI. Disco do VPS é persistente: o
   SQLite deixa de zerar.
2. **Antes de abrir para os usuários:** habilitar WAL + `busy_timeout` em
   `db/database.py` (pendência marcada, seção 5.6); setar
   `GOOGLE_ALLOWED_DOMAIN=rjalimentos.com.br`; recriar o(s) especialista(s) e
   documentos pelo painel (banco novo nasce vazio); adicionar o domínio de
   produção em `CORS_ORIGINS` se algo vier de outra origem (mesma origem não
   precisa).
3. **Perfis Admin / Supervisor / Usuário.** Hoje só existe Super-Admin vs
   usuário comum. Falta definir o que o Supervisor pode fazer (hipóteses:
   ver dashboard/conversas só do time; gerenciar documentos só da própria
   área, sem mexer em Grupos/Usuários/Administradores) e então modelar o
   papel no banco, seguindo a regra 11 (negar por padrão) e a camada da
   regra 9.
4. **Plataforma editável pelo Super-Admin** (sem mexer no código): ideia de
   uma aba "Configurações" no painel reunindo ajustes da plataforma (ex:
   tema padrão). Qualquer decisão nova deve deixar esse caminho aberto.
5. **DataLake e dado dinâmico.** Sem prazo. Esperar o time do DataLake
   concluir e então levantar: mecanismo de autenticação, se a API é acessível
   a partir do VPS (rede/VPN/whitelist), maturidade e documentação, formato
   de resposta, limites de chamadas, e quais dados o especialista precisa.
   Para Power BI: a API "Execute Queries" (JSON) funciona com licença Pro;
   exige app no Azure AD (service principal), tenant admin habilitar
   "Dataset Execute Queries REST API" e uso de service principals, com
   permissão Build+Read só no dataset necessário. Arquitetura recomendada:
   o modelo consulta sob demanda via *tool use* da Anthropic, em vez de
   despejar números no prompt (hoje o contexto é só documento estático).
6. **Definir o(s) próximo(s) especialista(s) de verdade** (área + documentos
   reais) e lembrar de vincular ao grupo certo (criar sozinho não libera
   acesso a ninguém).
7. **Polimento de UX, baixa prioridade:**
   - Ajustes finos do tema escuro conforme feedback visual.
   - Busca de verdade na topbar (hoje só leva pra Especialistas).
   - Feedback visual além de `alert()` no painel de Super-Admin (toasts).
   - `CONVERSATIONS_FAVORITAS` ainda é buscada em `app.js` mas não exibida
     em nenhuma view — remover a chamada ou trazer a seção de volta.
8. **PostgreSQL** só se houver múltiplas instâncias ou necessidade do
   DataLake (a Locaweb já inclui 3 bancos PostgreSQL no plano atual; a
   mudança de código é basicamente a `DATABASE_URL`).

Não pule etapas — cada uma dessas deve nascer seguindo exatamente os
mesmos padrões já estabelecidos nas seções 3, 5, 5.1, 5.2, 5.3, 5.4 e 5.5.

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
  automação além dos que já usa (`git add/commit/push`, `uvicorn`,
  `python -m db.seed`). O ambiente dela é Windows com CMD.
- Ao pedir que a pessoa rode o projeto local, lembre: **um único `uvicorn`
  em `localhost:8000`**, sem servidor separado de frontend (seção 5.6).
- Ao adicionar CSS, use `var(--surface)` para fundos de card/painel — nunca
  `var(--white)` (seção 5.7) — para não quebrar o tema escuro.
- Antes de dizer que um deploy novo "pegou", confira no log da hospedagem o
  hash do commit; auto-deploy às vezes não dispara.
- Erros de login Google: `redirect_uri_mismatch` → URI não cadastrado no
  Google Console; redirecionamento para endereço errado após logar →
  `FRONTEND_URL` (seção 5.4).
- Depois de qualquer mudança, oriente exatamente como testar (o que
  esperar no console do navegador, o que checar em `/docs`).
