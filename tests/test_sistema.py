"""Testes do Sistema IA TESS: catálogo, marketplace, marca e motores de documento."""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import gerar_marketplace  # noqa: E402
import sincronizar_marca  # noqa: E402
import tess_documento  # noqa: E402
import tess_planilha  # noqa: E402
import validar  # noqa: E402


def test_validador_sem_erros():
    assert validar.validar() == []


def test_validador_ignora_o_que_o_gitignore_exclui():
    residuo = RAIZ / "skills" / ".DS_Store"
    criado = not residuo.exists()
    residuo.write_bytes(b"\x00\x01")
    try:
        assert residuo not in set(validar.arquivos())
        assert validar.validar() == []
    finally:
        if criado:
            residuo.unlink()


def test_31_skills():
    assert len([p for p in (RAIZ / "skills").iterdir() if p.is_dir()]) == 31


def test_readme_lista_cada_plugin_com_instalacao():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert readme == gerar_marketplace.readme_gerado()
    for p in gerar_marketplace.gerar()["plugins"]:
        assert f"/plugin install {p['name']} --marketplace senal88/sistema-ia-tess" in readme, p["name"]


def test_marketplace_em_dia_e_completo():
    gerado = gerar_marketplace.gerar()
    versionado = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert gerado == versionado
    nomes = {p["name"]: p for p in gerado["plugins"]}
    assert len(nomes["sistema-ia-tess"]["skills"]) == 31
    avulsos = [p for p in gerado["plugins"] if p["category"] not in {"pacote", "area"}]
    assert len(avulsos) == 31 and all(len(p["skills"]) == 1 for p in avulsos)
    assert sum(len(p["skills"]) for p in gerado["plugins"] if p["category"] == "area") == 31
    for p in gerado["plugins"]:
        assert p["source"] == "./" and p["strict"] is False
        for s in p["skills"]:
            assert (RAIZ / s / "SKILL.md").exists()


def test_marca_igual_ao_dono():
    assert sincronizar_marca.check() == 0


# Montados por concatenação para o próprio validador não acusar este arquivo.
D = "Do" + "nos"
@pytest.mark.parametrize("texto", [f"o Sistema de {D}", f"manualde{D.lower()}", f"Manual de {D}", f"sistema-de-{D.lower()}", "cor #" + "0020" + "5B"])
def test_validador_pega_nome_e_cor_de_terceiros(texto):
    assert any(rx.search(texto) for rx, _ in validar.PROIBIDOS)


def test_validador_aceita_texto_tess():
    texto = "O dono da empresa decide com a TESS; a ferramenta mostra a margem."
    assert not any(rx.search(texto) for rx, _ in validar.PROIBIDOS)


@pytest.fixture
def spec():
    return json.loads((RAIZ / "exemplos" / "diagnostico-financeiro.json").read_text(encoding="utf-8"))


def test_html_sem_imagem_e_com_fontes(spec):
    html = tess_documento.gerar_html(spec, tess_documento.carregar_marca())
    assert "<img" not in html and "url(http" not in html
    assert "font/woff2;base64" in html
    assert spec["titulo"] in html and "TESS" in html
    assert "Confidencial" in html


def test_html_usa_so_cores_da_marca():
    m = tess_documento.carregar_marca()
    css = tess_documento.css(m)
    permitidas = {v["hex"].upper() for v in m["palette"].values()} | {v.upper() for v in m["colors"].values()}
    permitidas |= {v[k].upper() for v in m["status"].values() for k in ("bg", "fg")}
    permitidas |= {m["table"][k].upper() for k in ("header_bg", "header_fg", "total_bg", "total_fg")}
    permitidas |= {"E9E7E1"}  # fundo de tela em volta da folha; não imprime
    usadas = {h.upper() for h in re.findall(r"#([0-9A-Fa-f]{6})\b", css)}
    assert usadas <= permitidas, usadas - permitidas


def test_docx_abre_e_nao_tem_imagem(spec, tmp_path):
    pytest.importorskip("docx")
    destino = tmp_path / "d.docx"
    tess_documento.gerar_docx(spec, tess_documento.carregar_marca(), destino)
    with zipfile.ZipFile(destino) as z:
        xml = z.read("word/document.xml").decode()
        assert "Diagnóstico financeiro" in xml
        assert not [n for n in z.namelist() if n.startswith("word/media/")]


def test_especificacao_invalida():
    with pytest.raises(tess_documento.ErroEspecificacao):
        tess_documento.validar({"titulo": "x", "blocos": [{"tipo": "inexistente"}]})
    with pytest.raises(tess_documento.ErroEspecificacao):
        tess_documento.validar({"titulo": "x", "blocos": [{"tipo": "tabela", "colunas": ["a", "b"], "linhas": [["1"]]}]})


def test_planilha_com_nomes_e_formulas(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    spec = json.loads((RAIZ / "exemplos" / "plano-de-receita.json").read_text(encoding="utf-8"))
    destino = tmp_path / "p.xlsx"
    tess_planilha.gerar(spec, destino)
    wb = openpyxl.load_workbook(destino)
    assert wb.sheetnames == ["Premissas", "Funil"]
    assert {"meta", "ticket"} <= set(wb.defined_names.keys())
    assert wb["Funil"]["B5"].value == "=meta/ticket"
