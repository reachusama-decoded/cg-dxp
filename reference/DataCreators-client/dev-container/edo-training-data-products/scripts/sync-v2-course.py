#!/usr/bin/env python3
"""Generate bounded client reference/concept/summary views; never mutate a course."""
import argparse,copy,hashlib,json,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];V=ROOT/'challenges/v2';OUT=ROOT/'designer/generated/v2-quality-repair'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(n):
 if isinstance(n,dict):
  yield n
  for v in n.values():yield from walk(v)
 elif isinstance(n,list):
  for v in n:yield from walk(v)
def text(n):
 if isinstance(n,list):return ''.join(text(v) for v in n)
 if not isinstance(n,dict):return ''
 if n['t']=='Str':return n['c']
 if n['t']=='Code':return n['c'][1]
 if n['t'] in ['Space','SoftBreak','LineBreak']:return ' '
 return text(n.get('c',[]))
def ast(path):
 # Native anchors are preserved in ordinary Markdown preview. Infer stable
 # task identity from its heading prefix before validating the exact title.
 d=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json']))
 for n in walk(d['blocks']):
  if n['t']=='Header':
   m=re.match(r'^([a-z-]+-p[12]-\d+):',text(n['c'][2]))
   if m:n['c'][1][0]=m[1]
 return d
def md(doc):return subprocess.check_output(['pandoc','-f','json','-t','markdown','--wrap=none'],input=json.dumps(doc).encode()).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 m=json.loads((V/'manifest.json').read_text());actual={str(p.relative_to(V)) for p in V.rglob('README.md')}
 assert actual==set(m['readme_order']),'Incomplete/duplicate README inventory'
 docs={rel:ast(V/rel) for rel in m['readme_order']};concepts=['# Instructor concepts\n\nFull source-owned concepts; runnable solutions remain separate.'];summaries=[];coverage=[]
 for tool in m['tools']:
  root=(V/tool['readme']).read_text();concepts.append(root)
  for phase in tool['phases']:
   if not phase['offered']:continue
   doc=docs[phase['readme']]
   for task in phase['tasks']:
    heading=next((n for n in doc['blocks'] if n['t']=='Header' and n['c'][1][0]==task['id']),None)
    assert heading is not None,'Task metadata missing source heading'
    assert text(heading['c'][2])==task['id']+': '+task['title'],'Phase title/manifest drift: '+task['id']
    assert task['title'] in root and '#'+task['id']+')' in root,'Root task-table drift: '+task['id']
    task_start=doc['blocks'].index(heading)
    cn=next(n for n in doc['blocks'][task_start+1:] if n['t']=='Header' and text(n['c'][2])=='Concept')
    start=doc['blocks'].index(cn);end=next((i for i in range(start+1,len(doc['blocks'])) if doc['blocks'][i]['t']=='Header'),len(doc['blocks']))
    part=copy.deepcopy(doc);part['blocks']=doc['blocks'][start:end];concepts.append(md(part))
    summaries.append({'tool':tool['id'],'phase':phase['id'],'id':task['id'],'title':task['title'],'estimate_minutes':task['estimate_minutes'],'runtime':phase['runtime'],'evidence':task['success_evidence'],'source':phase['readme']})
 for rel in m['readme_order']:coverage.append({'path':rel,'sha256':sha(V/rel),'disposition':m.get('runtime_readme_dispositions',{}).get(rel,'complete learner source')})
 # This source reference is a support artifact. Main book layout is the
 # root course adapter's named-project output, not another fixed Appendix H.
 reference='# Complete v2 source reference\n\nSupporting learner reference; assigned route and ownership remain in each canonical phase.\n\n'+'\n\n---\n\n'.join((V/rel).read_text() for rel in m['readme_order'])
 outputs={OUT/'learner-reference.md':reference+'\n',OUT/'instructor-concepts.md':'\n\n'.join(concepts)+'\n',OUT/'task-summaries.json':json.dumps(summaries,indent=2)+'\n'}
 report={'manifest_sha256':sha(V/'manifest.json'),'generator_sha256':sha(pathlib.Path(__file__)),'readmes':coverage,'readme_count':len(coverage),'task_count':len(summaries),'full_content':'Every complete source README retained byte-for-byte between support-reference separators; no truncation','boundary':'No course candidate, promotion, publication or runtime execution performed','outputs':{str(p.relative_to(ROOT)):hashlib.sha256(v.encode()).hexdigest() for p,v in outputs.items()}}
 outputs[OUT/'coverage.json']=json.dumps(report,indent=2)+'\n'
 stale=[str(p.relative_to(ROOT)) for p,v in outputs.items() if not p.exists() or p.read_text()!=v]
 if args.check:assert not stale,'Stale generated files: '+', '.join(stale)
 else:
  for p,v in outputs.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v)
 print('Client source views:',len(coverage),'READMEs /',len(summaries),'tasks; '+('fresh' if args.check else 'written'))
if __name__=='__main__':main()
