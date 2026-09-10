/* ================================================================
   RJ HUB — auth.js
   Autenticação via SSO Google (fluxo: backend redireciona pro
   Google, Google chama de volta o backend, backend redireciona pro
   frontend com o token no fragmento da URL: #token=...).

   Esse módulo só cuida do token (guardar, ler, limpar). Chamadas
   autenticadas de verdade (enviar o header Authorization) ficam em
   api.js, como todo o resto da comunicação com o backend.
   ================================================================ */

const AUTH_STORAGE_KEY = "rjhub_token";

// Chama isso uma vez, na inicialização do app (antes de qualquer
// chamada à API). Se a URL tiver #token=..., guarda e limpa a URL.
function initAuth(){
  const hash = window.location.hash;
  if (hash.startsWith("#token=")) {
    const token = decodeURIComponent(hash.replace("#token=", ""));
    localStorage.setItem(AUTH_STORAGE_KEY, token);
    // Remove o token da URL (não deve ficar visível/salvo no histórico).
    window.history.replaceState(null, "", window.location.pathname + window.location.search);
  }
}

function getToken(){
  return localStorage.getItem(AUTH_STORAGE_KEY);
}

function estaLogado(){
  return !!getToken();
}

// Redireciona o navegador pro fluxo de login do backend (que por sua
// vez redireciona pro Google). Chame isso no onClick do botão de login.
function iniciarLogin(){
  window.location.href = `${API}/auth/login`;
}

function logout(){
  localStorage.removeItem(AUTH_STORAGE_KEY);
  window.location.reload();
}
