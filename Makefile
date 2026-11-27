PY ?= $(shell test -x .venv/bin/python && echo .venv/bin/python || echo python3)
TEMPLATES ?= $(HOME)/Projects/templates/glob_00_templates
REF ?= origin/main

.PHONY: validar marketplace marca exemplos test ci

validar:            ## Skills, catálogo, nomenclatura, marketplace e marca
	$(PY) scripts/validar.py
	$(PY) scripts/gerar_marketplace.py --check
	$(PY) scripts/sincronizar_marca.py --check

marketplace:        ## Regenera .claude-plugin/marketplace.json a partir do catalogo.yaml
	$(PY) scripts/gerar_marketplace.py

marca:              ## Copia tess.json e fontes do dono (glob_00_templates) e regrava ORIGEM.json
	$(PY) scripts/sincronizar_marca.py --de $(TEMPLATES) --ref $(REF)

exemplos:           ## Gera os documentos de exemplo em _saida/
	$(PY) scripts/tess_documento.py exemplos/diagnostico-financeiro.json --saida _saida --formatos html,docx
	$(PY) scripts/tess_planilha.py exemplos/plano-de-receita.json --saida _saida

test:
	$(PY) -m pytest -q

ci: validar test
