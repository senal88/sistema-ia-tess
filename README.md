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

## Pacotes e skills

<!-- catalogo:inicio — gerado de catalogo.yaml por `make marketplace`; não editar -->

| Pacote | Instalar no Claude Code |
|---|---|
| **Sistema IA TESS (completo)** (`sistema-ia-tess`) | `/plugin install sistema-ia-tess --marketplace senal88/sistema-ia-tess` |
| **TESS Gestão e Finanças** (`tess-gestao`) | `/plugin install tess-gestao --marketplace senal88/sistema-ia-tess` |
| **TESS Comercial e Cliente** (`tess-comercial`) | `/plugin install tess-comercial --marketplace senal88/sistema-ia-tess` |
| **TESS Gente** (`tess-gente`) | `/plugin install tess-gente --marketplace senal88/sistema-ia-tess` |
| **TESS IA no Negócio** (`tess-ia`) | `/plugin install tess-ia --marketplace senal88/sistema-ia-tess` |
| **TESS Marketing e Conteúdo** (`tess-marketing`) | `/plugin install tess-marketing --marketplace senal88/sistema-ia-tess` |

### TESS Gestão e Finanças

| Skill | Instalar só esta skill |
|---|---|
| Boas-vindas TESS (`tess-boas-vindas`) | `/plugin install tess-boas-vindas --marketplace senal88/sistema-ia-tess` |
| Perfil da empresa (`tess-perfil-da-empresa`) | `/plugin install tess-perfil-da-empresa --marketplace senal88/sistema-ia-tess` |
| Diretor Financeiro (`tess-diretor-financeiro`) | `/plugin install tess-diretor-financeiro --marketplace senal88/sistema-ia-tess` |
| Plano de Receita (`tess-plano-de-receita`) | `/plugin install tess-plano-de-receita --marketplace senal88/sistema-ia-tess` |
| Modelo de Gestão (`tess-modelo-de-gestao`) | `/plugin install tess-modelo-de-gestao --marketplace senal88/sistema-ia-tess` |
| Processos-Chave (`tess-processos-chave`) | `/plugin install tess-processos-chave --marketplace senal88/sistema-ia-tess` |
| Reforma Tributária (`tess-reforma-tributaria`) | `/plugin install tess-reforma-tributaria --marketplace senal88/sistema-ia-tess` |
| Modelo de Negócio (`tess-modelo-de-negocio`) | `/plugin install tess-modelo-de-negocio --marketplace senal88/sistema-ia-tess` |
| Modelo de Assinatura (`tess-modelo-de-assinatura`) | `/plugin install tess-modelo-de-assinatura --marketplace senal88/sistema-ia-tess` |

### TESS Comercial e Cliente

| Skill | Instalar só esta skill |
|---|---|
| Diretor Comercial (`tess-diretor-comercial`) | `/plugin install tess-diretor-comercial --marketplace senal88/sistema-ia-tess` |
| Agente de Vendas (`tess-agente-de-vendas`) | `/plugin install tess-agente-de-vendas --marketplace senal88/sistema-ia-tess` |
| Calendário Comercial (`tess-calendario-comercial`) | `/plugin install tess-calendario-comercial --marketplace senal88/sistema-ia-tess` |
| Experiência do Cliente (`tess-experiencia-do-cliente`) | `/plugin install tess-experiencia-do-cliente --marketplace senal88/sistema-ia-tess` |
| Mecanismos de Aquisição (`tess-mecanismos-de-aquisicao`) | `/plugin install tess-mecanismos-de-aquisicao --marketplace senal88/sistema-ia-tess` |
| Radar de Concorrentes (`tess-radar-de-concorrentes`) | `/plugin install tess-radar-de-concorrentes --marketplace senal88/sistema-ia-tess` |
| Raio-X do Site (`tess-raio-x-do-site`) | `/plugin install tess-raio-x-do-site --marketplace senal88/sistema-ia-tess` |

### TESS Gente

| Skill | Instalar só esta skill |
|---|---|
| Diretora de Gente (`tess-diretora-de-gente`) | `/plugin install tess-diretora-de-gente --marketplace senal88/sistema-ia-tess` |

### TESS IA no Negócio

| Skill | Instalar só esta skill |
|---|---|
| Head de IA (`tess-head-de-ia`) | `/plugin install tess-head-de-ia --marketplace senal88/sistema-ia-tess` |
| Serviços com IA (`tess-servicos-com-ia`) | `/plugin install tess-servicos-com-ia --marketplace senal88/sistema-ia-tess` |
| Negócio Eficiente com IA (`tess-negocio-eficiente-ia`) | `/plugin install tess-negocio-eficiente-ia --marketplace senal88/sistema-ia-tess` |
| Construtor de IA (`tess-construtor-de-ia`) | `/plugin install tess-construtor-de-ia --marketplace senal88/sistema-ia-tess` |
| Engenheiro de Prompt (`tess-engenheiro-de-prompt`) | `/plugin install tess-engenheiro-de-prompt --marketplace senal88/sistema-ia-tess` |
| Agente de Qualidade (`tess-agente-de-qualidade`) | `/plugin install tess-agente-de-qualidade --marketplace senal88/sistema-ia-tess` |

### TESS Marketing e Conteúdo

| Skill | Instalar só esta skill |
|---|---|
| Engenharia de Marketing (`tess-engenharia-de-marketing`) | `/plugin install tess-engenharia-de-marketing --marketplace senal88/sistema-ia-tess` |
| Ferramenta de Marketing (`tess-ferramenta-de-marketing`) | `/plugin install tess-ferramenta-de-marketing --marketplace senal88/sistema-ia-tess` |
| Marketing Educativo (`tess-marketing-educativo`) | `/plugin install tess-marketing-educativo --marketplace senal88/sistema-ia-tess` |
| Buscar Temas (`tess-buscar-temas`) | `/plugin install tess-buscar-temas --marketplace senal88/sistema-ia-tess` |
| Criar Ganchos (`tess-criar-ganchos`) | `/plugin install tess-criar-ganchos --marketplace senal88/sistema-ia-tess` |
| Storyteller de Carrossel (`tess-storyteller-carrossel`) | `/plugin install tess-storyteller-carrossel --marketplace senal88/sistema-ia-tess` |
| Máquina de Carrosséis (`tess-maquina-de-carrosseis`) | `/plugin install tess-maquina-de-carrosseis --marketplace senal88/sistema-ia-tess` |
| Vídeos Curtos (`tess-videos-curtos`) | `/plugin install tess-videos-curtos --marketplace senal88/sistema-ia-tess` |

<!-- catalogo:fim -->

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
