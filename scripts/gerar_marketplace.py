#!/usr/bin/env python3
"""Gera `.claude-plugin/marketplace.json` e a seção de pacotes do README a partir de `catalogo.yaml` e `VERSION`.

Cada skill vira um plugin avulso; cada área vira um pacote; e há o pacote completo.
Todos apontam para a raiz do repositório (`source: "./"`, `strict: false`) e listam
só as próprias skills, então as pastas compartilhadas (`compartilhado/`, `marca/`,
`scripts/`) existem em qualquer instalação sem cópia.

A seção do README entre os marcadores `catalogo:inicio` e `catalogo:fim` lista cada pacote,
área e skill com a linha de instalação em um passo; não se edita à mão.

Uso: python3 scripts/gerar_marketplace.py [--check]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / ".claude-plugin" / "marketplace.json"
README = RAIZ / "README.md"
INICIO = "<!-- catalogo:inicio — gerado de catalogo.yaml por `make marketplace`; não editar -->"
FIM = "<!-- catalogo:fim -->"


def descricao_da_skill(slug: str) -> str:
    texto = (RAIZ / "skills" / slug / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    desc = (yaml.safe_load(m.group(1)) or {}).get("description") if m else None
    if not desc:
        raise SystemExit(f"{slug}: SKILL.md sem description")
    primeira = re.split(r"(?<=\.)\s", desc.strip(), maxsplit=1)[0]
    return primeira


def gerar() -> dict:
    cat = yaml.safe_load((RAIZ / "catalogo.yaml").read_text(encoding="utf-8"))
    versao = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()
    mk = cat["marketplace"]
    autor = {"name": mk["dono"]}
    base = {"source": "./", "strict": False, "version": versao, "author": autor}

    plugins = []
    completo = cat["pacote_completo"]
    plugins.append({
        "name": completo["nome"], "displayName": completo["titulo"], "description": completo["descricao"],
        **base, "category": "pacote", "keywords": ["tess", "completo"],
        "skills": [f"./skills/{s['slug']}" for s in cat["skills"]],
    })
    for chave, area in cat["areas"].items():
        plugins.append({
            "name": area["plugin"], "displayName": area["titulo"], "description": area["descricao"],
            **base, "category": "area", "keywords": ["tess", chave],
            "skills": [f"./skills/{s['slug']}" for s in cat["skills"] if s["area"] == chave],
        })
    for s in cat["skills"]:
        plugins.append({
            "name": s["slug"], "displayName": f"TESS · {s['titulo']}", "description": descricao_da_skill(s["slug"]),
            **base, "category": s["area"], "keywords": ["tess", s["area"]],
            "skills": [f"./skills/{s['slug']}"],
        })
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": mk["nome"],
        "description": mk["descricao"],
        "owner": autor,
        "plugins": plugins,
    }


def bloco_readme() -> str:
    cat = yaml.safe_load((RAIZ / "catalogo.yaml").read_text(encoding="utf-8"))
    repo = cat["marketplace"]["repositorio"]
    instalar = lambda nome: f"`/plugin install {nome} --marketplace {repo}`"
    completo = cat["pacote_completo"]
    linhas = [INICIO, "", "| Pacote | Instalar no Claude Code |", "|---|---|",
              f"| **{completo['titulo']}** (`{completo['nome']}`) | {instalar(completo['nome'])} |"]
    for chave, area in cat["areas"].items():
        linhas.append(f"| **{area['titulo']}** (`{area['plugin']}`) | {instalar(area['plugin'])} |")
    for chave, area in cat["areas"].items():
        linhas += ["", f"### {area['titulo']}", "", "| Skill | Instalar só esta skill |", "|---|---|"]
        linhas += [f"| {s['titulo']} (`{s['slug']}`) | {instalar(s['slug'])} |" for s in cat["skills"] if s["area"] == chave]
    return "\n".join(linhas + ["", FIM])


def readme_gerado() -> str:
    atual = README.read_text(encoding="utf-8")
    if INICIO not in atual or FIM not in atual:
        raise SystemExit("README.md sem os marcadores catalogo:inicio/catalogo:fim")
    antes, resto = atual.split(INICIO, 1)
    depois = resto.split(FIM, 1)[1]
    return antes + bloco_readme() + depois


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="falha se o arquivo versionado divergir do gerado")
    a = ap.parse_args(argv)
    texto = json.dumps(gerar(), ensure_ascii=False, indent=2) + "\n"
    readme = readme_gerado()
    if a.check:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        erros = []
        if atual != texto:
            erros.append("marketplace.json desatualizado")
        if README.read_text(encoding="utf-8") != readme:
            erros.append("seção de pacotes do README desatualizada")
        if erros:
            print("; ".join(erros) + ": rode `make marketplace`", file=sys.stderr)
            return 1
        print("marketplace.json e README em dia")
        return 0
    DESTINO.parent.mkdir(exist_ok=True)
    DESTINO.write_text(texto, encoding="utf-8")
    README.write_text(readme, encoding="utf-8")
    print(DESTINO.relative_to(RAIZ), README.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
