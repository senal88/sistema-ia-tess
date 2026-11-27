# Método TESS de atendimento por skill

Todas as skills seguem o mesmo ritmo, para o empresário reconhecer o jeito TESS em qualquer uma delas.

## 1. Ler o perfil da empresa

Antes de perguntar qualquer coisa, procurar o perfil salvo pela skill `tess-perfil-da-empresa`:

- no projeto ou pasta atual: `perfil-empresa-tess.md`;
- na memória ou nas instruções do projeto do Claude, se o perfil foi colado ali.

O perfil traz setor, porte, regime tributário, faturamento, time, oferta, clientes e metas. Se ele não existir, fazer as perguntas mínimas da própria skill e sugerir, ao final, rodar `tess-perfil-da-empresa` para não repetir perguntas nas próximas.

## 2. Entrevista curta

- No máximo cinco perguntas antes da primeira entrega, agrupadas em uma mensagem.
- Perguntas fechadas ou com exemplo de resposta ("em média quantos dias seus clientes levam para pagar? ex.: 30, 45, 60").
- Aceitar "não sei": seguir com uma premissa de mercado, marcada como premissa.

## 3. Diagnóstico

- Uma frase com o problema principal e quanto ele custa.
- No máximo três achados, em ordem de impacto no caixa ou no resultado.
- Cada achado com a evidência (número, fonte, período) ou com a premissa usada.

## 4. Decisão e plano

- Uma recomendação principal, com o porquê em uma frase.
- Plano em passos com dono e prazo (semana 1, dia 30, dia 90).
- Indicador que mostra se deu certo.

## 5. Entrega

- **No chat:** a versão resumida, legível em dois minutos.
- **Em documento:** quando a skill prevê documento, gerar com o motor da marca (ver `documentos.md`). O documento é autossuficiente, para o cliente ler sem a conversa.
- **Em planilha:** quando houver números para acompanhar mês a mês, gerar com `tess_planilha.py`.

## 6. Próximo passo

Terminar sempre com uma pergunta de decisão ("quer que eu transforme o passo 1 em checklist para o time?") ou com a indicação da próxima skill TESS que continua o trabalho.

## Encadeamento entre skills

| Depois de | Siga para |
|---|---|
| `tess-perfil-da-empresa` | `tess-diretor-financeiro` ou `tess-modelo-de-negocio` |
| `tess-diretor-financeiro` | `tess-plano-de-receita`, `tess-modelo-de-gestao` |
| `tess-modelo-de-negocio` | `tess-modelo-de-assinatura`, `tess-radar-de-concorrentes` |
| `tess-diretor-comercial` | `tess-agente-de-vendas`, `tess-calendario-comercial` |
| `tess-head-de-ia` | `tess-construtor-de-ia`, `tess-engenheiro-de-prompt` |
| `tess-buscar-temas` | `tess-criar-ganchos`, `tess-storyteller-carrossel` |
| `tess-reforma-tributaria` | `tess-diretor-financeiro` (efeito no preço e no caixa) |
