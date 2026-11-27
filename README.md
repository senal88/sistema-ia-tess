# Sistema IA TESS

Skills da **TESS Contabilidade Estratégica** para o empresário usar no Claude (app, claude.ai, Cowork e Claude Code): 31 skills de gestão, finanças, comercial, gente, IA e marketing, com documentos e planilhas no padrão visual TESS.

Você pode instalar **uma skill**, **uma área** ou **o sistema completo**.

> O repositório é **privado**. A instalação funciona para quem tem acesso a `senal88/sistema-ia-tess` no GitHub: no Claude Code, pelas credenciais Git da máquina; no app do Claude, pela conta do GitHub conectada.

## Instalar no app do Claude

1. Abra **Customize › Plugins**.
2. **Add › Add marketplace › Add from a repository** e cole `senal88/sistema-ia-tess`.
3. Em **Plugins**, escolha:
   - **Sistema IA TESS (completo)** para as 31 skills; ou
   - uma área (**TESS Gestão e Finanças**, **TESS Comercial e Cliente**, **TESS Gente**, **TESS IA no Negócio**, **TESS Marketing e Conteúdo**); ou
   - uma skill avulsa (**TESS · Diretor Financeiro**, por exemplo).
4. Teste escrevendo: "testar o sistema ia tess".

## Instalar no Claude Code

```bash
claude plugin marketplace add senal88/sistema-ia-tess
```

Todas as 31 skills:

```bash
claude plugin install sistema-ia-tess@sistema-ia-tess
```

Uma área:

```bash
claude plugin install tess-gestao@sistema-ia-tess
```

Uma skill:

```bash
claude plugin install tess-diretor-financeiro@sistema-ia-tess
```

Instale o pacote completo **ou** as partes, não os dois: a mesma skill instalada duas vezes aparece em dobro.

## As 31 skills

| Área | Skills |
|---|---|
| **Gestão e Finanças** (`tess-gestao`) | `tess-boas-vindas`, `tess-perfil-da-empresa`, `tess-diretor-financeiro`, `tess-plano-de-receita`, `tess-modelo-de-gestao`, `tess-processos-chave`, `tess-reforma-tributaria`, `tess-modelo-de-negocio`, `tess-modelo-de-assinatura` |
| **Comercial e Cliente** (`tess-comercial`) | `tess-diretor-comercial`, `tess-agente-de-vendas`, `tess-calendario-comercial`, `tess-experiencia-do-cliente`, `tess-mecanismos-de-aquisicao`, `tess-radar-de-concorrentes`, `tess-raio-x-do-site` |
| **Gente** (`tess-gente`) | `tess-diretora-de-gente` |
| **IA no Negócio** (`tess-ia`) | `tess-head-de-ia`, `tess-servicos-com-ia`, `tess-negocio-eficiente-ia`, `tess-construtor-de-ia`, `tess-engenheiro-de-prompt`, `tess-agente-de-qualidade` |
| **Marketing e Conteúdo** (`tess-marketing`) | `tess-engenharia-de-marketing`, `tess-ferramenta-de-marketing`, `tess-marketing-educativo`, `tess-buscar-temas`, `tess-criar-ganchos`, `tess-storyteller-carrossel`, `tess-maquina-de-carrosseis`, `tess-videos-curtos` |

Comece por `tess-boas-vindas` ou `tess-perfil-da-empresa`: o perfil salvo evita repetir perguntas em todas as outras.

## Documentos no padrão TESS

As skills geram documentos (HTML A4 pronto para PDF e DOCX) e planilhas (XLSX) com os motores em `scripts/`. Cor, fonte, escala e tabela vêm de `marca/tess.json`: tinta e dourado da folha, Poppins. A marca é o nome **TESS** composto em texto; o repositório não tem imagem de logotipo. Referência em [`compartilhado/documentos.md`](compartilhado/documentos.md); exemplos em [`exemplos/`](exemplos/).

```bash
python3 scripts/tess_documento.py exemplos/diagnostico-financeiro.json --saida _saida --formatos html,docx,pdf
python3 scripts/tess_planilha.py exemplos/plano-de-receita.json --saida _saida
```

## Estrutura

```text
.claude-plugin/marketplace.json   gerado do catalogo.yaml (make marketplace)
catalogo.yaml                     dono da lista de skills, áreas e pacotes
skills/tess-*/SKILL.md            as 31 skills
compartilhado/                    voz, método, documentos e modelo de perfil (lidos por todas)
marca/                            tess.json + fontes, cópia do dono com sha256 em ORIGEM.json
scripts/                          motores de documento e planilha, gerador e validadores
exemplos/                         especificações de exemplo
tests/                            testes (make test)
```

## Publicar versão nova

1. Altere o conteúdo, rode `make marketplace` se mexeu no catálogo e `make ci`.
2. Suba o número em `VERSION` e rode `make marketplace`: sem mudar a versão, quem já instalou não recebe a atualização.
3. Commit e push em `main`.

## Licença

Conteúdo da TESS Contabilidade Estratégica; ver [LICENSE](LICENSE). Fontes Poppins e JetBrains Mono sob SIL Open Font License (`marca/fonts/OFL-*.txt`).
