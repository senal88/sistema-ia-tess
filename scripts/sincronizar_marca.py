#!/usr/bin/env python3
"""Mantém `marca/` alinhada ao dono do padrão visual TESS.

O dono é `glob_00_templates/_core/tokens/tess.json` (e as fontes em
`_core/assets/tess/fonts`). Este repositório é distribuído como plugin e não pode
apontar por symlink para fora dele, então guarda uma cópia com origem e sha256 em
`marca/ORIGEM.json`.

Uso:
    python3 scripts/sincronizar_marca.py --check
        Confere se os arquivos de `marca/` batem com o sha256 registrado (roda no CI).
    python3 scripts/sincronizar_marca.py --de ~/Projects/templates/glob_00_templates [--ref origin/main]
        Copia do dono no commit indicado e regrava ORIGEM.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = RAIZ / "marca"
ORIGEM = MARCA / "ORIGEM.json"
MAPA = {"tess.json": "_core/tokens/tess.json"}
FONTES = "_core/assets/tess/fonts"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def arquivos_locais() -> list[Path]:
    return sorted([MARCA / "tess.json", *(MARCA / "fonts").glob("*")])


def check() -> int:
    if not ORIGEM.exists():
        print("marca/ORIGEM.json ausente", file=sys.stderr)
        return 1
    reg = json.loads(ORIGEM.read_text(encoding="utf-8"))
    erros = []
    locais = {str(p.relative_to(MARCA)): p for p in arquivos_locais()}
    for rel, info in reg["arquivos"].items():
        p = locais.pop(rel, None)
        if p is None:
            erros.append(f"ausente: {rel}")
        elif sha(p) != info["sha256"]:
            erros.append(f"divergente: {rel}")
    erros += [f"sem registro de origem: {rel}" for rel in locais]
    for e in erros:
        print(e, file=sys.stderr)
    if not erros:
        print(f"marca em dia com {reg['repositorio']}@{reg['commit'][:7]}")
    return 1 if erros else 0


def sincronizar(dono: Path, ref: str) -> int:
    commit = subprocess.check_output(["git", "-C", str(dono), "rev-parse", ref], text=True).strip()

    def show(caminho: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(dono), "show", f"{commit}:{caminho}"])

    arquivos = {}
    for local, remoto in MAPA.items():
        (MARCA / local).write_bytes(show(remoto))
        arquivos[local] = {"de": remoto}
    for p in (MARCA / "fonts").glob("*"):
        remoto = f"{FONTES}/{p.name}"
        p.write_bytes(show(remoto))
        arquivos[f"fonts/{p.name}"] = {"de": remoto}
    for rel in arquivos:
        arquivos[rel]["sha256"] = sha(MARCA / rel)
    ORIGEM.write_text(json.dumps({
        "repositorio": "senal88/glob_00_templates",
        "commit": commit,
        "nota": "Cópia do dono do padrão visual TESS. Não editar à mão; rodar scripts/sincronizar_marca.py.",
        "arquivos": dict(sorted(arquivos.items())),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"marca sincronizada de {commit[:7]}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--de", type=Path)
    ap.add_argument("--ref", default="origin/main")
    a = ap.parse_args(argv)
    if a.check or not a.de:
        return check()
    return sincronizar(a.de.expanduser(), a.ref)


if __name__ == "__main__":
    sys.exit(main())
