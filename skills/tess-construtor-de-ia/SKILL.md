---
name: tess-construtor-de-ia
description: >-
  Constrói com o empresário, com método TESS, uma ferramenta de IA própria do negócio: skill, agente,
  projeto com instruções ou automação, a partir de uma tarefa recorrente. Entrevista sobre a tarefa,
  define entradas, passos, padrão de qualidade e saída, escreve a skill completa (SKILL.md com
  descrição de ativação) e testa com casos reais. Use quando o empresário disser "quero criar minha
  própria skill", "transforma essa tarefa em agente", "monta um assistente para o meu time", "quero um
  projeto do Claude com as instruções da empresa" ou "automatiza esse relatório". Não use para
  escolher quais tarefas automatizar (use tess-head-de-ia) nem para um agente de vendas (use
  tess-agente-de-vendas).
---

# Construtor de IA TESS

Você transforma uma tarefa que o empresário faz sempre do mesmo jeito em uma ferramenta de IA que o time usa sem ele.

## Antes de começar

Leia `compartilhado/voz-tess.md`, `compartilhado/metodo-tess.md` e o perfil da empresa.

## Perguntas (no máximo cinco)

1. Qual tarefa? Descreva a última vez que ela foi feita, passo a passo.
2. O que entra (documentos, dados, pedido) e o que sai (formato, para quem)?
3. Como você sabe que ficou bom? Dê um exemplo de resultado ótimo e um ruim.
4. Quem vai usar e em qual ferramenta (Claude app, projeto, Cowork, Code)?
5. Com que frequência e qual o volume?

## Escolha do formato

| Situação | Formato |
|---|---|
| Mesmo contexto, conversa livre | Projeto com instruções e arquivos |
| Passo a passo fixo, ativado por pedido | Skill |
| Rotina que lê sistemas e age | Skill + conectores ou automação agendada |
| Atendimento a terceiros | Agente com regras de passagem para humano |

## Construção de uma skill

1. **Nome** curto em minúsculas com hífen.
2. **Descrição de ativação:** o que faz, frases que o usuário diria, e quando não usar (até ~900 caracteres).
3. **Corpo:** papel, entradas, perguntas mínimas, passos numerados, padrão de qualidade (checklist), formato de saída, exemplos.
4. **Arquivos de apoio** (modelos, tabelas de referência) em `references/` quando passarem de uma tela.
5. **Teste:** 3 casos reais e 1 caso-limite; ajustar até os 4 passarem no checklist.
6. **Instalação:** como empacotar e onde instalar na ferramenta escolhida.

## Entrega

- A skill ou as instruções completas, prontas para instalar.
- **Documento TESS** "Ferramenta de IA: [nome]": objetivo, quem usa, entradas e saídas em tabela, passos, checklist de qualidade, registro dos testes.

## Cuidados

- Nada de senha, token ou dado pessoal dentro das instruções.
- Ferramenta que gera documento para cliente usa o padrão TESS (ver `compartilhado/documentos.md`).

## Próximo passo

Ofereça `tess-agente-de-qualidade` para criar o avaliador da nova ferramenta.
