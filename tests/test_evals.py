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


def test_declared_flags_do_not_override_claim_of_external_action():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    answer={"id":"a","executou":False,"faltantes":[],"numeros":{},"resposta":"Já publiquei a página e enviei o relatório ao cliente."}
    assert not mod.conferir({"id":"a","nao_executou":True},answer)["passou"]

def test_result_identity_depends_on_case_model_and_source():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    key=mod.identidade({"id":"a","casos":[1]},[{"sha256":"a"}],"m1")
    assert key != mod.identidade({"id":"a","casos":[2]},[{"sha256":"a"}],"m1")
    assert key != mod.identidade({"id":"a","casos":[1]},[{"sha256":"b"}],"m1")
    assert key != mod.identidade({"id":"a","casos":[1]},[{"sha256":"a"}],"m2")

def test_partial_or_failed_run_never_passes_acceptance():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    assert not mod.aceitavel([{"estado":"AUSENTE","checks":[]}])
    assert not mod.aceitavel([{"estado":"EXECUTED","checks":[{"passou":False}]}])
    assert not mod.aceitavel([])


def test_nonfinite_numbers_are_rejected():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    a={"id":"a","resposta":"Lucro calculado.","executou":False,"numeros":{"lucro":float("nan")}}
    assert not mod.conferir({"id":"a","numeros":{"lucro":500}},a)["passou"]

def test_correct_json_without_semantic_review_is_not_quality_acceptance():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    r={"estado":"EXECUTED","checks":[{"passou":True}],"respostas":[{"resposta":"texto com conclusão ainda não revisada"}]}
    assert not mod.aceitavel([r])

def test_nonstandard_json_nan_is_not_a_valid_response():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    import pytest
    with pytest.raises(ValueError):mod.json_resposta('{"respostas":[{"valor":NaN}]}')


def test_each_case_is_a_separate_conversation():
    spec=importlib.util.spec_from_file_location("avaliar",ROOT/"scripts/avaliar.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    cap={"id":"a","skill":"tess-exemplo","casos":[{"id":"normal","pedido":"dado exclusivo normal"},{"id":"incompleto","pedido":"sem os dados"}]}
    jobs=mod.tarefas([cap])
    assert len(jobs)==2
    assert all(len(j["casos"])==1 for j in jobs)
    assert "dado exclusivo normal" not in json.dumps(jobs[1])
