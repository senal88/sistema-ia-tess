# Documentos TESS

Todo documento e planilha das skills sai dos dois motores da marca. O conteúdo é da skill; cor, fonte, grade e tabela vêm de `marca/tess.json`. Não escrever CSS, cor ou fonte à mão, e não inserir imagem de logotipo: a marca é o nome **TESS** composto em texto pelo próprio motor.

Os caminhos abaixo partem da raiz do plugin (`${CLAUDE_PLUGIN_ROOT}` no Claude Code; nos outros apps, duas pastas acima da pasta da skill).

## Documento (HTML A4 + DOCX, PDF opcional)

1. Montar a especificação JSON com os blocos do conteúdo.
2. Rodar:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tess_documento.py" especificacao.json --saida . --formatos html,docx
```

O DOCX precisa de `python-docx` (`pip install python-docx`). Sem ele, entregar o HTML, que imprime em PDF A4 direto do navegador. O formato `pdf` usa Chrome ou Chromium sem interface, quando existir na máquina.

### Campos

| Campo | Uso |
|---|---|
| `titulo` | Título da capa, curto (até ~60 caracteres) |
| `subtitulo` | A promessa do documento em uma frase |
| `sobrancelha` | Nome da entrega (ex.: "Diagnóstico financeiro") |
| `cliente`, `data` | Para quem e quando |
| `rotulo` | Classificação no rodapé (padrão: "Uso interno"; use "Confidencial" para cliente) |
| `blocos` | Lista de blocos, na ordem de leitura |

### Blocos

| `tipo` | Campos | Quando usar |
|---|---|---|
| `secao` | `titulo` | Abre uma seção numerada (01, 02…) |
| `paragrafo` | `texto` (aceita `**negrito**`) | Texto corrido, até ~5 linhas |
| `lista` | `itens` | Itens paralelos, sem ordem |
| `kpis` | `itens[]`: `rotulo`, `valor`, `tom`, `detalhe` | Até 4 números de abertura. `tom`: `leitura` (neutro), `referencia` (meta), `risco`, `ganho` |
| `tabela` | `colunas`, `linhas`, `total`, `alinhar` (`e`/`d`/`c`) | Dados comparáveis; sempre seguida de `fonte` |
| `destaque` | `titulo`, `texto`, `tom` (`nota`/`risco`/`ok`/`info`) | Uma mensagem que não pode passar batida |
| `passos` | `itens[]`: `titulo`, `texto`, `prazo` | Plano de ação com prazo |
| `checklist` | `itens[]`: `texto`, `feito` | Itens a conferir |
| `fonte` | `texto` | Fonte e período de tabela ou número |
| `quebra` | — | Nova página |

### Ordem recomendada

1. `secao` "Leitura em um minuto" + `paragrafo` + `kpis`
2. Seções de diagnóstico (tabela + fonte + destaque)
3. `secao` "Plano" + `passos`
4. `destaque` `nota` com o próximo passo com a TESS

Exemplo completo: `exemplos/diagnostico-financeiro.json`.

## Planilha (XLSX)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tess_planilha.py" especificacao.json --saida .
```

Precisa de `openpyxl`. Cada aba tem `colunas`, `formatos` (`texto`, `inteiro`, `moeda`, `percentual`, `decimal`, `data`), `linhas` e, se quiser, `total`, `editaveis` (colunas de entrada, em destaque dourado), `nomes` (intervalos nomeados para fórmulas legíveis) e `nota`. Fórmulas começam com `=` e usam a sintaxe em inglês do Excel (`SUM`, `IF`). As linhas de dados começam na linha 5.

Exemplo completo: `exemplos/plano-de-receita.json`.

## Checagem antes de entregar

- O título diz o resultado, não o assunto ("Margem caiu 6,6 pontos: 3 decisões", e não "Análise financeira").
- Todo número tem fonte e período, ou está marcado como estimativa.
- Nenhum trecho cita a conversa, a ferramenta ou o modelo de IA.
- Nenhuma marca além de TESS.
- O documento termina com passos com prazo e com o próximo passo.
