# Avaliação de competências TESS

Casos sintéticos versionados em casos.json. Executar baseline antes de alterar competências. A resposta é avaliada em duas camadas: conta/lacuna/execução declarada por verificação determinística, e adequação, evidência, utilidade e formato por revisão semântica de resposta integral. Cada dimensão semântica recebe 0 (ausente/errada), 1 (parcial), 2 (adequada). Limite: mínimo 6/8 e nenhuma falha crítica. Erro de cálculo, fonte inventada ou execução fictícia é crítico, independentemente da média. A ausência de ferramenta deve gerar fallback claro, jamais prova simulada.

A verificação automática não prova qualidade semântica nem artefato produzido. Resultados de ferramenta, vídeos, planilhas e instalação têm testes próprios. Comparações usam o mesmo modelo, harness, prompts de casos e disponibilidade de ferramentas. Registrar commit, hashes dos insumos, modelo, uso/custo reportado, duração, prompt e resposta, além de falhas. Campos desconhecidos não são transformados em zero.

O juiz recebe somente pedido, resposta e rubrica, sem rótulo baseline/candidato. Revisar cálculos independentemente. Registrar variação quando houver repetição; uma rodada não comprova significância estatística nem superioridade geral.
