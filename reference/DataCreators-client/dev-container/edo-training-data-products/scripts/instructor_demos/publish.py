"""Offline reviewed-asset export. Publishing never runs tool workloads."""
from __future__ import annotations
import html,json,math,re,shutil,subprocess
from pathlib import Path
from .contracts import sha,write_json
from .runner import check_capture

ANSI=re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
def safe_text(text,manifest):
    text=re.sub(r'\x1eDEMO_[a-f0-9]+:-?\d+\x1f','',text)
    text=ANSI.sub('',text).replace('\r','')
    private=manifest['private_artifacts']['path']
    text=text.replace(private+'/workspace','challenges/demo-workspace').replace(private,'demo-artifacts')
    return ''.join(c for c in text if c in '\n\t' or ord(c)>=32)
def vtt_time(seconds):
    milliseconds=round(seconds*1000);h,milliseconds=divmod(milliseconds,3600000);m,milliseconds=divmod(milliseconds,60000);s,milliseconds=divmod(milliseconds,1000)
    return f'{h:02}:{m:02}:{s:02}.{milliseconds:03}'
def latex(text):
    return ''.join({'\\':r'\textbackslash{}','{':r'\{','}':r'\}','#':r'\#','$':r'\$','%':r'\%','&':r'\&','_':r'\_','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(text))

def page_groups(checkpoints):
    groups=[];pending=[]
    for cp in checkpoints:
        dense='\n' in cp['command'] or len(cp['command'])>100
        if dense:
            if pending:groups.append(pending);pending=[]
            groups.append([cp])
        else:
            pending.append(cp)
            if len(pending)==2:groups.append(pending);pending=[]
    if pending:groups.append(pending)
    return groups

def review(root,path,story,manifest,reviewer,notes):
    check_capture(root,path,story,manifest)
    if not notes.strip():raise ValueError('Review must describe actual frame/video inspection and limits')
    manifest['review']={'reviewer':reviewer,'notes':notes,'source_hashes':manifest['source_hashes'],'frames':{x['frame']:x['frame_sha256'] for x in manifest['checkpoints']},'videos':manifest.get('videos',[]),'verdict':'approved for candidate export'}
    return manifest

def export(root,items,output,pdf=False):
    if output.exists():raise ValueError('Export destination exists; choose a fresh candidate')
    models=[]
    # Validate everything before creating a partial export.
    for path,story,manifest in items:
        check_capture(root,path,story,manifest)
        r=manifest.get('review')
        if not r or r.get('verdict')!='approved for candidate export' or r['source_hashes']!=manifest['source_hashes'] or r['frames']!={x['frame']:x['frame_sha256'] for x in manifest['checkpoints']} or r['videos']!=manifest.get('videos',[]):raise ValueError('Missing or stale review')
    output.mkdir(parents=True)
    shutil.copy2(root/'scripts/serve-instructor-demos.py',output/'serve.py')
    for path,story,manifest in items:
        work=Path(manifest['private_artifacts']['path']);dest=output/'stories'/story['id'];dest.mkdir(parents=True)
        # Exact demonstrated helper commands need their source in a portable
        # bundle. This allowlisted independent oracle contains no model answers.
        if (work/'workspace/inspect-output.py').is_file():
            shutil.copy2(work/'workspace/inspect-output.py',dest/'inspect-output.py')
        checkpoints=[];transcript=[];captions=['WEBVTT','']
        for index,cp in enumerate(manifest['checkpoints'],1):
            shutil.copy2(work/cp['frame'],dest/cp['frame'])
            executed=cp.get('executed_action',cp['action'])
            command=safe_text(executed.get('command',executed.get('input',executed.get('verb',''))),manifest)
            text=safe_text(cp['observation']['output'],manifest)
            transcript.extend([str(index)+'. '+cp['caption']['action'],cp['context'],command,text,''])
            captions.extend([str(index),vtt_time(cp['time_range'][0])+' --> '+vtt_time(cp['time_range'][1]),cp['caption']['action']+' '+cp['caption']['notice'],''])
            checkpoints.append({'index':index,'step_id':cp['step_id'],'context':cp['context'],'command':command,'caption':cp['caption'],'frame':'stories/'+story['id']+'/'+cp['frame'],'frame_sha256':cp['frame_sha256'],'exit_code':cp['observation']['exit_code'],'time_range':cp['time_range'],'assertions':cp['assertions'],'observed_output':text})
        (dest/'transcript.txt').write_text('\n'.join(transcript));(dest/'captions.vtt').write_text('\n'.join(captions))
        videos=[]
        for index,v in enumerate(manifest.get('videos',[]),1):
            name=f'recording-{index}.webm';shutil.copy2(work/v['path'],dest/name)
            videos.append('stories/'+story['id']+'/'+name)
        model={'id':story['id'],'title':story['title'],'objective':story['objective'],'tool':story['tool'],'route':story['route'],'audience':story['audience'],'task_ids':story['task_ids'],'main_book':story['main_book'],'closing_question':story['closing_question'],'checkpoints':checkpoints,'videos':videos,'captions':'stories/'+story['id']+'/captions.vtt','transcript':'stories/'+story['id']+'/transcript.txt','run_id':manifest['run_id'],'source_hashes':manifest['source_hashes'],'runtime':manifest['runtime'],'recording':manifest['recording'],'review':manifest['review']}
        write_json(dest/'story.json',model);models.append(model)
    generate_html(output,models);generate_tex(output,models)
    (output/'README.md').write_text('# Instructor demo review candidate\n\nRun `python3 serve.py --port 8000` and open `http://localhost:8000/`. The supplied static server supports HTTP byte ranges for video seeking. The PDF links to the relative HTML companion. Captured stories are explicitly instructor demonstrations on the stated routes; they do not establish connected execution or learner completion.\n\nCommands assume the fresh prepared instructor project shown in each story. The independent `inspect-output.py` helper is supplied beside each dbt story; copy it into that project when replaying its inspection command. Complete instructor projects and the reusable capture runner are supplied in the separate instructor archive. Authenticate outside recordings.\n\nFull catalogue, course integration, human pacing and projector review remain pending as recorded in the source handoff.\n')
    if pdf:
        result=subprocess.run(['xelatex','-halt-on-error','-interaction=nonstopmode','DataCreators-Instructor-Demos.tex'],cwd=output,capture_output=True,text=True)
        (output/'pdf-build.log').write_text(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError('Demo PDF render failed: '+result.stdout[-3000:])
        subprocess.run(['xelatex','-halt-on-error','-interaction=nonstopmode','DataCreators-Instructor-Demos.tex'],cwd=output,check=True,stdout=subprocess.DEVNULL)
    write_json(output/'selection.json',{'captured_eligible':len(models),'selected':sum(m['main_book']['include'] for m in models),'planned_catalogue':12,'planned_selected':3,'complete_library':len(models)==12,'page_cost':sum(len(page_groups(m['checkpoints'])) for m in models if m['main_book']['include']),'course_integration':'pending remaining selected live pilots and course review'})
    write_json(output/'bundle.json',{'schema_version':1,'stories':[m['id'] for m in models],'files':{str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*')) if p.is_file() and p.suffix not in ['.log','.aux','.toc','.out']}})
    return {'output':str(output),'stories':len(models),'pdf':pdf}

def generate_html(output,models):
    h=html.escape
    parts=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Data Creators instructor demos — candidate</title><style>body{font:18px/1.5 system-ui;margin:auto;max-width:1000px;padding:20px;color:#142436}a{color:#086669}nav{display:flex;gap:20px;flex-wrap:wrap}article{margin:45px 0;border-top:4px solid #187577}img,video{max-width:100%;height:auto}figure{margin:25px 0}figcaption{background:#eef4f5;padding:12px}pre{overflow:auto;background:#142436;color:white;padding:15px;font-size:16px}button{padding:10px;cursor:pointer}button:focus,a:focus{outline:3px solid #187577}small{display:block}video{width:100%}details{margin:20px 0}</style></head><body><h1>Data Creators instructor demos</h1><p>Review candidate. Only observed, reviewed stories appear here; the execution report records the remaining catalogue and live gates. Run <code>python3 serve.py --port 8000</code> to view and seek captioned recordings.</p><nav aria-label="Stories">']
    parts.extend(f'<a href="#{h(m["id"])}">{h(m["title"])}</a>' for m in models);parts.append('</nav>')
    for m in models:
        parts.append(f'<article id="{h(m["id"])}"><h2>{h(m["title"])}</h2><p>{h(m["objective"])}</p><small>{h(m["id"])} · {h(m["route"])} · {h(", ".join(m["task_ids"]))} · Run {h(m["run_id"])}</small>')
        for index,video in enumerate(m['videos'],1):parts.append(f'<video controls preload="metadata" aria-label="{h(m["title"])} recording {index}"><source src="{h(video)}" type="video/webm"><track default kind="captions" src="{h(m["captions"])}" srclang="en" label="English"><a href="{h(video)}">Download recording</a></video>')
        for cp in m['checkpoints']:
            parts.append(f'<figure id="{h(m["id"])}-{h(cp["step_id"])}"><img src="{h(cp["frame"])}" alt="Observed checkpoint {cp["index"]}: {h(cp["caption"]["notice"])}"><figcaption><strong>{cp["index"]}. {h(cp["caption"]["action"])}</strong><small>{h(cp["context"])} · observed exit {cp["exit_code"]}</small>{h(cp["caption"]["notice"])}</figcaption></figure>')
            if cp['command']:parts.append(f'<pre><code>{h(cp["command"])}</code></pre><button type="button" class="copy">Copy command</button>')
        parts.append(f'<p><strong>Discuss:</strong> {h(m["closing_question"])}</p><details><summary>Transcript and exact commands</summary><pre>{h((output/m["transcript"]).read_text())}</pre></details><a href="{h(m["transcript"])}">Download transcript</a></article>')
    parts.append('<script>for(const b of document.querySelectorAll(".copy")){b.addEventListener("click",async()=>{const text=b.previousElementSibling.textContent;try{await navigator.clipboard.writeText(text);b.textContent="Copied"}catch(e){b.textContent="Select the command above to copy"}})}</script></body></html>')
    (output/'index.html').write_text('\n'.join(parts))

def generate_tex(output,models):
    preamble=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=12mm]{geometry}
\usepackage{fontspec}\setmainfont{DejaVu Sans}\setmonofont{DejaVu Sans Mono}
\usepackage{graphicx,xcolor,hyperref,fvextra}
\definecolor{ink}{HTML}{142436}\definecolor{accent}{HTML}{187577}
\hypersetup{colorlinks=true,urlcolor=accent,linkcolor=accent}
\setlength{\parindent}{0pt}\setlength{\parskip}{2pt}
\newcommand{\demoband}[1]{\noindent\colorbox{ink}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\color{white}\large #1}}}
'''
    pages=[preamble,r'\begin{document}',r'\begin{titlepage}\Huge Data Creators\\Instructor Demos\par\vspace{1cm}\large Review candidate — observed stories only.\par\normalsize The pending catalogue and external runtime gates are recorded separately.\par\href{run:index.html}{Open the offline HTML companion}\end{titlepage}',r'\tableofcontents\clearpage']
    for m in models:
        fragment=[]
        groups=page_groups(m['checkpoints'])
        for start,group in enumerate(groups):
            fragment.extend([r'\clearpage',r'\phantomsection',r'\demoband{INSTRUCTOR DEMO · '+latex(m['tool'])+' · '+latex(m['id'])+'}',r'{\Large\bfseries '+latex(m['title'])+'}'+(' (continued)' if start else '')+r'\par'])
            if start==0:fragment.extend([r'\addcontentsline{toc}{section}{'+latex(m['title'])+'}',latex(m['objective'])+r'\par',r'{\small Route: '+latex(m['route'])+' · Tasks: '+latex(', '.join(m['task_ids']))+r'}\par'])
            for cp in group:
                fragment.extend([r'\noindent\includegraphics[width=\linewidth,height=.36\textheight,keepaspectratio]{'+cp['frame']+'}',r'\par{\bfseries '+str(cp['index'])+'. '+latex(cp['caption']['action'])+r'}\par',r'{\small '+latex(cp['context'])+' · observed exit '+latex(cp['exit_code'])+r'}\par',latex(cp['caption']['notice'])+r'\par'])
                if cp['command']:fragment.extend([r'\begin{Verbatim}[fontsize=\small,breaklines=true,breakanywhere=true]',cp['command'],r'\end{Verbatim}'])
            if start==len(groups)-1:fragment.extend([r'\textbf{Discuss:} '+latex(m['closing_question'])+r'\par',r'\href{run:index.html\#'+m['id']+'}{Watch the demo in the offline HTML companion}'])
        (output/'stories'/m['id']/'story.tex').write_text('\n'.join(fragment)+'\n');pages.extend(fragment)
    pages.extend([r'\clearpage\section*{Tool and task index}'])
    for m in models:pages.append(latex(m['tool']+' · '+m['id']+' · '+', '.join(m['task_ids']))+r'\par')
    pages.append(r'\end{document}');(output/'DataCreators-Instructor-Demos.tex').write_text('\n'.join(pages)+'\n')
