# AGENTS.md — glob_00_sistema_ia_tess

Contrato do repositório `senal88/sistema-ia-tess`. Herda `~/SYSTEM.md` → `~/Projects/AGENTS.md`; em conflito, vence a fonte de maior autoridade.

```text
COMMIT_ROOT    = ~/Projects/sistema_ia_tess/glob_00_sistema_ia_tess
NO_COMMIT_ROOT = ~/Projects/sistema_ia_tess/glob_00_sistema_ia_tess__local   (rascunhos, saídas, evidências)
REMOTE         = git@github.com:senal88/sistema-ia-tess.git
```

## O que é

Marketplace de plugins do Claude com 31 skills **originais** da TESS Contabilidade Estratégica. Cada skill é instalável sozinha, por área ou no pacote completo `sistema-ia-tess`.

## Fonte única de cada fato

| Fato | Dono | Derivado |
|---|---|---|
| Lista de skills, áreas e pacotes | `catalogo.yaml` | `.claude-plugin/marketplace.json` (`make marketplace`) |
| Conteúdo de cada skill | `skills/<slug>/SKILL.md` | descrição curta no marketplace |
| Voz, método, padrão de documento | `compartilhado/*.md` | lido pelas skills, nunca copiado para dentro delas |
| Cor, fonte, escala, tabela | `glob_00_templates/_core/tokens/tess.json` | `marca/tess.json` (cópia com sha256 em `marca/ORIGEM.json`, `make marca`) |
| Versão | `VERSION` | `version` de cada plugin no marketplace |

## Regras

1. **Só TESS.** Nenhuma marca, nome, logotipo, cor ou texto de terceiros. Nada de imagem de logotipo: a marca é o nome TESS composto pelo motor. O validador bloqueia nomenclatura e paleta de terceiros.
2. **Conteúdo original.** Não copiar, adaptar ou traduzir skills, referências ou textos de outros pacotes de skills. Fonte externa entra só como inspiração conceitual de domínio público.
3. **Slug** `tess-<nome>` em minúsculas com hífen; `name` no frontmatter igual à pasta; `description` em bloco YAML (`>-`) com "Use quando" e "Não use".
4. **Estilo não se escreve à mão** em skill ou documento: usar `scripts/tess_documento.py` e `scripts/tess_planilha.py`.
5. Mudou catálogo → `make marketplace`. Mudou `tess.json` no dono → `make marca`. Toda entrega → `make ci` verde.
6. Release: subir `VERSION`, `make marketplace`, commit em Conventional Commits (minúsculas, ≤72 caracteres).

## Verificação

```bash
make ci
claude plugin validate .
```
