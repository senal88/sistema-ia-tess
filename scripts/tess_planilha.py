#!/usr/bin/env python3
"""Motor de planilhas do Sistema IA TESS.

Gera um .xlsx no padrão TESS a partir de uma especificação JSON. Cores, fonte e
regras de tabela vêm de `marca/tess.json`.

Uso:
    python3 scripts/tess_planilha.py especificacao.json --saida pasta/ [--nome arquivo]

Especificação:
    {
      "titulo": "Plano de receita 2027",
      "cliente": "Empresa X",
      "abas": [
        {
          "nome": "Premissas",
          "nota": "Altere só as células em destaque.",
          "colunas": ["Premissa", "Valor"],
          "formatos": ["texto", "moeda"],          # texto|inteiro|moeda|percentual|decimal|data
          "editaveis": [1],                         # colunas de entrada (fundo de destaque)
          "linhas": [["Ticket médio", 1500]],
          "total": ["Total", "=SUM(B5:B9)"],         # opcional; fórmulas começam com "="
          "larguras": [34, 16],                     # opcional, em caracteres
          "nomes": {"ticket": "B5"}                 # opcional: intervalos nomeados
        }
      ]
    }
As linhas começam na linha 5 (1 título, 2 subtítulo, 4 cabeçalho).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORMATOS = {
    "texto": "@",
    "inteiro": "#,##0",
    "moeda": '"R$" #,##0.00;[Red]-"R$" #,##0.00',
    "percentual": "0.0%",
    "decimal": "#,##0.00",
    "data": "dd/mm/yyyy",
}
LINHA_CABECALHO = 4


def carregar_marca() -> dict:
    return json.loads((RAIZ / "marca" / "tess.json").read_text(encoding="utf-8"))


def validar(spec: dict) -> None:
    if not spec.get("abas"):
        raise ValueError("a especificação precisa de ao menos uma aba em 'abas'")
    nomes = set()
    for a in spec["abas"]:
        n = a.get("nome", "")
        if not n or len(n) > 31 or re.search(r"[\[\]:*?/\\]", n):
            raise ValueError(f"nome de aba inválido: {n!r} (até 31 caracteres, sem []:*?/\\)")
        if n in nomes:
            raise ValueError(f"aba repetida: {n}")
        nomes.add(n)
        cols = a.get("colunas", [])
        for f in a.get("formatos", []):
            if f not in FORMATOS:
                raise ValueError(f"aba {n}: formato {f!r} inválido; use {sorted(FORMATOS)}")
        for i, linha in enumerate(a.get("linhas", []) + ([a["total"]] if a.get("total") else [])):
            if len(linha) != len(cols):
                raise ValueError(f"aba {n}, linha {i}: {len(linha)} células para {len(cols)} colunas")


def gerar(spec: dict, destino: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.workbook.defined_name import DefinedName

    validar(spec)
    m = carregar_marca()
    c, p, tab = m["colors"], m["palette"], m["table"]
    fam = m["font"]["family"]
    fino = Side(style="thin", color=c["border"])
    ouro = Side(style="medium", color=p["gold_leaf"]["hex"])

    wb = Workbook()
    wb.remove(wb.active)
    for a in spec["abas"]:
        ws = wb.create_sheet(a["nome"])
        ws.sheet_view.showGridLines = False
        cols, fmts = a["colunas"], a.get("formatos", ["texto"] * len(a["colunas"]))
        edit = set(a.get("editaveis", []))
        n = len(cols)

        ws["A1"] = spec.get("titulo", a["nome"])
        ws["A1"].font = Font(name=fam, size=16, bold=True, color=c["primary"])
        sub = " · ".join(x for x in (a["nome"], spec.get("cliente"), "TESS Contabilidade Estratégica") if x)
        ws["A2"] = sub
        ws["A2"].font = Font(name=fam, size=9, color=c["muted"])
        for col in range(1, n + 1):
            ws.cell(row=2, column=col).border = Border(bottom=ouro)
        if a.get("nota"):
            ws["A3"] = a["nota"]
            ws["A3"].font = Font(name=fam, size=9, italic=True, color=c["accent_text"])
        ws.row_dimensions[1].height = 26

        for i, col in enumerate(cols, start=1):
            ce = ws.cell(row=LINHA_CABECALHO, column=i, value=col)
            ce.font = Font(name=fam, size=10, bold=True, color=tab["header_fg"])
            ce.fill = PatternFill("solid", fgColor=tab["header_bg"])
            ce.alignment = Alignment(horizontal="left" if fmts[i - 1] == "texto" else "right", vertical="center", wrap_text=True)
        ws.row_dimensions[LINHA_CABECALHO].height = 24

        destaque = PatternFill("solid", fgColor=m["status"]["tratativa"]["bg"])
        for r, linha in enumerate(a.get("linhas", []), start=LINHA_CABECALHO + 1):
            for i, v in enumerate(linha, start=1):
                ce = ws.cell(row=r, column=i, value=v)
                ce.font = Font(name=fam, size=10, color=c["text"])
                ce.number_format = FORMATOS[fmts[i - 1]]
                ce.border = Border(bottom=fino)
                ce.alignment = Alignment(horizontal="left" if fmts[i - 1] == "texto" else "right", vertical="center")
                if (i - 1) in edit:
                    ce.fill = destaque
                    ce.font = Font(name=fam, size=10, bold=True, color=c["accent_text"])
        if a.get("total"):
            r = LINHA_CABECALHO + 1 + len(a.get("linhas", []))
            for i, v in enumerate(a["total"], start=1):
                ce = ws.cell(row=r, column=i, value=v)
                ce.font = Font(name=fam, size=10, bold=True, color=tab["total_fg"])
                ce.fill = PatternFill("solid", fgColor=tab["total_bg"])
                ce.number_format = FORMATOS[fmts[i - 1]]
                ce.alignment = Alignment(horizontal="left" if fmts[i - 1] == "texto" else "right")

        larg = a.get("larguras") or [max(12, min(48, max([len(str(cols[i]))] + [len(str(l[i])) for l in a.get("linhas", [])]) + 3)) for i in range(n)]
        for i, w in enumerate(larg, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = ws.cell(row=LINHA_CABECALHO + 1, column=1)
        ws.sheet_properties.tabColor = p["gold_leaf"]["hex"] if edit else c["primary"]
        for nome, ref in (a.get("nomes") or {}).items():
            col, lin = re.match(r"([A-Z]+)(\d+)", ref).groups()
            wb.defined_names[nome] = DefinedName(nome, attr_text=f"'{a['nome']}'!${col}${lin}")
        ws.print_options.horizontalCentered = True
        ws.page_setup.orientation = "landscape" if n > 5 else "portrait"
        ws.page_setup.fitToWidth = 1
        ws.oddFooter.left.text = "TESS · &A"
        ws.oddFooter.right.text = "&P / &N"
    wb.properties.creator = "TESS Contabilidade Estratégica"
    wb.properties.title = spec.get("titulo", "")
    wb.save(destino)


def slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "planilha"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("especificacao", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome")
    a = ap.parse_args(argv)
    spec = json.loads(a.especificacao.read_text(encoding="utf-8"))
    a.saida.mkdir(parents=True, exist_ok=True)
    destino = a.saida / f"{a.nome or slug(spec.get('titulo', 'planilha'))}.xlsx"
    gerar(spec, destino)
    print(destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
