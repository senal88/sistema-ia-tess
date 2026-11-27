#!/usr/bin/env python3
"""Motor de documentos do Sistema IA TESS.

Lê uma especificação JSON (conteúdo) e gera o documento no padrão visual TESS
(tinta + dourado da folha, Poppins), em HTML A4 pronto para imprimir/PDF e em DOCX.
Cor, fonte, escala e grade vêm de `marca/tess.json`; nada de estilo fica fixo aqui.

Uso:
    python3 scripts/tess_documento.py especificacao.json --saida pasta/ [--formatos html,docx,pdf]

Especificação (resumo; referência completa em compartilhado/documentos.md):
    {
      "titulo": "...", "subtitulo": "...", "sobrancelha": "Diagnóstico",
      "cliente": "Empresa X", "data": "27/11/2026", "rotulo": "Confidencial",
      "blocos": [
        {"tipo": "secao", "titulo": "..."},
        {"tipo": "paragrafo", "texto": "..."},
        {"tipo": "lista", "itens": ["...", "..."]},
        {"tipo": "kpis", "itens": [{"rotulo": "...", "valor": "...", "tom": "leitura|referencia|risco|ganho"}]},
        {"tipo": "tabela", "colunas": [...], "linhas": [[...]], "total": [...], "alinhar": ["e","d"]},
        {"tipo": "destaque", "titulo": "...", "texto": "...", "tom": "nota|risco|ok|info"},
        {"tipo": "passos", "itens": [{"titulo": "...", "texto": "...", "prazo": "..."}]},
        {"tipo": "checklist", "itens": [{"texto": "...", "feito": false}]},
        {"tipo": "fonte", "texto": "..."},
        {"tipo": "quebra"}
      ]
    }
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = RAIZ / "marca"
TIPOS = {"secao", "paragrafo", "lista", "kpis", "tabela", "destaque", "passos", "checklist", "fonte", "quebra"}
TONS_KPI = {"leitura", "referencia", "risco", "ganho"}
TONS_DESTAQUE = {"nota", "risco", "ok", "info"}


class ErroEspecificacao(ValueError):
    pass


def carregar_marca() -> dict:
    return json.loads((MARCA / "tess.json").read_text(encoding="utf-8"))


def validar(spec: dict) -> None:
    if not isinstance(spec, dict) or not spec.get("titulo"):
        raise ErroEspecificacao("a especificação precisa de 'titulo'")
    for i, b in enumerate(spec.get("blocos", [])):
        t = b.get("tipo")
        if t not in TIPOS:
            raise ErroEspecificacao(f"bloco {i}: tipo '{t}' desconhecido; use {sorted(TIPOS)}")
        if t == "kpis":
            for k in b.get("itens", []):
                if k.get("tom", "leitura") not in TONS_KPI:
                    raise ErroEspecificacao(f"bloco {i}: tom de KPI '{k.get('tom')}' inválido")
        if t == "destaque" and b.get("tom", "nota") not in TONS_DESTAQUE:
            raise ErroEspecificacao(f"bloco {i}: tom de destaque '{b.get('tom')}' inválido")
        if t == "tabela":
            n = len(b.get("colunas", []))
            for j, linha in enumerate(b.get("linhas", []) + ([b["total"]] if b.get("total") else [])):
                if len(linha) != n:
                    raise ErroEspecificacao(f"bloco {i}, linha {j}: {len(linha)} células para {n} colunas")


# --------------------------------------------------------------------------- HTML

def _fonte_b64(nome: str) -> str:
    return base64.b64encode((MARCA / "fonts" / f"{nome}.woff2").read_bytes()).decode()


def _font_faces() -> str:
    faces = []
    for peso in (400, 500, 600, 700, 800):
        for sub, rng in (("latin", None), ("latin-ext", "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1E00-1EFF, U+20A0-20C0")):
            nome = f"poppins-{peso}-{sub}"
            if not (MARCA / "fonts" / f"{nome}.woff2").exists():
                continue
            ur = f"unicode-range:{rng};" if rng else ""
            faces.append(
                f"@font-face{{font-family:'Poppins';font-weight:{peso};font-style:normal;font-display:swap;{ur}"
                f"src:url(data:font/woff2;base64,{_fonte_b64(nome)}) format('woff2');}}"
            )
    for peso in (400, 500):
        nome = f"jetbrains-mono-{peso}-latin"
        if (MARCA / "fonts" / f"{nome}.woff2").exists():
            faces.append(
                f"@font-face{{font-family:'JetBrains Mono';font-weight:{peso};font-display:swap;"
                f"src:url(data:font/woff2;base64,{_fonte_b64(nome)}) format('woff2');}}"
            )
    return "\n".join(faces)


def css(m: dict, rotulo: str | None = None) -> str:
    c, p, tab, st = m["colors"], m["palette"], m["table"], m["status"]
    tp, g = m["type_scale_a4_pt"], m["grid_a4_mm"]
    f = m["font"]
    gold = p["gold_leaf"]["hex"]
    return f"""
{_font_faces()}
:root{{
  --ink:#{c['text']};--tinta:#{c['primary']};--capa:#{c['cover']};--ouro:#{gold};--ouro-texto:#{c['accent_text']};
  --muted:#{c['muted']};--linha:#{c['border']};--zebra:#{c['zebra']};--suave:#{c['subtle']};
  --risco:#{c['negative']};--sob-escuro:#{c['on_dark_muted']};--branco:#{c['white']};
  --ganho:#{p['sage']['hex']};
  --mx:{g['margin_x']}mm;--mt:{g['margin_top']}mm;--mb:{g['margin_bottom']}mm;
  --sans:'{f['family']}',{f['fallback']},sans-serif;--mono:'{f['mono']}',{f['mono_fallback']},monospace;
}}
@page{{size:A4;margin:var(--mt) var(--mx) var(--mb);
  @bottom-left{{content:"TESS  ·  {rotulo or m['footer']['confidential_label']}";font:500 {tp['micro']}pt var(--mono);color:var(--muted);letter-spacing:.12em;text-transform:uppercase}}
  @bottom-right{{content:counter(page);font:500 {tp['micro']}pt var(--mono);color:var(--muted)}}}}
@page capa{{margin:0;@bottom-left{{content:none}}@bottom-right{{content:none}}}}
*{{box-sizing:border-box}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{margin:0;background:#E9E7E1;font-family:var(--sans);color:var(--ink);font-size:{tp['body']}pt;line-height:1.55;
  font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}}
.folha{{width:210mm;min-height:297mm;margin:12mm auto;background:var(--branco);padding:var(--mt) var(--mx) var(--mb);
  box-shadow:0 1px 2px rgba(0,0,0,.06),0 12px 40px rgba(0,0,0,.08)}}
.capa{{page:capa;width:210mm;height:297mm;margin:12mm auto;background:var(--capa);color:var(--branco);position:relative;
  padding:28mm var(--mx) 22mm;display:flex;flex-direction:column;overflow:hidden;break-after:page}}
.capa::after{{content:"";position:absolute;right:-60mm;top:-40mm;width:170mm;height:170mm;border-radius:50%;
  border:.6pt solid var(--ouro);opacity:.55}}
.capa .marca{{font-weight:700;letter-spacing:.42em;font-size:13pt}}
.capa .marca small{{display:block;font:500 {tp['micro']}pt var(--mono);letter-spacing:.18em;color:var(--sob-escuro);margin-top:2.2mm;text-transform:uppercase}}
.capa .miolo{{margin-top:auto;max-width:150mm}}
.sobrancelha{{font:500 {tp['eyebrow']}pt var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--ouro);margin:0 0 5mm}}
.capa h1{{font-size:34pt;line-height:1.04;letter-spacing:-.03em;word-spacing:.1em;font-weight:800;margin:0}}
.capa .sub{{font-size:12pt;line-height:1.45;color:var(--sob-escuro);margin:6mm 0 0;max-width:135mm}}
.capa .fio{{width:24mm;height:0;border-top:1.2pt solid var(--ouro);margin:12mm 0 6mm}}
.capa .meta{{display:grid;grid-template-columns:repeat(3,auto);justify-content:start;gap:0 12mm;font-size:{tp['small']}pt}}
.capa .meta span{{display:block;font:500 {tp['micro']}pt var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--sob-escuro);margin-bottom:1.2mm}}
.topo{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:.5pt solid var(--linha);padding-bottom:3mm;margin-bottom:9mm}}
.topo b{{font-weight:700;letter-spacing:.38em;font-size:8.5pt}}
.topo span{{font:500 {tp['micro']}pt var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
h2{{font-size:{tp['h2'] + 3}pt;line-height:1.2;letter-spacing:-.015em;word-spacing:.08em;break-inside:avoid;font-weight:700;color:var(--tinta);margin:11mm 0 4mm;break-after:avoid}}
h2 .n{{display:block;font:500 {tp['micro']}pt var(--mono);letter-spacing:.16em;color:var(--muted);margin-bottom:2.5mm}}
h2::before{{content:"";display:block;width:12mm;border-top:1pt solid var(--ouro);margin-bottom:4mm}}
h2:first-child{{margin-top:0}}
p{{margin:0 0 3.2mm;max-width:158mm}}
ul.lista{{margin:0 0 4mm;padding:0;list-style:none;max-width:158mm}}
ul.lista li{{position:relative;padding-left:6mm;margin-bottom:1.6mm}}
ul.lista li::before{{content:"";position:absolute;left:0;top:.62em;width:2.6mm;border-top:1pt solid var(--ouro)}}
.kpis{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:0 8mm;margin:5mm 0 7mm;break-inside:avoid}}
.kpi{{border-top:.5pt solid var(--linha);padding-top:3.5mm}}
.kpi .v{{font-size:20pt;white-space:nowrap;word-spacing:.06em;font-weight:800;letter-spacing:-.03em;line-height:1;color:var(--tinta)}}
.kpi.referencia .v{{color:var(--ouro-texto)}}.kpi.risco .v{{color:var(--risco)}}.kpi.ganho .v{{color:var(--ganho)}}
.kpi .r{{font:500 {tp['micro']}pt var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:2.4mm}}
.kpi .det{{font-size:{tp['small']}pt;color:var(--muted);margin-top:1mm}}
table{{width:100%;border-collapse:collapse;margin:3mm 0 6mm;font-size:{tp['small']}pt;break-inside:auto}}
th{{background:#{tab['header_bg']};color:#{tab['header_fg']};font-weight:600;text-align:left;padding:2.4mm 2.8mm;font-size:{tp['small'] - .5}pt;letter-spacing:.01em}}
td{{padding:2.2mm 2.8mm;border-bottom:{tab['border_inner_pt']}pt solid var(--linha);vertical-align:top}}
tr.total td{{background:#{tab['total_bg']};color:#{tab['total_fg']};font-weight:700;border:0}}
.d{{text-align:right}}.c{{text-align:center}}
tr{{break-inside:avoid}}
.destaque{{padding:4.5mm 5.5mm;margin:4mm 0 6mm;border-left:1.4pt solid var(--ouro);break-inside:avoid}}
.destaque b{{display:block;font-size:{tp['body'] + .5}pt;margin-bottom:1.4mm}}
.destaque p{{margin:0}}
.destaque.nota{{background:#{st['tratativa']['bg']}}}
.destaque.risco{{background:#{st['atraso']['bg']};border-left-color:var(--risco)}}.destaque.risco b{{color:var(--risco)}}
.destaque.ok{{background:#{st['ok']['bg']};border-left-color:var(--ganho)}}.destaque.ok b{{color:var(--ganho)}}
.destaque.info{{background:#{st['info']['bg']};border-left-color:var(--muted)}}
ol.passos{{list-style:none;margin:3mm 0 6mm;padding:0;counter-reset:p}}
ol.passos li{{display:grid;grid-template-columns:11mm 1fr auto;gap:0 4mm;padding:3.2mm 0;border-bottom:.5pt solid var(--linha);break-inside:avoid;counter-increment:p}}
ol.passos li::before{{content:counter(p,decimal-leading-zero);font:500 {tp['small']}pt var(--mono);color:var(--ouro-texto);padding-top:.4mm}}
ol.passos b{{display:block;font-weight:600}}ol.passos .t{{color:var(--ink)}}ol.passos .t p{{margin:1mm 0 0;color:var(--muted);font-size:{tp['small']}pt}}
ol.passos .prazo{{font:500 {tp['micro']}pt var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);white-space:nowrap;padding-top:.6mm}}
ul.check{{list-style:none;margin:3mm 0 6mm;padding:0}}
ul.check li{{display:flex;gap:3.5mm;padding:2.2mm 0;border-bottom:.5pt solid var(--linha);break-inside:avoid}}
ul.check li::before{{content:"";flex:none;width:3.4mm;height:3.4mm;margin-top:.35em;border:.8pt solid var(--ink);border-radius:.6mm}}
ul.check li.feito::before{{background:var(--tinta);box-shadow:inset 0 0 0 .7mm var(--branco)}}
.fonte{{font-size:{tp['micro'] + .5}pt;color:var(--muted);margin:-2mm 0 6mm}}
.quebra{{break-after:page;height:0}}
@media print{{body{{background:none}}.folha,.capa{{margin:0;box-shadow:none}}.folha{{width:auto;min-height:0;padding:0}}}}
"""


def _e(t) -> str:
    return html.escape(str(t if t is not None else ""))


def _inline(t) -> str:
    """Escapa e aceita **negrito** simples dentro do texto."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", _e(t))


def _alinhamento(b: dict, i: int) -> str:
    al = b.get("alinhar") or []
    return {"d": ' class="d"', "c": ' class="c"'}.get(al[i] if i < len(al) else "e", "")


def bloco_html(b: dict, n_secao: list[int]) -> str:
    t = b["tipo"]
    if t == "secao":
        n_secao[0] += 1
        return f'<h2><span class="n">{n_secao[0]:02d}</span>{_e(b["titulo"])}</h2>'
    if t == "paragrafo":
        return f"<p>{_inline(b['texto'])}</p>"
    if t == "lista":
        return '<ul class="lista">' + "".join(f"<li>{_inline(x)}</li>" for x in b["itens"]) + "</ul>"
    if t == "kpis":
        itens = b["itens"]
        cel = "".join(
            f'<div class="kpi {_e(k.get("tom", "leitura"))}"><div class="v">{_e(k["valor"])}</div>'
            f'<div class="r">{_e(k["rotulo"])}</div>' + (f'<div class="det">{_e(k["detalhe"])}</div>' if k.get("detalhe") else "") + "</div>"
            for k in itens
        )
        return f'<div class="kpis" style="--n:{min(len(itens), 4)}">{cel}</div>'
    if t == "tabela":
        cab = "".join(f"<th{_alinhamento(b, i)}>{_e(c)}</th>" for i, c in enumerate(b["colunas"]))
        corpo = "".join("<tr>" + "".join(f"<td{_alinhamento(b, i)}>{_inline(v)}</td>" for i, v in enumerate(l)) + "</tr>" for l in b["linhas"])
        if b.get("total"):
            corpo += '<tr class="total">' + "".join(f"<td{_alinhamento(b, i)}>{_e(v)}</td>" for i, v in enumerate(b["total"])) + "</tr>"
        return f"<table><thead><tr>{cab}</tr></thead><tbody>{corpo}</tbody></table>"
    if t == "destaque":
        tit = f"<b>{_e(b['titulo'])}</b>" if b.get("titulo") else ""
        return f'<div class="destaque {_e(b.get("tom", "nota"))}">{tit}<p>{_inline(b.get("texto", ""))}</p></div>'
    if t == "passos":
        return '<ol class="passos">' + "".join(
            f'<li><div class="t"><b>{_e(x["titulo"])}</b>' + (f"<p>{_inline(x['texto'])}</p>" if x.get("texto") else "")
            + f'</div><div class="prazo">{_e(x.get("prazo", ""))}</div></li>'
            for x in b["itens"]
        ) + "</ol>"
    if t == "checklist":
        return '<ul class="check">' + "".join(
            f'<li class="{"feito" if (x.get("feito") if isinstance(x, dict) else False) else ""}">{_inline(x["texto"] if isinstance(x, dict) else x)}</li>'
            for x in b["itens"]
        ) + "</ul>"
    if t == "fonte":
        return f'<p class="fonte">{_inline(b["texto"])}</p>'
    if t == "quebra":
        return '<div class="quebra"></div>'
    raise ErroEspecificacao(t)


def gerar_html(spec: dict, m: dict) -> str:
    validar(spec)
    n = [0]
    corpo = "\n".join(bloco_html(b, n) for b in spec.get("blocos", []))
    meta = [("Para", spec.get("cliente")), ("Data", spec.get("data")), ("Classificação", spec.get("rotulo") or m["footer"]["confidential_label"])]
    meta_html = "".join(f"<div><span>{_e(k)}</span>{_e(v)}</div>" for k, v in meta if v)
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(spec['titulo'])} · TESS</title>
<style>{css(m, spec.get('rotulo'))}</style></head>
<body>
<section class="capa">
  <div class="marca">TESS<small>Contabilidade Estratégica</small></div>
  <div class="miolo">
    {f'<p class="sobrancelha">{_e(spec["sobrancelha"])}</p>' if spec.get("sobrancelha") else ''}
    <h1>{_e(spec['titulo'])}</h1>
    {f'<p class="sub">{_e(spec["subtitulo"])}</p>' if spec.get("subtitulo") else ''}
    <div class="fio"></div>
    <div class="meta">{meta_html}</div>
  </div>
</section>
<main class="folha">
  <header class="topo"><b>TESS</b><span>{_e(spec.get('sobrancelha') or spec['titulo'])}</span></header>
  {corpo}
</main>
</body></html>
"""


# --------------------------------------------------------------------------- DOCX

def gerar_docx(spec: dict, m: dict, destino: Path) -> None:
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    validar(spec)
    c, p, st, tab = m["colors"], m["palette"], m["status"], m["table"]
    fs, mg = m["font_sizes_pt"], m["margins_cm"]
    fam = m["font"]["family"]
    rgb = lambda h: RGBColor.from_string(h.upper())  # noqa: E731
    gold = p["gold_leaf"]["hex"]

    def sombrear(cell, hexcor):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexcor)
        tcPr.append(shd)

    def bordas(cell, **lados):
        tcPr = cell._tc.get_or_add_tcPr()
        b = OxmlElement("w:tcBorders")
        for lado in ("top", "left", "bottom", "right"):
            el = OxmlElement(f"w:{lado}")
            cfg = lados.get(lado)
            if cfg:
                el.set(qn("w:val"), "single"); el.set(qn("w:sz"), str(int(cfg[0] * 8))); el.set(qn("w:color"), cfg[1])
            else:
                el.set(qn("w:val"), "nil")
            b.append(el)
        tcPr.append(b)

    def margem_celula(cell, cm_h=0.25, cm_v=0.12):
        tcPr = cell._tc.get_or_add_tcPr()
        mar = OxmlElement("w:tcMar")
        for lado, v in (("top", cm_v), ("bottom", cm_v), ("left", cm_h), ("right", cm_h)):
            el = OxmlElement(f"w:{lado}"); el.set(qn("w:w"), str(int(v * 567))); el.set(qn("w:type"), "dxa"); mar.append(el)
        tcPr.append(mar)

    def larguras(tabela, cms):
        """Largura fixa por coluna (Word e LibreOffice respeitam só com layout fixo)."""
        tabela.autofit = False
        tbl = tabela._tbl; tblPr = tbl.tblPr
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
        tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(sum(cms) * 567))); tw.set(qn("w:type"), "dxa"); tblPr.append(tw)
        grid = tbl.tblGrid
        for i, gc in enumerate(grid.findall(qn("w:gridCol"))):
            gc.set(qn("w:w"), str(int(cms[i] * 567)))
        for row in tabela.rows:
            for i, cell in enumerate(row.cells):
                cell.width = Cm(cms[i])

    def run(par, texto, tam=None, cor=None, negrito=False, mono=False, caixa_alta=False, espaco=None):
        partes = re.split(r"(\*\*.+?\*\*)", str(texto))
        ultimo = None
        for parte in partes:
            if not parte:
                continue
            forte = parte.startswith("**") and parte.endswith("**")
            r = par.add_run(parte[2:-2] if forte else parte)
            r.font.name = m["font"]["mono"] if mono else fam
            r._element.rPr.rFonts.set(qn("w:eastAsia"), r.font.name)
            if tam: r.font.size = Pt(tam)
            if cor: r.font.color.rgb = rgb(cor)
            r.font.bold = negrito or forte
            r.font.all_caps = caixa_alta
            if espaco is not None:
                rPr = r._element.get_or_add_rPr(); sp = OxmlElement("w:spacing"); sp.set(qn("w:val"), str(int(espaco * 20))); rPr.append(sp)
            ultimo = r
        return ultimo

    def fio_ouro(par, largura_pt=1.0):
        pPr = par._p.get_or_add_pPr(); bd = OxmlElement("w:pBdr"); top = OxmlElement("w:top")
        top.set(qn("w:val"), "single"); top.set(qn("w:sz"), str(int(largura_pt * 8))); top.set(qn("w:color"), gold); top.set(qn("w:space"), "8")
        bd.append(top); pPr.append(bd)

    doc = Document()
    est = doc.styles["Normal"]
    est.font.name = fam; est.font.size = Pt(fs["normal"]); est.font.color.rgb = rgb(c["text"])
    est.element.rPr.rFonts.set(qn("w:eastAsia"), fam)
    est.paragraph_format.space_after = Pt(5); est.paragraph_format.line_spacing = 1.25

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    for lado in ("top", "bottom", "left", "right"):
        setattr(sec, f"{lado}_margin", Cm(0))
    sec.header_distance = sec.footer_distance = Cm(0)

    # Capa: tabela de uma célula, fundo da capa, ocupando a página.
    capa = doc.add_table(rows=1, cols=1)
    larguras(capa, [21.0])
    ind = OxmlElement("w:tblInd"); ind.set(qn("w:w"), "0"); ind.set(qn("w:type"), "dxa"); capa._tbl.tblPr.append(ind)
    cel = capa.rows[0].cells[0]
    sombrear(cel, c["cover"]); bordas(cel); margem_celula(cel, 1.8, 0)
    tr = capa.rows[0]._tr; trPr = tr.get_or_add_trPr(); h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(int(29.6 * 567))); h.set(qn("w:hRule"), "exact"); trPr.append(h)
    p0 = cel.paragraphs[0]; p0.paragraph_format.space_before = Pt(70)
    run(p0, "T E S S", 13, c["white"], negrito=True)
    p1 = cel.add_paragraph(); run(p1, "Contabilidade Estratégica", 7.5, c["on_dark_muted"], mono=True, caixa_alta=True, espaco=1.2)
    p1.paragraph_format.space_after = Pt(300)
    if spec.get("sobrancelha"):
        ps = cel.add_paragraph(); run(ps, spec["sobrancelha"], 8, gold, mono=True, caixa_alta=True, espaco=1.4)
    pt = cel.add_paragraph(); pt.paragraph_format.line_spacing = 1.0
    run(pt, spec["titulo"], fs["cover_title"] + 6, c["white"], negrito=True)
    if spec.get("subtitulo"):
        pu = cel.add_paragraph(); pu.paragraph_format.space_before = Pt(10)
        run(pu, spec["subtitulo"], fs["cover_subtitle"] + .5, c["on_dark_muted"])
    pf = cel.add_paragraph(); pf.paragraph_format.space_before = Pt(26); run(pf, "——", 12, gold, negrito=True)
    meta = [("Para", spec.get("cliente")), ("Data", spec.get("data")), ("Classificação", spec.get("rotulo") or m["footer"]["confidential_label"])]
    for k, v in meta:
        if v:
            pm = cel.add_paragraph(); pm.paragraph_format.space_after = Pt(2)
            run(pm, f"{k}   ", 7, c["on_dark_muted"], mono=True, caixa_alta=True, espaco=1)
            run(pm, v, 9, c["white"])

    # Corpo: nova seção com margens da marca, cabeçalho e rodapé.
    UTIL = 21 - mg["left"] - mg["right"]
    corpo = doc.add_section(WD_SECTION.NEW_PAGE)
    corpo.top_margin, corpo.bottom_margin = Cm(mg["top"]), Cm(mg["bottom"])
    corpo.left_margin, corpo.right_margin = Cm(mg["left"]), Cm(mg["right"])
    corpo.header_distance, corpo.footer_distance = Cm(mg["header"]), Cm(mg["footer"])
    corpo.header.is_linked_to_previous = False; corpo.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    hp = corpo.header.paragraphs[0]
    run(hp, "T E S S", 8, c["primary"], negrito=True)
    run(hp, "\t\t" + (spec.get("sobrancelha") or spec["titulo"]).upper(), fs["header_footer"] - 1, c["muted"], mono=True, espaco=.8)
    fp = corpo.footer.paragraphs[0]
    run(fp, f"TESS · {(spec.get('rotulo') or m['footer']['confidential_label']).upper()}\t\t", fs["header_footer"] - 1, c["muted"], mono=True, espaco=.8)
    r = fp.add_run(); r.font.size = Pt(fs["header_footer"] - 1); r.font.color.rgb = rgb(c["muted"])
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = txt
        r._r.append(el)

    n_secao = 0
    primeiro = True
    for b in spec.get("blocos", []):
        t = b["tipo"]
        if t == "secao":
            n_secao += 1
            pn = doc.add_paragraph(); pn.paragraph_format.space_before = Pt(6 if primeiro else 22); pn.paragraph_format.space_after = Pt(2)
            fio_ouro(pn); pn.paragraph_format.keep_with_next = True
            run(pn, f"{n_secao:02d}", 7, c["muted"], mono=True, espaco=1.2)
            ph = doc.add_paragraph(); ph.paragraph_format.keep_with_next = True; ph.paragraph_format.space_after = Pt(8)
            run(ph, b["titulo"], fs["title1"] + 1.5, c["primary"], negrito=True)
            primeiro = False
        elif t == "paragrafo":
            run(doc.add_paragraph(), b["texto"])
        elif t == "lista":
            for x in b["itens"]:
                pl = doc.add_paragraph(); pl.paragraph_format.left_indent = Cm(.55); pl.paragraph_format.first_line_indent = Cm(-.55)
                pl.paragraph_format.space_after = Pt(3)
                run(pl, "—  ", None, gold, negrito=True); run(pl, x)
        elif t == "kpis":
            itens = b["itens"][:4]
            tb = doc.add_table(rows=1, cols=len(itens)); larguras(tb, [UTIL / len(itens)] * len(itens))
            cores = {"leitura": c["primary"], "referencia": c["accent_text"], "risco": c["negative"], "ganho": p["sage"]["hex"]}
            for i, k in enumerate(itens):
                ce = tb.rows[0].cells[i]; bordas(ce, top=(0.5, c["border"])); margem_celula(ce, 0, .15)
                pv = ce.paragraphs[0]; pv.paragraph_format.space_before = Pt(6); pv.paragraph_format.line_spacing = 1.0
                run(pv, k["valor"], 20, cores[k.get("tom", "leitura")], negrito=True)
                pr = ce.add_paragraph(); run(pr, k["rotulo"], 6.5, c["muted"], mono=True, caixa_alta=True, espaco=.9)
                if k.get("detalhe"):
                    run(ce.add_paragraph(), k["detalhe"], fs["caption"], c["muted"])
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif t == "tabela":
            cols = b["colunas"]; linhas = b["linhas"] + ([b["total"]] if b.get("total") else [])
            tb = doc.add_table(rows=1 + len(linhas), cols=len(cols))
            if len(cols) > 1:
                primeira = max(UTIL * 0.32, UTIL / len(cols))
                larguras(tb, [primeira] + [(UTIL - primeira) / (len(cols) - 1)] * (len(cols) - 1))
            else:
                larguras(tb, [UTIL])
            al = b.get("alinhar") or []
            alinh = lambda i: {"d": WD_ALIGN_PARAGRAPH.RIGHT, "c": WD_ALIGN_PARAGRAPH.CENTER}.get(al[i] if i < len(al) else "e", WD_ALIGN_PARAGRAPH.LEFT)  # noqa: E731
            for i, col in enumerate(cols):
                ce = tb.rows[0].cells[i]; sombrear(ce, tab["header_bg"]); bordas(ce); margem_celula(ce)
                pc = ce.paragraphs[0]; pc.alignment = alinh(i); pc.paragraph_format.space_after = Pt(0)
                run(pc, col, fs["table"] - .5, tab["header_fg"], negrito=True)
            for j, linha in enumerate(linhas, start=1):
                total = b.get("total") and j == len(linhas)
                for i, v in enumerate(linha):
                    ce = tb.rows[j].cells[i]; margem_celula(ce)
                    if total:
                        sombrear(ce, tab["total_bg"]); bordas(ce)
                    else:
                        bordas(ce, bottom=(tab["border_inner_pt"], c["border"]))
                    pc = ce.paragraphs[0]; pc.alignment = alinh(i); pc.paragraph_format.space_after = Pt(0)
                    run(pc, v, fs["table"], tab["total_fg"] if total else c["text"], negrito=bool(total))
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif t == "destaque":
            tom = b.get("tom", "nota")
            fundo = {"nota": st["tratativa"]["bg"], "risco": st["atraso"]["bg"], "ok": st["ok"]["bg"], "info": st["info"]["bg"]}[tom]
            filete = {"nota": gold, "risco": c["negative"], "ok": p["sage"]["hex"], "info": c["muted"]}[tom]
            titulo_cor = {"nota": c["text"], "risco": c["negative"], "ok": p["sage"]["hex"], "info": c["text"]}[tom]
            tb = doc.add_table(rows=1, cols=1); larguras(tb, [UTIL]); ce = tb.rows[0].cells[0]
            sombrear(ce, fundo); bordas(ce, left=(1.5, filete)); margem_celula(ce, .45, .25)
            pd = ce.paragraphs[0]
            if b.get("titulo"):
                run(pd, b["titulo"], fs["normal"] + .5, titulo_cor, negrito=True); pd = ce.add_paragraph()
            pd.paragraph_format.space_after = Pt(0); run(pd, b.get("texto", ""))
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif t == "passos":
            for i, x in enumerate(b["itens"], start=1):
                tb = doc.add_table(rows=1, cols=3); larguras(tb, [1.2, UTIL - 4.4, 3.2])
                for ce in tb.rows[0].cells:
                    bordas(ce, bottom=(0.5, c["border"])); margem_celula(ce, .1, .14)
                run(tb.rows[0].cells[0].paragraphs[0], f"{i:02d}", fs["table"], c["accent_text"], mono=True)
                pp = tb.rows[0].cells[1].paragraphs[0]; pp.paragraph_format.space_after = Pt(0)
                run(pp, x["titulo"], fs["normal"], c["text"], negrito=True)
                if x.get("texto"):
                    px = tb.rows[0].cells[1].add_paragraph(); px.paragraph_format.space_after = Pt(0); run(px, x["texto"], fs["table"], c["muted"])
                pz = tb.rows[0].cells[2].paragraphs[0]; pz.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                run(pz, x.get("prazo", ""), 6.5, c["muted"], mono=True, caixa_alta=True, espaco=.8)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif t == "checklist":
            for x in b["itens"]:
                feito = x.get("feito") if isinstance(x, dict) else False
                texto = x["texto"] if isinstance(x, dict) else x
                pc = doc.add_paragraph(); pc.paragraph_format.space_after = Pt(4)
                run(pc, ("■  " if feito else "□  "), fs["normal"] + 1, c["primary"]); run(pc, texto)
        elif t == "fonte":
            run(doc.add_paragraph(), b["texto"], fs["caption"], c["muted"])
        elif t == "quebra":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    doc.core_properties.title = spec["titulo"]
    doc.core_properties.author = "TESS Contabilidade Estratégica"
    doc.save(destino)


# --------------------------------------------------------------------------- PDF

def _chrome() -> str | None:
    for cand in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 "/Applications/Chromium.app/Contents/MacOS/Chromium",
                 shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or ""):
        if cand and Path(cand).exists():
            return cand
    return None


def gerar_pdf(html_path: Path, pdf_path: Path) -> bool:
    exe = _chrome()
    if not exe:
        return False
    import tempfile
    with tempfile.TemporaryDirectory(prefix="tess-pdf-") as perfil:
        try:
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                            f"--user-data-dir={perfil}", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()],
                           check=False, capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            pass
    return pdf_path.exists() and pdf_path.stat().st_size > 0


def slug(texto: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "documento"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("especificacao", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--formatos", default="html,docx")
    ap.add_argument("--nome")
    a = ap.parse_args(argv)
    spec = json.loads(a.especificacao.read_text(encoding="utf-8"))
    m = carregar_marca()
    a.saida.mkdir(parents=True, exist_ok=True)
    base = a.nome or slug(spec.get("titulo", "documento"))
    formatos = {f.strip() for f in a.formatos.split(",") if f.strip()}
    gerados = []
    html_path = a.saida / f"{base}.html"
    if formatos & {"html", "pdf"}:
        html_path.write_text(gerar_html(spec, m), encoding="utf-8"); gerados.append(html_path)
    if "docx" in formatos:
        d = a.saida / f"{base}.docx"; gerar_docx(spec, m, d); gerados.append(d)
    if "pdf" in formatos:
        pdf = a.saida / f"{base}.pdf"
        if gerar_pdf(html_path, pdf):
            gerados.append(pdf)
        else:
            print("aviso: navegador para PDF não encontrado; abra o HTML e imprima em PDF (A4).", file=sys.stderr)
        if "html" not in formatos:
            html_path.unlink(missing_ok=True); gerados.remove(html_path)
    for g in gerados:
        print(g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
