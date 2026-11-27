import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_suite_has_complete_unique_pairs():
    suite = json.loads((ROOT / "evals/casos.json").read_text())
    ids = [c["id"] for c in suite["capacidades"]]
    assert len(ids) == len(set(ids)) == 34
    assert all({x["tipo"] for x in c["casos"]} == {"normal", "incompleto"} for c in suite["capacidades"])

def test_grader_rejects_wrong_numbers_and_false_execution():
    spec = importlib.util.spec_from_file_location("avaliar", ROOT / "scripts/avaliar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    case = {"id":"teste", "numeros":{"lucro":500}, "nao_executou":True}
    good = {"id":"teste", "numeros":{"lucro":500}, "executou":False,"resposta":"O lucro calculado é 500.","faltantes":[]}
    assert mod.conferir(case, good)["passou"]
    assert not mod.conferir(case, dict(good,numeros={"lucro":600}))["passou"]
    assert not mod.conferir(case, dict(good,executou=True))["passou"]

def test_grader_requires_missing_data_instead_of_inventing():
    spec = importlib.util.spec_from_file_location("avaliar", ROOT / "scripts/avaliar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    case={"id":"lacuna", "exige_lacuna":True,"nao_executou":True}
    assert not mod.conferir(case,{"id":"lacuna","numeros":{},"executou":False,"resposta":"Tudo pronto.","faltantes":[]})["passou"]

def test_error_or_missing_response_never_becomes_pass():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    assert not mod.conferir({"id":"a"},None)["passou"]
