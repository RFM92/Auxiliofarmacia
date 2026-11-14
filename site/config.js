/* ===================================================================
   AUXILIO FARMACIA - CONFIGURACAO DE DEPLOY
   ===================================================================
   Este arquivo e o unico ponto de alteracao para hospedar o site.

   COMO CONFIGURAR AO PUBLICAR:
   1. Copie este arquivo como `config.local.js` e edite a linha
      `window.AUXF_CONFIG = {...}` com a URL real da API.
   2. OU edite diretamente o objeto abaixo.

   A URL da API e lida pelo:
     - api-client.js   (todas as chamadas /api/*)
     - index.html      (login da tela de acesso unico)
     - checkout.html   (criacao do pagamento)
     - success.html    (verificacao do status)
   =================================================================== */

window.AUXF_CONFIG = {
  /* ---- URL do backend FastAPI ---- */
  /* Deixe VAZIO para usar a mesma origem (ideal quando front e back
     estao no mesmo dominio, ex: atras de um proxy /api).
     Exemplo de outro dominio:
       apiBase: 'https://auxfarmacia-api.onrender.com'
     Exemplo local (desenvolvimento):
       apiBase: 'http://localhost:8000'
  */
  apiBase: 'https://raphaelmenossi-maker-auxiliofarmacia-api.hf.space',

  /* ---- Nome exibido no rodape/assinaturas ---- */
  appName: 'Auxílio Farmácia',

  /* ---- Suporte ---- */
  supportEmail: 'suporte@auxfarmacia.com.br',

  /* ---- Versao (aparece no rodape e na tela inicial) ---- */
  version: '2026.08.1',
};
