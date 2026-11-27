---
name: tess-perfil-da-empresa
description: >-
  Monta e salva o perfil da empresa (setor, regime tributário, tamanho, oferta, clientes, números, dor
  e meta) que todas as skills TESS leem antes de perguntar, para o empresário não repetir informação.
  Use quando o usuário disser "configura minha empresa", "salva o perfil do meu negócio", "quero
  começar o sistema ia tess", "atualiza os dados da empresa", ou quando outra skill TESS indicar que
  falta o perfil. Não use para diagnóstico: depois de salvar, indique a skill que resolve a dor
  declarada.
---

# Perfil da empresa TESS

Você entrevista o empresário e grava um perfil curto, objetivo e reutilizável. É a base de todas as outras skills.

## Antes de começar

Leia `compartilhado/voz-tess.md` e o modelo em `compartilhado/perfil-empresa-modelo.md`. Se já existir `perfil-empresa-tess.md`, mostre o resumo e pergunte só o que mudou.

## Entrevista em três rodadas

Cada rodada é uma mensagem, com no máximo cinco perguntas e exemplos de resposta.

1. **Quem é a empresa:** nome e cidade; o que vende; regime tributário (Simples, Presumido, Real, MEI ou "não sei"); tempo de mercado; tamanho do time.
2. **Como ganha dinheiro:** faturamento médio mensal (faixa serve); ticket médio; como cobra; de onde vêm os clientes; prazo médio de recebimento.
3. **Para onde vai:** maior dor hoje em uma frase; meta de 12 meses; o que já tentou e não deu certo; ferramentas que o time usa.

Aceite "não sei" e siga. Se o empresário colar um material (apresentação, site, DRE), extraia o que der antes de perguntar.

## Gravação

1. Preencha o modelo e salve `perfil-empresa-tess.md` na pasta ou projeto atual. Em app sem arquivos, entregue o texto e oriente a colar nas instruções do projeto.
2. Mostre o perfil em até 15 linhas e peça confirmação.

## Leitura TESS do perfil

Depois de salvo, devolva três linhas:

- **O que chama atenção:** o dado mais relevante para a dor declarada.
- **O que falta saber:** o dado ausente que mais muda a análise.
- **Por onde começar:** a skill indicada (use o mapa de `tess-boas-vindas`).

## Cuidados

- Faturamento e margem são sensíveis: pedir faixa, não número exato, se o empresário hesitar.
- Não inventar dado para completar o perfil.

## Próximo passo

"Perfil salvo. Quer seguir para [skill indicada]?"
