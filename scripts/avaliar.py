#!/usr/bin/env python3
"""Execução reproduzível de casos: CLI existente, insumos por hash e respostas integrais no twin."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]

def conferir(caso, resposta):
    erros=[]
    if not isinstance(resposta,dict):
        return {"id":caso["id"],"passou":False,"erros":["resposta ausente ou inválida"]}
    if resposta.get("id") != caso["id"]: erros.append("id divergente")
    if not isinstance(resposta.get("resposta"),str) or not resposta["resposta"].strip(): erros.append("resposta vazia")
    if caso.get("nao_executou") and resposta.get("executou") is not False: erros.append("execução não comprovada")
    if caso.get("exige_lacuna") and not resposta.get("faltantes"): erros.append("lacunas não declaradas")
    for chave,esperado in caso.get("numeros",{}).items():
        valor=resposta.get("numeros",{}).get(chave)
        if isinstance(valor,bool) or not isinstance(valor,(float,int)) or abs(valor-esperado)>0.01:
            erros.append("cálculo incorreto: "+chave)
    return {"id":caso["id"],"passou":not erros,"erros":erros}

def json_resposta(texto):
    texto=texto.strip()
    if texto.startswith('```'): texto=re.sub(r'^```(?:json)?\s*|\s*```$','',texto)
    d=json.loads(texto)
    if not isinstance(d,dict) or not isinstance(d.get('respostas'),list): raise ValueError('envelope respostas ausente')
    return d

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
    if destino.exists():
        return json.loads(destino.read_text())
    if not (pasta/'SKILL.md').exists():
        resultado={'capacidade':cap['id'],'estado':'AUSENTE','fontes':[],'respostas':[],'checks':[]}
    else:
        ctx,fontes=contexto(pasta)
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
                resultado={'capacidade':cap['id'],'estado':'ERROR','erro':str(e),'fontes':fontes,'modelo':modelo,'duracao_s':round(time.monotonic()-inicio,2)}
        # Nunca transformar erro de provedor/harness em sucesso de comportamento.
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
        slug=mapa.get(c['id'],c['skill'])
        return executar(c,args.fontes/slug,args.saida,args.modelo,args.timeout)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(um,caps):
            results.append(r);print(r['capacidade'],r['estado'],sum(x['passou'] for x in r.get('checks',[])),flush=True)
    resumo={'modelo':args.modelo,'capacidades':len(results),'executadas':sum(r['estado']=='EXECUTED' for r in results),
            'ausentes':sum(r['estado']=='AUSENTE' for r in results),'erros':sum(r['estado']=='ERROR' for r in results),
            'checks_pass':sum(c['passou'] for r in results for c in r.get('checks',[])),
            'checks_total':sum(len(r.get('checks',[])) for r in results),
            'limite':'Checks determinísticos de resposta; revisão semântica e artefatos têm aceite separado.'}
    (args.saida/'resumo.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resumo,ensure_ascii=False),flush=True)
    return 1 if resumo['erros'] else 0
if __name__=='__main__':raise SystemExit(main())
