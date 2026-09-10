/* ================================================================
   RJ HUB — data.js
   Camada de DADOS. Responsável apenas pelas informações usadas pela
   aplicação (especialistas, workspaces, biblioteca, conversas,
   dashboard). Nunca deve conter lógica de renderização ou de negócio.

   Hoje os dados são mocks locais. No futuro serão substituídos por
   chamadas reais à API FastAPI (/especialistas, /workspaces,
   /documentos, /conversas, /dashboard) — ver api.js.
   ================================================================ */

// ---------------- Mensagens motivacionais (Home) ----------------
const MOTIVATIONAL = [
  "Seu dia mais produtivo começa aqui.",
  "Tudo que você precisa, em um único lugar.",
  "Menos tempo procurando, mais tempo entregando.",
  "Organização é o primeiro passo da produtividade.",
];

// ---------------- Base de especialistas ----------------
// SPECIALISTS_MOCK é o fallback local, usado apenas se a API estiver
// indisponível no momento do carregamento (ver carregarDadosIniciais em app.js).
const SPECIALISTS_MOCK = [
  { id:'comercial',    nome:'Comercial',    icone:'📈', desc:'Vendas, metas e relacionamento com clientes.',  docs:128, proc:34, atualizado:'há 2 horas',  favorito:true,  status:'ok'     },
  { id:'compras',      nome:'Compras',      icone:'🛒', desc:'Cotações, fornecedores e pedidos de compra.',    docs:96,  proc:21, atualizado:'há 5 horas',  favorito:false, status:'ok'     },
  { id:'financeiro',   nome:'Financeiro',   icone:'💰', desc:'Fluxo de caixa, contas a pagar e receber.',       docs:210, proc:47, atualizado:'há 1 hora',   favorito:true,  status:'ok'     },
  { id:'fiscal',       nome:'Fiscal',       icone:'⚖',  desc:'Tributos, obrigações e legislação fiscal.',       docs:174, proc:38, atualizado:'há 3 horas',  favorito:true,  status:'review' },
  { id:'pricing',      nome:'Pricing',      icone:'📊', desc:'Formação de preço e análise de margens.',         docs:64,  proc:15, atualizado:'ontem',       favorito:false, status:'ok'     },
  { id:'contabilidade',nome:'Contabilidade',icone:'📑', desc:'Lançamentos contábeis e demonstrações.',          docs:189, proc:41, atualizado:'há 6 horas',  favorito:false, status:'review' },
  { id:'ti',           nome:'TI',           icone:'🖥', desc:'Suporte técnico, sistemas e infraestrutura.',     docs:142, proc:29, atualizado:'há 30 min',   favorito:true,  status:'ok'     },
  { id:'producao',     nome:'Produção',     icone:'🏭', desc:'Processos produtivos e controle de qualidade.',   docs:118, proc:33, atualizado:'há 4 horas',  favorito:false, status:'ok'     },
  { id:'logistica',    nome:'Logística',    icone:'🚚', desc:'Transporte, entregas e roteirização.',            docs:87,  proc:22, atualizado:'há 8 horas',  favorito:false, status:'review' },
  { id:'diretoria',    nome:'Diretoria',    icone:'👔', desc:'Indicadores estratégicos e governança.',          docs:41,  proc:9,  atualizado:'ontem',       favorito:false, status:'ok'     },
  { id:'rh',           nome:'RH',           icone:'👥', desc:'Admissão, benefícios e políticas internas.',      docs:103, proc:26, atualizado:'há 12 horas', favorito:false, status:'ok'     },
  { id:'estoque',      nome:'Estoque',      icone:'📦', desc:'Inventário, movimentações e reposição.',          docs:76,  proc:18, atualizado:'há 7 horas',  favorito:false, status:'ok'     },
];

// SPECIALISTS é a lista efetivamente usada pela interface. Começa como
// cópia do mock e é substituída pelos dados reais da API assim que
// carregarDadosIniciais() (em app.js) terminar — os módulos de
// renderização sempre leem esta variável, nunca o SPECIALISTS_MOCK.
let SPECIALISTS = SPECIALISTS_MOCK.slice();

// ---------------- Workspaces ----------------
// WORKSPACES_MOCK é o fallback local, usado apenas se a API estiver
// indisponível no momento do carregamento (ver carregarDadosIniciais em app.js).
const WORKSPACES_MOCK = [
  { id:'geral',      nome:'Geral',      icone:'🏢', membros:SPECIALISTS.map(s=>s.id) },
  { id:'comercial',  nome:'Comercial',  icone:'📈', membros:['comercial','pricing','logistica','estoque'] },
  { id:'financeiro', nome:'Financeiro', icone:'💰', membros:['financeiro','fiscal','contabilidade','pricing'] },
  { id:'ti',         nome:'TI',         icone:'🖥', membros:['ti','producao','estoque','logistica'] },
  { id:'rh',         nome:'RH',         icone:'👥', membros:['rh','diretoria','contabilidade','ti'] },
];

// WORKSPACES é a lista efetivamente usada pela interface — mesmo padrão de SPECIALISTS.
let WORKSPACES = WORKSPACES_MOCK.slice();

// Workspace atualmente selecionado (estado inicial — mutado pelo workspace.js)
let currentWorkspace = WORKSPACES[0];

// ---------------- Sugestões e respostas do chat (mock — futura IA) ----------------
const SUGGESTIONS = {
  comercial:['Como está a meta do mês?', 'Relatório de vendas por região', 'Política de descontos vigente'],
  compras:['Fornecedores homologados', 'Status do último pedido', 'Prazo médio de entrega'],
  financeiro:['Fluxo de caixa da semana', 'Contas a pagar em aberto', 'Como solicitar reembolso'],
  fiscal:['Prazo da próxima obrigação', 'Regras de emissão de NF-e', 'Tabela de tributos vigente'],
  pricing:['Como calcular margem ideal', 'Tabela de preços atual', 'Política de reajuste'],
  contabilidade:['Fechamento do último mês', 'Como lançar uma despesa', 'Demonstrativo de resultados'],
  ti:['Abrir chamado de suporte', 'Status dos sistemas', 'Política de senhas'],
  producao:['Indicadores de qualidade', 'Cronograma da linha 2', 'Procedimento de parada'],
  logistica:['Rastrear entrega', 'Rotas disponíveis hoje', 'Custo médio de frete'],
  diretoria:['Indicadores do trimestre', 'Resumo executivo semanal', 'Metas estratégicas'],
  rh:['Solicitar férias', 'Política de benefícios', 'Como funciona o plano de carreira'],
  estoque:['Nível de estoque atual', 'Itens em ruptura', 'Última movimentação'],
};

const REPLIES = [
  "Encontrei {n} documentos relacionados a esse tema na base do departamento. Deseja que eu resuma os pontos principais?",
  "Esse processo está documentado no procedimento interno mais recente, atualizado {u}. Posso te mostrar o passo a passo.",
  "Já localizei referências sobre isso. Quer que eu gere um resumo executivo ou prefere o documento completo?",
];

const QA_REPLIES = {
  "Criar documento": "Certo! Vou preparar um rascunho de documento com base nos modelos deste departamento. Me diga o tema principal.",
  "Responder e-mail": "Posso montar uma resposta com base no histórico e nas políticas da área. Cole o e-mail recebido, se quiser.",
  "Analisar arquivo": "Envie o arquivo (PDF, planilha ou documento) e eu trago um resumo com os pontos mais relevantes.",
  "Consultar procedimento": "Qual procedimento você gostaria de consultar? Posso buscar pelo nome ou pelo processo relacionado.",
};

// ---------------- Biblioteca ----------------
// *_MOCK são os fallbacks locais, usados apenas se a API estiver
// indisponível no momento do carregamento (ver carregarDadosIniciais em app.js).
const LIB_CATS_MOCK = [
  { icon:'📋', nome:'POP', qtd:'42 documentos' },
  { icon:'📜', nome:'Políticas', qtd:'28 documentos' },
  { icon:'⚙️', nome:'Procedimentos', qtd:'65 documentos' },
  { icon:'📐', nome:'Normas', qtd:'19 documentos' },
  { icon:'📝', nome:'Formulários', qtd:'37 documentos' },
  { icon:'🎓', nome:'Treinamentos', qtd:'23 documentos' },
];

const LIB_RECENT_MOCK = [
  { icon:'📋', nome:'POP - Fechamento de Caixa', area:'Financeiro', tag:'POP', quando:'Atualizado há 2 dias' },
  { icon:'📜', nome:'Política de Descontos Comerciais', area:'Comercial', tag:'Política', quando:'Atualizado há 4 dias' },
  { icon:'⚙️', nome:'Procedimento de Parada de Linha', area:'Produção', tag:'Procedimento', quando:'Atualizado há 1 semana' },
  { icon:'📝', nome:'Formulário de Solicitação de Compras', area:'Compras', tag:'Formulário', quando:'Atualizado há 3 dias' },
  { icon:'🎓', nome:'Treinamento — Segurança de Dados', area:'TI', tag:'Treinamento', quando:'Atualizado há 5 dias' },
];

let LIB_CATS = LIB_CATS_MOCK.slice();
let LIB_RECENT = LIB_RECENT_MOCK.slice();

// ---------------- Conversas ----------------
const CONVERSATIONS_MOCK = [
  { icon:'💰', nome:'Financeiro', id:'financeiro', preview:'Qual o saldo de caixa consolidado desta semana?', quando:'09:20' },
  { icon:'⚖', nome:'Fiscal', id:'fiscal', preview:'Prazo da próxima obrigação acessória vence em breve.', quando:'Ontem' },
  { icon:'🖥', nome:'TI', id:'ti', preview:'Chamado #4521 foi resolvido pela equipe de suporte.', quando:'Ontem' },
  { icon:'📈', nome:'Comercial', id:'comercial', preview:'Relatório de vendas da região Sul enviado.', quando:'Seg' },
  { icon:'👥', nome:'RH', id:'rh', preview:'Sua solicitação de férias está em análise.', quando:'Seg' },
];

const CONVERSATIONS_FAVORITAS_MOCK = [
  'Financeiro — Fluxo de caixa',
  'Fiscal — Obrigações do mês',
  'TI — Chamados recorrentes',
];

let CONVERSATIONS = CONVERSATIONS_MOCK.slice();
let CONVERSATIONS_FAVORITAS = CONVERSATIONS_FAVORITAS_MOCK.slice();

// ---------------- Dashboard (mock — futura API) ----------------
const DASH_STATS = [
  { icon:'🤖', bg:'#FBEFEF',       num:12,      lab:'Especialistas ativos' },
  { icon:'📄', bg:'var(--gold-soft)', num:'1.428', lab:'Documentos indexados' },
  { icon:'📋', bg:'#E9F3EF',       num:333,     lab:'Procedimentos' },
  { icon:'💬', bg:'#EAF1FB',       num:212,     lab:'Conversas nesta semana' },
];

const DASH_BARS = [
  { nome:'Financeiro', val:82 }, { nome:'Comercial', val:76 }, { nome:'TI', val:64 },
  { nome:'Fiscal', val:58 }, { nome:'RH', val:41 }, { nome:'Compras', val:35 },
];
