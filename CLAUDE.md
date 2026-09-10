# RJ HUB — Contexto do Projeto

Leia este arquivo antes de qualquer alteração. Ele define as regras de
arquitetura do projeto. Em caso de dúvida sobre uma decisão, preserve a
arquitetura atual em vez de assumir.

## O que é o projeto

O RJ HUB é uma plataforma corporativa de Inteligência Artificial para a
RJ Alimentos. Não é um "ChatGPT genérico": é um HUB onde o usuário
conversa com **especialistas da empresa** (Comercial, Fiscal, Financeiro,
RH, PCP, Compras, Estoque, TI, e outros no futuro). Cada especialista
tem conhecimento, documentos, contexto e histórico próprios. O usuário
escolhe um workspace, escolhe um especialista, e conversa apenas com ele.

## Histórico — por que este projeto foi recomeçado

Uma versão anterior (feita com outra ferramenta de IA) acumulou
inconsistências: HTML sendo editado em uma pasta enquanto o JavaScript
correspondente era criado em outra, arquivos de protótipo confundidos
com o frontend oficial, e módulos JS vazios ou nunca conectados ao HTML.
Este projeto foi recomeçado do zero para eliminar essa dívida técnica
desde o início. **O visual (identidade vinho/dourado, sidebar, cards de
especialistas) foi reaproveitado** — só a base técnica foi reconstruída.

## Regras de arquitetura (sempre respeitar)

1. Nunca criar arquivos gigantes. Cada módulo tem uma responsabilidade.
2. Nunca misturar HTML/JS de protótipo ou teste com o código oficial.
   Se for prototipar algo, crie uma pasta separada tipo `sandbox/` e
   deixe explícito no nome que não é o projeto oficial.
3. Nunca colocar dados dentro da interface (HTML) nem regras de negócio
   dentro de `app.js` ou de rotas do backend.
4. Sempre modularizar responsabilidades — se um arquivo cresce demais
   ou passa a fazer mais de uma coisa, divida.
5. Antes de mudar uma decisão arquitetural, justifique por escrito
   (comentário ou mensagem) o motivo.
6. Entre duas soluções técnicas equivalentes, escolha a mais simples.
7. Evite dependências desnecessárias entre módulos.
8. Front e back evoluem em paralelo, mas o contrato entre eles é a API
   — o frontend nunca deve depender de detalhes internos do backend.

## Estrutura do projeto

```
rj-hub/
├── CLAUDE.md                 ← este arquivo
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── data.js           dados (mock hoje, API no futuro) — sem lógica
│       ├── ui.js              sidebar, navegação entre views, menu mobile
│       ├── workspace.js       seletor de workspace, saudação, home
│       ├── especialistas.js   listagem, busca, favoritos
│       ├── biblioteca.js      biblioteca de documentos
│       ├── conversas.js       histórico de conversas
│       ├── dashboard.js       indicadores e gráficos
│       ├── chat.js            modal de chat
│       ├── config.js          configurações (tema, idioma, workspace padrão)
│       ├── api.js             chamadas HTTP ao backend
│       └── app.js             só inicialização — chama os init()/render() dos outros módulos, nada de lógica
└── backend/
    ├── main.py                cria o app FastAPI e registra rotas — nada de lógica
    ├── core/
    │   └── config.py          configurações (CORS, nome do app etc.)
    ├── models/                schemas Pydantic — só estrutura de dados
    ├── services/               regra de negócio; hoje mocks, no futuro banco de dados
    └── api/routes/             endpoints HTTP; só recebem requisição e chamam o service
```

## Como rodar localmente

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
A API sobe em `http://127.0.0.1:8000`. Documentação automática em
`http://127.0.0.1:8000/docs`.

**Frontend:**
Basta servir a pasta `frontend/` com qualquer servidor estático (ex.:
extensão "Live Server" do VS Code, ou `python -m http.server` dentro da
pasta). Não abra o `index.html` direto com `file://` sem servidor, pois
o `fetch()` para a API pode ter problemas de CORS dependendo do navegador.

## Estado atual

- Frontend: todas as views (Início, Especialistas, Biblioteca, Conversas,
  Dashboard, Configurações) e o modal de chat estão implementados com
  dados mockados em `frontend/js/data.js`.
- Backend: só o endpoint `/especialistas` está implementado (mock,
  espelhando os dados do frontend), como prova de conceito da integração.

## Próximos passos (em ordem sugerida)

1. Implementar `/workspaces` no backend e consumir em `workspace.js`.
2. Implementar `/documentos` (biblioteca) e `/conversas`.
3. Decidir e configurar um banco de dados real (hoje os `services/` só
   retornam listas em memória).
4. Autenticação corporativa (SSO) antes de expor a API fora da rede local.
5. Só depois disso: motor de IA real por trás dos especialistas.

Não pule etapas — cada uma dessas deve ser modularizada como um novo
service + rota no backend, e um novo módulo (ou atualização pontual) no
frontend, seguindo os mesmos padrões já estabelecidos acima.
