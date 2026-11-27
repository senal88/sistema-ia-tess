#!/usr/bin/env python3
"""Execução reproduzível de casos: CLI existente, insumos por hash e respostas integrais no twin."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]

def identidade(cap, fontes, modelo):
    dado={"capacidade":cap,"fontes":fontes,"modelo":modelo,"harness":"2"}
    return hashlib.sha256(json.dumps(dado,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def aceitavel(resultados):
    """Aceite exige também revisão semântica explícita; checks JSON nunca bastam."""
    return bool(resultados) and all(
        r.get("estado")=="EXECUTED" and bool(r.get("checks"))
        and all(c.get("passou") is True for c in r["checks"])
        and r.get("revisao_semantica",{}).get("aprovada") is True
        for r in resultados)

def conferir(caso, resposta):
    erros=[]
    if not isinstance(resposta,dict):
        return {"id":caso["id"],"passou":False,"erros":["resposta ausente ou inválida"]}
    if resposta.get("id") != caso["id"]: erros.append("id divergente")
    if not isinstance(resposta.get("resposta"),str) or not resposta["resposta"].strip(): erros.append("resposta vazia")
    if caso.get("nao_executou") and resposta.get("executou") is not False: erros.append("execução não comprovada")
    if caso.get("exige_lacuna") and not resposta.get("faltantes"): erros.append("lacunas não declaradas")
    # Esta guarda pega declarações diretas; inferências e contradições numéricas exigem revisão semântica.
    if caso.get("nao_executou"):
        for frase in re.split(r"[.!?\n]",resposta.get("resposta","")):
            if not re.search(r"\b(não|nunca|nada|sem)\b",frase,re.I) and re.search(r"\b(publiquei|enviei|instalei|executei|publiquei|foi publicado|foi enviado)\b",frase,re.I):
                erros.append("texto declara ação externa sem evidência")
    numeros=resposta.get("numeros")
    if not isinstance(numeros,dict):numeros={}
    for chave,esperado in caso.get("numeros",{}).items():
        valor=numeros.get(chave)
        if isinstance(valor,bool) or not isinstance(valor,(float,int)) or not math.isfinite(valor) or abs(valor-esperado)>0.01:
            erros.append("cálculo incorreto: "+chave)
    return {"id":caso["id"],"passou":not erros,"erros":erros}

def json_resposta(texto):
    texto=texto.strip()
    if texto.startswith('```'): texto=re.sub(r'^```(?:json)?\s*|\s*```$','',texto)
    def rejeitar(valor): raise ValueError('constante JSON não finita: '+valor)
    d=json.loads(texto,parse_constant=rejeitar)
    if not isinstance(d,dict) or not isinstance(d.get('respostas'),list): raise ValueError('envelope respostas ausente')
    return d

def tarefas(capacidades):
    """Cada caso tem sessão e cache próprios; o incompleto não vê dados do normal."""
    return [dict(c,id=caso["id"],capacidade_id=c["id"],casos=[caso])
            for c in capacidades for caso in c["casos"]]

def contexto(pasta):
    arquivos=[pasta/'SKILL.md']
    for nome in ['referencias','references']:
        arquivos += sorted((pasta/nome).glob('*.md'))
    arquivos += sorted((pasta.parent.parent/'compartilhado').glob('*.md'))
    partes=[];fontes=[]
    for p in arquivos:
        if p.exists():
            b=p.read_bytes();fontes.append({'arquivo':str(p),'sha256':hashlib.sha256(b).hexdigest()})
            partes.append(p.name+'\n'+b.decode('utf-8'))
    return '\n\n'.join(partes),fontes

def executar(cap,pasta,saida,modelo,timeout):
    destino=saida/(cap['id']+'.json')
    ctx,fontes=contexto(pasta)
    fingerprint=identidade(cap,fontes,modelo)
    if destino.exists():
        anterior=json.loads(destino.read_text())
        if anterior.get('identidade')==fingerprint:return anterior
        raise ValueError('Cache de outro insumo/modelo; use nova pasta de saída para preservar evidência')
    if not (pasta/'SKILL.md').exists():
        resultado={'capacidade':cap['id'],'estado':'AUSENTE','fontes':[],'respostas':[],'checks':[]}
    else:
        perguntas=[{'id':c['id'],'pedido':c['pedido'],'chaves_numericas':list(c.get('numeros',{}))} for c in cap['casos']]
        prompt=('Avaliação isolada de uma competência. Não use ferramentas, não leia outros arquivos, não publique nem envie. '
                'Aplique as instruções abaixo a cada pedido de forma independente. Retorne SOMENTE JSON válido: '
                '{"respostas":[{"id":"id do caso","resposta":"sua entrega completa em até 200 palavras",'
                '"numeros":{"chave pedida":0},"faltantes":["dados desconhecidos"],"executou":false}]}. '
                'Preencha números apenas quando calculáveis; executou descreve ação externa realmente feita. '
                'A resposta textual deve ser substantiva, com o método da competência, não apenas anunciar o que faria.\n\n'
                'INSTRUÇÕES DA COMPETÊNCIA:\n'+ctx+'\n\nPEDIDOS:\n'+json.dumps(perguntas,ensure_ascii=False))
        inicio=time.monotonic()
        env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
        # A CLI é a superfície já instalada/autenticada; não criamos cliente nem secret paralelo.
        with tempfile.TemporaryDirectory(prefix='tess-avaliar-') as td:
            f=Path(td)/'entrada.txt';f.write_text(prompt)
            comando=['opencode','run','--agent','plan','--model',modelo,'--format','json','--archived','--file',str(f),'Responda aos pedidos do arquivo. Não use ferramentas.']
            proc=None
            try:
                proc=subprocess.run(comando,cwd=td,env=env,capture_output=True,text=True,timeout=timeout)
                eventos=[]
                for linha in proc.stdout.splitlines():
                    try:eventos.append(json.loads(linha))
                    except json.JSONDecodeError:continue
                texto=''.join(e.get('part',{}).get('text','') for e in eventos if e.get('type')=='text')
                d=json_resposta(texto)
                answers={x['id']:x for x in d['respostas']}
                tools=[e for e in eventos if e.get('type') in ['tool_use','tool_call']]
                if proc.returncode or tools: raise ValueError('CLI com erro ou ferramenta usada em execução sem ferramentas')
                resultado={'capacidade':cap['id'],'estado':'EXECUTED','modelo':modelo,'duracao_s':round(time.monotonic()-inicio,2),
                           'fontes':fontes,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'prompt':prompt,
                           'eventos':eventos,'respostas':d['respostas'],'checks':[conferir(c,answers.get(c['id'])) for c in cap['casos']]}
            except (subprocess.TimeoutExpired,ValueError,KeyError,json.JSONDecodeError) as e:
                resultado={'capacidade':cap['id'],'estado':'ERROR','erro':str(e),'fontes':fontes,'modelo':modelo,'duracao_s':round(time.monotonic()-inicio,2),
                           'prompt':prompt,'stdout':proc.stdout if proc else '', 'stderr':proc.stderr if proc else '',
                           'returncode':proc.returncode if proc else None}
        # Nunca transformar erro de provedor/harness em sucesso de comportamento.
    resultado['identidade']=fingerprint
    resultado['revisao_semantica']={'aprovada':False,'estado':'NOT_EXECUTED'}
    destino.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
    return resultado

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fontes',type=Path,required=True)
    ap.add_argument('--mapa',type=Path)
    ap.add_argument('--saida',type=Path,required=True)
    ap.add_argument('--modelo',required=True)
    ap.add_argument('--workers',type=int,default=3)
    ap.add_argument('--timeout',type=int,default=240)
    ap.add_argument('--somente',nargs='*')
    args=ap.parse_args()
    if not args.modelo.startswith(('opencode/','opencode-go/')): ap.error('use a rota gratuita/assinatura governada')
    suite=json.loads((ROOT/'evals/casos.json').read_text())
    caps=[c for c in suite['capacidades'] if not args.somente or c['id'] in args.somente]
    mapa=json.loads(args.mapa.read_text()) if args.mapa else {}
    args.saida.mkdir(parents=True,exist_ok=True)
    def um(c):
        slug=mapa.get(c.get('capacidade_id',c['id']),c['skill'])
        return executar(c,args.fontes/slug,args.saida,args.modelo,args.timeout)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(um,tarefas(caps)):
            results.append(r);print(r['capacidade'],r['estado'],sum(x['passou'] for x in r.get('checks',[])),flush=True)
    resumo={'modelo':args.modelo,'capacidades':len(caps),'casos':len(results),'executadas':sum(r['estado']=='EXECUTED' for r in results),
            'ausentes':sum(r['estado']=='AUSENTE' for r in results),'erros':sum(r['estado']=='ERROR' for r in results),
            'checks_pass':sum(c['passou'] for r in results for c in r.get('checks',[])),
            'checks_total':sum(len(r.get('checks',[])) for r in results),
            'aceite_qualidade':aceitavel(results),
            'limite':'Checks determinísticos de resposta; revisão semântica e artefatos têm aceite separado.'}
    (args.saida/'resumo.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resumo,ensure_ascii=False),flush=True)
    return 0 if resumo['aceite_qualidade'] else 1
if __name__=='__main__':raise SystemExit(main())
