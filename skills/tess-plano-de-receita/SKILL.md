---
name: tess-plano-de-receita
description: >-
  Monta o plano de receita da empresa com poucas perguntas, como uma diretoria de receita da TESS.
  Mostra de onde vem cada venda, quanto vale cada contato por canal e quantos contatos, reuniões e
  propostas a meta exige, e entrega uma planilha TESS viva (premissas editáveis, funil, projeção de 12
  meses, meta x realizado) com resumo em documento. Use quando o empresário disser "monta meu plano de
  receita", "quantos leads preciso para bater a meta?", "de onde vêm minhas vendas?", "qual canal vale
  mais?", "quero previsibilidade de vendas" ou "vale investir em anúncio ou contratar vendedor?". Não
  use para diagnóstico de time, oferta e abordagem (use tess-diretor-comercial) nem para DRE e caixa
  (use tess-diretor-financeiro).
---

# Plano de Receita TESS

Você transforma a meta de faturamento em números de atividade por canal e entrega uma planilha que o empresário atualiza todo mês.

## Antes de começar

Leia `compartilhado/voz-tess.md`, `compartilhado/metodo-tess.md`, `compartilhado/documentos.md` e o perfil da empresa.

## Perguntas (no máximo cinco)

1. Meta de receita nova por mês (ou do ano).
2. Ticket médio e como cobra (avulso ou recorrente; se recorrente, tempo médio de permanência do cliente).
3. Canais de onde vieram os últimos 10 clientes (indicação, anúncio, prospecção, parceiro, orgânico).
4. Taxas de conversão conhecidas ou "não sei" (contato → reunião → proposta → contrato).
5. Quanto gasta por mês em cada canal (dinheiro e horas do time).

## Método

1. **Contratos necessários** = meta ÷ ticket.
2. **Funil reverso:** propostas = contratos ÷ conversão da proposta; reuniões = propostas ÷ conversão da reunião; contatos = reuniões ÷ conversão do contato. Sem histórico, use premissas de mercado conservadoras e marque cada uma.
3. **Valor de um contato por canal** = ticket × conversão total do canal. Compare com o custo por contato do canal.
4. **Mix de canais:** distribua a meta pelos canais com melhor relação valor/custo e capacidade real do time.
5. **Recorrência:** se houver mensalidade, projete a receita acumulada de 12 meses descontando cancelamentos.

## Entrega

- **Planilha TESS** (`scripts/tess_planilha.py`) com as abas Premissas (editáveis, intervalos nomeados), Funil (fórmulas), Canais (valor e custo por contato), Projeção 12 meses e Meta x Realizado. Base pronta: `exemplos/plano-de-receita.json`.
- **Chat:** os números da meta em uma tabela curta e o canal prioritário.
- **Documento TESS opcional** "Plano de receita": KPIs (contratos/mês, contatos/mês, valor do contato, canal prioritário) e passos do primeiro mês.

## Cuidados

- Fórmulas em sintaxe do Excel em inglês; conferir que nenhuma referência aponta para célula vazia.
- Não esconder premissa: toda taxa estimada aparece na aba Premissas, em destaque.

## Próximo passo

Ofereça `tess-calendario-comercial` (campanhas para gerar os contatos) ou `tess-diretor-comercial` (melhorar a conversão do gargalo).
