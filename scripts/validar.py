#!/usr/bin/env python3
"""Validador do Sistema IA TESS. Roda no CI e em `make validar`.

Confere:
  1. cada pasta em skills/ tem SKILL.md com `name` igual à pasta, prefixo `tess-` e `description` válida;
  2. catalogo.yaml lista exatamente as skills do disco, sem repetição e com área conhecida;
  3. toda referência a `compartilhado/...`, `exemplos/...` ou `scripts/...` nas skills existe;
  4. toda skill citada em outra skill (`tess-...`) existe;
  5. nenhuma marca, nome ou cor de terceiros (só TESS);
  6. nenhuma imagem de logotipo ou arquivo de imagem no repositório; fontes só em marca/fonts.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
IGNORAR = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
PROIBIDOS = [
    (re.compile(r"\bdonos\b", re.I), "nomenclatura de terceiros ('donos')"),
    (re.compile(r"manual\s*de\s*donos|manualdedonos", re.I), "marca de terceiros"),
    (re.compile(r"sistema[-_ ]de[-_ ]donos", re.I), "nomenclatura antiga do sistema"),
    (re.compile(r"#?\b(00205B|5DD9BA|BBA249)\b", re.I), "cor fora da paleta TESS vigente"),
]
EXT_IMAGEM = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp", ".tif", ".tiff", ".heic", ".ai", ".eps", ".psd"}
EXT_FONTE = {".woff2", ".woff", ".ttf", ".otf"}
MAX_DESCRICAO = 1024


def arquivos():
    for p in RAIZ.rglob("*"):
        if p.is_file() and not (set(p.relative_to(RAIZ).parts) & IGNORAR):
            yield p


def frontmatter(texto: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        raise ValueError("sem frontmatter YAML")
    return yaml.safe_load(m.group(1)) or {}


def validar() -> list[str]:
    erros: list[str] = []
    pastas = sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir())

    # 1. skills
    for nome in pastas:
        arq = RAIZ / "skills" / nome / "SKILL.md"
        if not arq.exists():
            erros.append(f"{nome}: falta SKILL.md"); continue
        texto = arq.read_text(encoding="utf-8")
        try:
            fm = frontmatter(texto)
        except Exception as e:  # noqa: BLE001
            erros.append(f"{nome}: {e}"); continue
        if fm.get("name") != nome:
            erros.append(f"{nome}: name '{fm.get('name')}' difere da pasta")
        if not nome.startswith("tess-") or not re.fullmatch(r"[a-z0-9-]+", nome):
            erros.append(f"{nome}: slug precisa começar com 'tess-' e usar só a-z, 0-9 e hífen")
        d = fm.get("description") or ""
        if not (80 <= len(d) <= MAX_DESCRICAO):
            erros.append(f"{nome}: description com {len(d)} caracteres (80 a {MAX_DESCRICAO})")
        if "Use quando" not in d:
            erros.append(f"{nome}: description sem gatilhos ('Use quando ...')")
        # 3. referências a arquivos do repositório
        for ref in sorted(set(re.findall(r"`((?:compartilhado|exemplos|scripts)/[\w./-]+)`", texto))):
            if not (RAIZ / ref).exists():
                erros.append(f"{nome}: referência inexistente {ref}")
        # 4. skills citadas
        for citada in sorted(set(re.findall(r"`(tess-[a-z0-9-]+)`", texto))):
            if citada not in pastas:
                erros.append(f"{nome}: cita skill inexistente {citada}")

    # 2. catálogo
    cat = yaml.safe_load((RAIZ / "catalogo.yaml").read_text(encoding="utf-8"))
    slugs = [s["slug"] for s in cat["skills"]]
    if len(slugs) != len(set(slugs)):
        erros.append("catalogo.yaml: slug repetido")
    for falta in sorted(set(pastas) - set(slugs)):
        erros.append(f"catalogo.yaml: skill {falta} fora do catálogo")
    for sobra in sorted(set(slugs) - set(pastas)):
        erros.append(f"catalogo.yaml: {sobra} sem pasta em skills/")
    for s in cat["skills"]:
        if s["area"] not in cat["areas"]:
            erros.append(f"catalogo.yaml: {s['slug']} com área desconhecida {s['area']}")

    # 3b. referências nos documentos compartilhados
    for doc in (RAIZ / "compartilhado").glob("*.md"):
        for citada in sorted(set(re.findall(r"`(tess-[a-z0-9-]+)`", doc.read_text(encoding="utf-8")))):
            if citada not in pastas:
                erros.append(f"{doc.relative_to(RAIZ)}: cita skill inexistente {citada}")

    # 5 e 6. marca e arquivos
    este = Path(__file__).resolve()
    for p in arquivos():
        rel = p.relative_to(RAIZ)
        ext = p.suffix.lower()
        if ext in EXT_IMAGEM:
            erros.append(f"{rel}: arquivo de imagem não permitido (a marca é o nome TESS em texto)")
        if ext in EXT_FONTE and rel.parts[:2] != ("marca", "fonts"):
            erros.append(f"{rel}: fonte fora de marca/fonts")
        if p.resolve() == este or ext in EXT_FONTE | {".docx", ".xlsx", ".pdf"}:
            continue
        try:
            texto = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            erros.append(f"{rel}: binário inesperado"); continue
        if re.search(r"(^|[-_.])logo", rel.name.lower()):
            erros.append(f"{rel}: arquivo de logotipo não permitido")
        for rx, motivo in PROIBIDOS:
            if (m := rx.search(texto)):
                linha = texto.count("\n", 0, m.start()) + 1
                erros.append(f"{rel}:{linha}: {motivo}: '{m.group(0)}'")
    return erros


def main() -> int:
    erros = validar()
    for e in erros:
        print(f"ERRO  {e}", file=sys.stderr)
    n = len(list((RAIZ / "skills").iterdir()))
    if erros:
        print(f"{len(erros)} erro(s)", file=sys.stderr)
        return 1
    print(f"validar OK · {n} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
