# Relatório de Auditoria Técnica

**Data:** 29/10/2026 · **Versão:** 2026.08

## Integridade HTML
| Métrica | Valor |
|---|---|
| Arquivos auditados | 46 |
| Sem erros estruturais | 46 |
| Com erros | 0 |

**Critérios verificados:**
- Balanceamento de tags `<style>` / `</style>`
- Balanceamento de tags `<script>` / `</script>`
- Unicidade de `<head>` / `<body>`
- Links internos resolvem para arquivo existente
- Hash anchors correspondem a IDs existentes

## Links Internos
| Métrica | Valor |
|---|---|
| Links internos checados | 280 |
| Links quebrados | 0 |
| Hash anchors quebrados | 0 |

✅ Nenhum link interno quebrado.

✅ Nenhum hash anchor quebrado.

## Correções Aplicadas nesta Rodada
1. `</style>` órfão removido de 5 dashboards (master, PRO, PREMIUM, ENTERPRISE, educativo)
   — causava renderização de CSS como texto visível na página
2. CSS responsivo de header adicionado (breakpoint 860px) — mobile sem overflow
3. Botão "Entrar / Criar conta" encurtado para "🔑 Entrar" em telas pequenas
4. Link `educativo.html` inexistente → `dashboard-auxfarmacia-educativo.html` (2 arquivos)
5. 87 hash anchors normalizados para os IDs reais das abas (`#casos` → `#tabCasos`, etc.)
6. Botões de login de todos os dashboards apontam para `login.html` standalone
7. Todos os `<button onclick="showAuthModal(...)">` de header substituídos por links

## Conteúdo Clínico
| Métrica | Valor |
|---|---|
| Medicamentos no catálogo | 61 |
| Classes terapêuticas | 50 |
| Calculadoras clínicas | 9 |
| Abas com deep-linking | 12 |
| Endpoints REST | 38 |
| Tipos de ação de auditoria | 25+ |

## Aviso Médico
Presente e visível em todos os dashboards e builds. Não removível por configuração.
