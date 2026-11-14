# Workflows

| Arquivo | O que faz |
|---|---|
| `ci.yml` | Auditoria automática a cada push: sintaxe JS, acessibilidade WCAG AA, links internos, sintaxe do backend |
| `release.yml` | Ao criar uma tag `v*`, monta o ZIP e publica na aba Releases |

> ⚠️ **Não há workflow de GitHub Pages aqui de propósito.**
> A documentação do GitHub diz que Pages não deve ser usado para e-commerce
> ou sites que facilitem transações comerciais — e o Auxílio Farmácia tem
> checkout com assinatura. O frontend é publicado no **Cloudflare Pages**
> (grátis e permitido). Veja `GUIA_DEPLOY.md`.
