/* ================================================================
   RJ HUB — conversas.js
   Renderiza o histórico de conversas (view "Conversas"), a lista
   curta de "Conversas recentes" da sidebar, e agora também o card
   "Continue de onde parou" da Home (a mais recente das conversas).

   A coluna de "Conversas favoritas" que existia ao lado da lista
   foi removida nesta rodada de reskin, seguindo o protótipo
   aprovado — CONVERSATIONS_FAVORITAS/_MOCK continuam em data.js,
   só não há mais elemento na tela pra exibir isso.
   ================================================================ */

function renderConversationsList(){
  document.getElementById('convList').innerHTML = CONVERSATIONS.length
    ? CONVERSATIONS.map(c => `
        <div class="conversation" data-open="${c.id}" style="cursor:pointer">
          <div><h3>${c.nome}</h3><p>${c.quando} · ${c.preview}</p></div>
          <span style="color:var(--wine);font-weight:800">→</span>
        </div>
      `).join('')
    : `<div class="empty-note">Nenhuma conversa ainda.</div>`;
}

function renderConversations(){
  renderConversationsList();
}

// Card "Continue de onde parou" (Home) — mostra só a conversa mais
// recente. CONVERSATIONS já vem ordenada da mais recente pra mais
// antiga (mesma suposição que a lista da sidebar já fazia).
function renderHomeRecentConversation(){
  const container = document.getElementById('homeRecentConversation');
  if (!container) return;

  if (!CONVERSATIONS || CONVERSATIONS.length === 0) {
    container.innerHTML = `<div class="card"><div class="conversation"><div><h3>Nenhuma conversa ainda</h3><p>Abra um especialista pra começar</p></div></div></div>`;
    return;
  }

  const c = CONVERSATIONS[0];
  container.innerHTML = `
    <div class="card">
      <div class="conversation" data-open="${c.id}" style="cursor:pointer">
        <div><h3>${c.nome}</h3><p>${c.quando} · ${c.preview}</p></div>
        <span style="color:var(--wine);font-weight:800">→</span>
      </div>
    </div>
  `;
}

// Lista curta na sidebar (Parte B). Recebe as conversas já buscadas
// via buscarConversas(5) em app.js — não faz fetch aqui, só renderiza,
// pra manter o mesmo padrão de "app.js busca, *.js só desenha" usado
// no resto do projeto.
//
// Cada item usa data-open="${c.id}" — em models/conversa.py, "id" é
// o id do especialista relacionado à conversa (não um id próprio da
// conversa), então reaproveita o mesmo listener global de [data-open]
// que já abre o chat (chat.js). Clicar numa conversa recente abre o
// especialista dela, do mesmo jeito que clicar num card de
// especialista. Isso NÃO restaura o histórico de mensagens daquela
// conversa específica ainda (abre uma conversa nova com o
// especialista); restaurar a conversa exata é um passo futuro, fora
// do escopo desta rodada.
function renderSidebarRecentConversations(conversas){
  const container = document.getElementById('sidebarRecentConversations');
  if (!container) return;

  if (!conversas || conversas.length === 0) {
    container.innerHTML = `<div class="sb-recent-empty">Nenhuma conversa ainda</div>`;
    return;
  }

  container.innerHTML = conversas.map(c => `
    <button class="sb-recent-item" data-open="${c.id}" title="${c.nome}">
      ${c.nome}
    </button>
  `).join('');
}
