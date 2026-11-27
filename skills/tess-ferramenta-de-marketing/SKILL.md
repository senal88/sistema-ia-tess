---
name: tess-ferramenta-de-marketing
description: >-
  Cria, com método TESS, uma ferramenta de marketing interativa que atrai e qualifica clientes:
  calculadora, simulador, diagnóstico rápido ou checklist com resultado, em página HTML única pronta
  para publicar, com captura de contato opcional e o resultado com a cara da marca do cliente. Use
  quando o empresário disser "quero uma calculadora no meu site", "cria um simulador para o meu
  cliente", "isca digital", "quiz de diagnóstico", "ferramenta para captar leads" ou "algo útil para
  atrair cliente". Não use para planejar o marketing inteiro (use tess-engenharia-de-marketing) nem
  para peças de redes sociais (use as skills de conteúdo TESS).
---

# Ferramenta de Marketing TESS

Você constrói uma ferramenta útil de verdade, que entrega um resultado ao visitante e abre a conversa de venda.

## Antes de começar

Leia `compartilhado/voz-tess.md`, `compartilhado/metodo-tess.md` e o perfil da empresa.

## Perguntas (no máximo cinco)

1. Que pergunta o cliente faz antes de comprar e que a ferramenta pode responder? (ex.: "quanto eu economizo?", "estou pronto para...?")
2. Que números ou respostas o visitante consegue informar em menos de 2 minutos?
3. Qual é a lógica ou fórmula do resultado? (se não houver, construa com o empresário)
4. O que acontece depois do resultado: WhatsApp, agendamento, formulário?
5. Cores e fonte da marca da empresa (ou site de referência).

## Construção

1. **Formato:** calculadora (entradas → número), diagnóstico (perguntas → nível + recomendações) ou checklist (itens → pontuação).
2. **Lógica:** escreva as fórmulas e faixas em linguagem simples e confirme com o empresário antes de codificar.
3. **Página:** HTML único (sem dependência externa obrigatória), responsivo, acessível (rótulos nos campos, contraste, navegação por teclado), carregamento rápido.
4. **Resultado:** número ou nível em destaque, o que significa, três recomendações e a chamada para o próximo passo.
5. **Captura:** opcional e depois do valor entregue; texto claro sobre o uso do contato.
6. **Teste:** 5 cenários com resultado esperado conferido.

## Entrega

- O arquivo HTML pronto e as instruções de publicação (site, página de link, hospedagem simples).
- Tabela com a lógica de cálculo e premissas para o empresário validar.

## Cuidados

- Resultado é estimativa: dizer isso na tela, com as premissas.
- Nada de rastreamento oculto; captura só com consentimento.
- A ferramenta leva a identidade visual da empresa do cliente.

## Próximo passo

Ofereça `tess-calendario-comercial` para lançar a ferramenta numa campanha.
