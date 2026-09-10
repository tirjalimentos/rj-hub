/* ================================================================
   RJ HUB — chat.js
   Chat do RJ HUB: abrir, mensagens, sugestões rápidas, quick actions
   e o painel de contexto lateral (Parte B — dados reais).

   Conectado de verdade ao backend (enviarMensagemChat, em api.js).
   Mantém o histórico da conversa em memória (currentMessages) pra
   mandar junto a cada nova mensagem, já que o motor de IA precisa do
   contexto completo pra responder de forma coerente.

   O chat é uma view integrada na mesma casca (sidebar + header
   sempre visíveis) — showView('chat', ...) em vez de abrir/fechar
   modal, conforme a decisão da Parte B (mantida mesmo depois do
   protótipo de referência mais recente, que reintroduzia overlay).
   ================================================================ */

const chatBody = document.getElementById('chatBody');
const chatTitle = document.getElementById('chatTitle');
const chatIcon = document.getElementById('chatIcon');
const chatWsBadge = document.getElementById('chatWsBadge');
const quickSuggestions = document.getElementById('quickSuggestions');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatContextDocs = document.getElementById('chatContextDocs');

let currentSpecialist = null;
let currentMessages = []; // histórico da conversa atual, formato { role, content }
let currentDocumentosUsados = []; // documentos usados na última resposta (painel de contexto)

// Iniciais mostradas no avatar das mensagens do usuário. Antes era
// fixo ("PA"); agora lê o usuário logado de verdade, aplicado em
// window.USUARIO_ATUAL por aplicarUsuarioNaInterface() (workspace.js)
// assim que GET /auth/me responde. Fallback '?' cobre a janela entre
// abrir o chat e essa chamada terminar (raro, mas possível).
function getUserInitials(){
  const usuario = window.USUARIO_ATUAL;
  if (!usuario || !usuario.nome) return '?';
  return usuario.nome.split(' ').filter(Boolean).slice(0, 2).map(p => p[0].toUpperCase()).join('');
}

// Escapa texto antes de inserir via innerHTML (usado pra mensagens do
// usuário, que são texto puro, não HTML confiável — nunca passam por
// Markdown, ver renderMarkdown abaixo).
function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, m => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;'
  }[m]));
}

// Mensagens do especialista (bot) vêm em Markdown — o system_prompt em
// ia_service.py instrui o modelo a formatar assim (títulos, listas,
// negrito) quando fizer sentido pro conteúdo. Aqui converte pra HTML de
// verdade (marked) e sanitiza antes de inserir na tela (DOMPurify), já
// que HTML gerado por um modelo de IA não é uma fonte confiável o
// suficiente pra ir direto no innerHTML sem sanitização.
//
// Mensagens do usuário NUNCA passam por aqui — continuam sempre
// escapeHtml puro (ver addMessage). Não faz sentido interpretar
// Markdown do que a pessoa digitou, e isso reduz a superfície de risco
// pela metade.
function renderMarkdown(text){
  if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
    // CDN fora do ar, sem internet etc. — cai pro texto escapado puro.
    // Pior experiência (sem formatação), mas nunca quebra o chat.
    console.error('marked/DOMPurify não carregaram — exibindo texto sem formatação.');
    return escapeHtml(text);
  }
  return DOMPurify.sanitize(marked.parse(text));
}

function openChat(id){
  const s = SPECIALISTS.find(x => x.id === id);
  if(!s) return;
  currentSpecialist = s;
  currentMessages = [];
  currentDocumentosUsados = [];

  chatTitle.textContent = 'Especialista de ' + s.nome;
  chatIcon.textContent = s.icone;
  chatWsBadge.textContent = currentWorkspace.icone + ' Workspace ' + currentWorkspace.nome;

  chatBody.innerHTML = `
    <div class="msg bot">
      <div class="msg-avatar">${s.icone}</div>
      <div class="bubble">Olá 👋 Sou o especialista de <strong>${s.nome}</strong>. Tenho acesso a ${s.docs} documentos e ${s.proc} procedimentos desta área. Como posso te ajudar hoje?</div>
    </div>
  `;

  const suggestions = SUGGESTIONS[s.id] || [];
  quickSuggestions.innerHTML = suggestions.map(q => `<button class="qs-btn" data-q="${q}">${q}</button>`).join('');

  renderContextPanel([]);

  // Chat pertence à seção "Especialistas" na navegação — mantém esse
  // item destacado na sidebar, já que não tem entrada própria.
  const specialistsBtn = document.querySelector('.sb-item[data-view="specialists"]');
  showView('chat', specialistsBtn);
  setBreadcrumb('Especialista de ' + s.nome);

  chatInput.value = '';
  setTimeout(() => chatInput.focus(), 200);
}

function addMessage(text, who){
  const div = document.createElement('div');
  div.className = 'msg ' + who;

  const avatarContent = who === 'user' ? getUserInitials() : (currentSpecialist ? currentSpecialist.icone : '🤖');
  const bubbleHtml = who === 'bot' ? renderMarkdown(text) : escapeHtml(text);
  div.innerHTML = `
    <div class="msg-avatar">${avatarContent}</div>
    <div class="bubble">${bubbleHtml}</div>
  `;

  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function showTyping(){
  const div = document.createElement('div');
  div.className = 'typing'; div.id = 'typingIndicator';
  div.innerHTML = '<span></span><span></span><span></span>';
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function hideTyping(){
  const t = document.getElementById('typingIndicator');
  if(t) t.remove();
}

// Desenha o painel "Base consultada" com os documentos que o
// ia_service.py de fato usou pra montar a última resposta. Vazio no
// início da conversa e sempre que a última resposta não usou nenhum
// documento (pergunta fora da base de conhecimento).
function renderContextPanel(documentos){
  currentDocumentosUsados = documentos || [];
  if (!chatContextDocs) return;

  if (currentDocumentosUsados.length === 0) {
    chatContextDocs.innerHTML = `<p class="ctx-empty">Nenhum documento consultado ainda nesta conversa.</p>`;
    return;
  }

  chatContextDocs.innerHTML = `
    <p class="ctx-count">${currentDocumentosUsados.length} documento(s) relevante(s) encontrados para esta conversa.</p>
    <ul class="ctx-doc-list">
      ${currentDocumentosUsados.map(d => `<li>${d.titulo}</li>`).join('')}
    </ul>
  `;
}

// Envia a mensagem pro motor de IA real (via api.js) e mostra a
// resposta. Mantém currentMessages atualizado com os dois lados da
// conversa, pra manter contexto nas próximas mensagens, e atualiza o
// painel de contexto com os documentos usados nesta resposta.
async function sendReply(texto){
  if(!currentSpecialist) return;

  currentMessages.push({ role: 'user', content: texto });
  showTyping();

  const dados = await enviarMensagemChat(currentSpecialist.id, currentMessages);

  hideTyping();

  if(dados === null){
    addMessage('Não consegui falar com o especialista agora. Verifique se o backend está no ar e tente novamente.', 'bot');
    currentMessages.pop(); // remove a pergunta do histórico, já que não teve resposta
    return;
  }

  currentMessages.push({ role: 'assistant', content: dados.resposta });
  addMessage(dados.resposta, 'bot');
  renderContextPanel(dados.documentos_usados);
}

function handleSend(){
  const val = chatInput.value.trim();
  if(!val) return;
  addMessage(val, 'user');
  chatInput.value = '';
  sendReply(val);
}

// "Nova conversa" (sidebar) não sabe de antemão qual especialista o
// usuário quer — com só 1 especialista ativo hoje isso seria trivial,
// mas fixar o id aqui quebraria assim que o segundo especialista
// entrar. Por isso leva pra view de Especialistas pra escolher, em
// vez de abrir um chat direto.
function iniciarNovaConversa(){
  currentSpecialist = null;
  currentMessages = [];
  const specialistsBtn = document.querySelector('.sb-item[data-view="specialists"]');
  showView('specialists', specialistsBtn);
}

function initChat(){
  // Abertura do chat: delegado globalmente para qualquer [data-open],
  // funciona tanto para elementos estáticos quanto para cards
  // renderizados dinamicamente por especialistas.js/workspace.js, e
  // também para os itens de "Conversas recentes" da sidebar.
  document.addEventListener('click', (e) => {
    const openBtn = e.target.closest('[data-open]');
    if(openBtn){ openChat(openBtn.dataset.open); }
  });

  chatSendBtn.addEventListener('click', handleSend);
  chatInput.addEventListener('keydown', (e) => { if(e.key === 'Enter') handleSend(); });

  quickSuggestions.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-q]');
    if(btn){ addMessage(btn.dataset.q, 'user'); sendReply(btn.dataset.q); }
  });

  document.querySelectorAll('.qa-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if(!currentSpecialist) return;
      addMessage(btn.dataset.qa, 'user');
      sendReply(btn.dataset.qa);
    });
  });

  // Ações rápidas do painel de contexto — só fazem sentido quando já
  // existe pelo menos 1 documento usado na conversa.
  const resumirBtn = document.getElementById('ctxResumirBtn');
  const verDocsBtn = document.getElementById('ctxVerDocsBtn');

  if (resumirBtn) {
    resumirBtn.addEventListener('click', () => {
      if (!currentSpecialist || currentDocumentosUsados.length === 0) return;
      const pergunta = 'Resuma os documentos que você usou na sua última resposta.';
      addMessage(pergunta, 'user');
      sendReply(pergunta);
    });
  }

  if (verDocsBtn) {
    verDocsBtn.addEventListener('click', () => {
      if (!currentSpecialist || currentDocumentosUsados.length === 0) return;
      const titulos = currentDocumentosUsados.map(d => d.titulo).join(', ');
      addMessage(`Quais informações desses documentos você usou: ${titulos}?`, 'user');
      sendReply(`Explique com mais detalhe o que consta em: ${titulos}`);
    });
  }

  const novaConversaBtn = document.getElementById('newConversationBtn');
  if (novaConversaBtn) {
    novaConversaBtn.addEventListener('click', iniciarNovaConversa);
  }
}
