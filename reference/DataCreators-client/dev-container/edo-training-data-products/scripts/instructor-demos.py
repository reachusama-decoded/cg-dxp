#!/usr/bin/env python3
"""Capture verified observations; review and export candidates without running jobs."""
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
from instructor_demos.contracts import Blocked,doctor,load_story,write_json
from instructor_demos.runner import capture,check_capture
from instructor_demos.publish import export,review
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT)
    sub=ap.add_subparsers(dest='command',required=True)
    for name in ['doctor','list','validate']:
        p=sub.add_parser(name);p.add_argument('--story')
    p=sub.add_parser('capture');p.add_argument('--story',required=True);p.add_argument('--run-id',default=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));p.add_argument('--dry-run',action='store_true')
    for name in ['check','review']:
        p=sub.add_parser(name);p.add_argument('--story',required=True);p.add_argument('--run-id',required=True)
        if name=='review':p.add_argument('--reviewer',required=True);p.add_argument('--notes',required=True)
    p=sub.add_parser('export');p.add_argument('--run-id',required=True);p.add_argument('--story',action='append',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--pdf',action='store_true')
    a=ap.parse_args();root=a.root.resolve();paths=sorted((root/'instructor-demos/stories').glob('*/story.yaml'));stories={}
    for path in paths:
        story=load_story(root,path)
        if story['id'] in stories:raise ValueError('Duplicate story ID')
        stories[story['id']]=(path,story)
    def select(ident):
        if ident not in stories:raise ValueError('Unknown story '+ident)
        return stories[ident]
    def manifest(ident):return json.loads((root/'designer/reviews/instructor-demos'/a.run_id/ident/'capture-manifest.json').read_text())
    if a.command=='list':result=[{'id':s['id'],'tool':s['tool'],'readiness':s['readiness'],'selected':s['main_book']['include'],'route':s['route']} for _,s in stories.values() if not a.story or a.story==s['id']]
    elif a.command=='validate':
        if a.story:select(a.story)
        result={'validated':len(stories) if not a.story else 1,'selected':sum(s['main_book']['include'] for _,s in stories.values())}
    elif a.command=='doctor':
        req=select(a.story)[1]['requires'] if a.story else sorted({r for _,s in stories.values() for r in s['requires']})
        result=doctor(root,req)
    elif a.command=='capture':
        path,story=select(a.story);result=capture(root,path,story,a.run_id,a.dry_run)
    elif a.command in ['check','review']:
        path,story=select(a.story);m=manifest(a.story)
        if a.command=='check':result={'valid':check_capture(root,path,story,m)}
        else:
            m=review(root,path,story,m,a.reviewer,a.notes);write_json(root/'designer/reviews/instructor-demos'/a.run_id/a.story/'capture-manifest.json',m);result=m['review']
    else:
        items=[(*select(ident),manifest(ident)) for ident in a.story];result=export(root,items,a.output.resolve(),a.pdf)
    print(json.dumps(result,indent=2))
    if a.command=='capture' and not a.dry_run and result['status']!='captured':return 77 if result['status']=='blocked' else 1
    if a.command=='doctor' and any(r['status']=='blocked' for r in result.values()):return 77
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except KeyboardInterrupt:print('Interrupted; owned cleanup recorded',file=sys.stderr);sys.exit(130)
    except (ValueError,AssertionError,Blocked) as e:print(str(e),file=sys.stderr);sys.exit(77 if isinstance(e,Blocked) else 1)
