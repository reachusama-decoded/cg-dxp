#!/usr/bin/env python3
"""Move assessed legacy answer blocks out of v2 learner READMEs; preserve every byte."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def transform(text,tool):
    # These source blocks are HTML details wrappers around ordinary Markdown.
    # Fence-aware scanning prevents a literal tag in a code example closing one.
    lines=text.splitlines(keepends=True);out=[];answers=[];i=0;fence=None
    while i<len(lines):
        line=lines[i];marker=re.match(r'^\s*(`{3,}|~{3,})',line)
        if fence:
            out.append(line);i+=1
            if marker and marker[1][0]==fence[0] and len(marker[1])>=fence[1]:fence=None
            continue
        if marker:fence=(marker[1][0],len(marker[1]));out.append(line);i+=1;continue
        start=re.fullmatch(r'\s*<details><summary>(.*[Ss]olution.*?)</summary>\s*',line)
        if not start:out.append(line);i+=1;continue
        body=[];j=i+1;inner=None
        while j<len(lines):
            marker=re.match(r'^\s*(`{3,}|~{3,})',lines[j])
            if inner:
                if marker and marker[1][0]==inner[0] and len(marker[1])>=inner[1]:inner=None
            elif marker:inner=(marker[1][0],len(marker[1]))
            elif lines[j].strip()=='</details>':break
            elif '<details>' in lines[j]:raise ValueError('Unexpected nested answer block')
            body.append(lines[j]);j+=1
        if j==len(lines):raise ValueError('Unclosed solution details')
        number=len(answers)+1;answers.append({'title':start[1],'body':''.join(body),'original_wrapper_sha256':hashlib.sha256(''.join(lines[i:j+1]).encode()).hexdigest()})
        out.append(f'Worked answer {number} is supplied separately in the instructor pack: `challenges/v2-solutions/{tool}/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.\n')
        i=j+1
    return ''.join(out),answers

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args();ledger=[]
    for tool in ['dbt','airflow','capstone']:
        source=ROOT/f'challenges/v2/{tool}/phase-two-proficient/stretch/README.md';text=source.read_text();changed,answers=transform(text,tool)
        if a.check:
            if answers:raise SystemExit('Embedded assessed answers remain: '+str(source))
            continue
        if not answers:continue
        dest=ROOT/f'challenges/v2-solutions/{tool}/phase-two-proficient/legacy-stretch-answers.md'
        if dest.exists():raise SystemExit('Existing instructor answers; refusing overwrite')
        header=f'# Instructor legacy stretch answers — {tool}\n\nPreserved from `{source.relative_to(ROOT)}` before separation. These legacy exercises retain their separate v1 runtime and access requirements; they are not evidence of v2 live execution. No real notification or external publishing is authorized.\n'
        body=header+'\n'.join(f'## Answer {i}: {x["title"]}\n'+x['body'] for i,x in enumerate(answers,1))
        dest.write_text(body);source.write_text(changed)
        ledger.append({'source':str(source.relative_to(ROOT)),'original_sha256':hashlib.sha256(text.encode()).hexdigest(),'learner_sha256':hashlib.sha256(changed.encode()).hexdigest(),'instructor':str(dest.relative_to(ROOT)),'answers':[{'title':x['title'],'original_wrapper_sha256':x['original_wrapper_sha256'],'body_sha256':hashlib.sha256(x['body'].encode()).hexdigest()} for x in answers]})
    if ledger:
        (ROOT/'designer/reviews/v2-answer-separation.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print('Answer separation checked' if a.check else f'Moved {sum(len(x["answers"]) for x in ledger)} complete answer blocks')
if __name__=='__main__':main()
