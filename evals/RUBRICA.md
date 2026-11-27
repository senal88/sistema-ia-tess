# Avaliação de competências TESS

Casos sintéticos versionados em casos.json. Executar baseline antes de alterar competências. A resposta é avaliada em duas camadas: conta/lacuna/execução declarada por verificação determinística, e adequação, evidência, utilidade e formato por revisão semântica de resposta integral. Cada dimensão semântica recebe 0 (ausente/errada), 1 (parcial), 2 (adequada). Limite: mínimo 6/8 e nenhuma falha crítica. Erro de cálculo, fonte inventada ou execução fictícia é crítico, independentemente da média. A ausência de ferramenta deve gerar fallback claro, jamais prova simulada.

A verificação automática não prova qualidade semântica nem artefato produzido. Resultados de ferramenta, vídeos, planilhas e instalação têm testes próprios. Comparações usam o mesmo modelo, harness, prompts de casos e disponibilidade de ferramentas. Registrar commit, hashes dos insumos, modelo, uso/custo reportado, duração, prompt e resposta, além de falhas. Campos desconhecidos não são transformados em zero.

O juiz recebe somente pedido, resposta e rubrica, sem rótulo baseline/candidato. Revisar cálculos independentemente. Registrar variação quando houver repetição; uma rodada não comprova significância estatística nem superioridade geral.

## Limites da rodada inicial

A rodada exploratória anterior enviou normal/incompleto juntos e impôs respostas curtas sem ferramentas. Ela não serve para aceite de equivalência: há contaminação entre casos e ausência de prova de artefatos. A versão seguinte do runner separa as conversas e preserva diagnósticos. Toda saída conserva `revisao_semantica` como NOT_EXECUTED até revisão efetiva; retorno zero não é produzido para aprovação parcial. A guarda de ação fictícia é limitada: uma resposta textual com número errado e JSON correto ainda exige revisão integral.

Para qualificar uma personalização, acrescentar avaliações de ativação/encadeamento, entrevista longa, cada método/setor relevante, exceções, cálculos, documentos/planilhas e execução com ferramentas. Marca e design só são aceitos quando dados, fórmulas, referências, legibilidade e funcionalidades passam no mesmo conjunto antes/depois. Contagens, nomes e médias não substituem uma capacidade obrigatória ausente.
