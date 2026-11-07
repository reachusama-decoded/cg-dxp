#!/usr/bin/env python3
"""Audit retained source, full appendix parity, word/page floors and offline HTML."""
import hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[2]/'DataCreators-v4';C=BASE/'candidates/challenges-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
retention=json.loads((C/'retention.json').read_text());assert len(retention)==12
for row in retention:
 a=(C/'learner'/row['path']).read_bytes();b=(BASE/'learner'/row['path']).read_bytes();assert a.startswith(b)
coverage=json.loads((C/'coverage.json').read_text());m=json.loads((ROOT/'challenges/v2/manifest.json').read_text())
assert {r['path'] for r in coverage['readmes']}==set(m['readme_order'])
for r in coverage['readmes']:assert r['sha256']==sha(ROOT/'challenges/v2'/r['path'])
word=json.loads((C/'reviews/qualifying-text/word-count.json').read_text());assert word['passed']
pdf=C/'DataCreators-challenges-v2.pdf';pages=int(re.search(r'^Pages:\s+(\d+)',subprocess.check_output(['pdfinfo',str(pdf)],text=True),re.M)[1]);assert pages>=237
text=(C/'render/course.txt').read_text();log=(C/'render/build.log').read_text()
for marker in ['Diagram failed to render','MISSING IMAGE','[MISSING-IMAGE]','renderer failed','Missing character:']:assert marker not in text+log,marker
for task in [x for t in m['tools'] for p in t['phases'] for x in p['tasks']]:assert task['id'] in text,task['id']
# Actual diagram count from parsed source, rather than a hardcoded number.
ast=json.loads(subprocess.check_output(['pandoc',str(C/'render/course.md'),'-t','json']))
diagrams=sum(n.get('t')=='CodeBlock' and 'mermaid' in n['c'][0][1] for n in walk(ast))
images=list((C/'render/images').glob('*.png'));assert len(images)==diagrams and all(p.stat().st_size for p in images)
ids=[n['c'][1][0] for n in walk(ast) if n.get('t')=='Header'];assert len(ids)==len(set(ids)),'Duplicate book heading anchors'
# Offline full-book HTML uses the exact combined source and rendered local diagrams.
style=C/'build/pdf';builder=Path(__import__('os').environ.get('CWBUILDER_ROOT',str(ROOT.parents[3].parent/'ts-courseware/Platform/CwBuilder')))
subprocess.run(['pandoc',str(C/'render/course.md'),'-s','--toc','-t','html5','-o',str(C/'DataCreators-challenges-v2.html'),f'--lua-filter={style}/provenance.lua',f'--lua-filter={style}/debrief.lua',f'--lua-filter={builder}/filters/mermaid.lua',f'--lua-filter={C}/render/book-links.lua','-M',f'mermaid-output-dir={C}/render/images','-M',f'mermaid-theme-config={builder}/themes/decoded/mermaid-theme.json','-M','title=Data Creators: challenge v2 candidate'],check=True)
html=C/'DataCreators-challenges-v2.html';s=html.read_text().replace(str(C/'render/images')+'/','render/images/')
def local_target(match):
    key,quote,target=match.groups()
    if target.startswith(('#','http:','https:','data:','mailto:')):return match[0]
    name=target.partition('#')[0]
    if not (C/name).exists() and (C/'learner'/name).exists():target='learner/'+target
    return key+'='+quote+target+quote
s=re.sub(r"(href|src)=([\"'])([^\"']+)[\"']",local_target,s)
html.write_text(s)
report={'passed':True,'pages':pages,'substantive_learner_words':word['substantive_learner_words'],'readmes_in_full':len(coverage['readmes']),'active_tasks':coverage['task_count'],'retained_baseline_chapters':len(retention),'diagrams':diagrams,'pdf_sha256':sha(pdf),'html_sha256':sha(html),'source_sha256':{p.name:sha(p) for p in sorted((C/'learner').glob('[0-9][0-9]-*.md'))},'limits':['Human junior pilots pending','Docker/GitHub/Databricks/Astro UI/Kafka chain pending','Visual sample review recorded separately']}
(C/'reviews/course-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
