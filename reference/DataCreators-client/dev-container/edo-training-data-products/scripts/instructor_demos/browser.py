"""Real browser actions and locator assertions; no application DOM rewriting."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

class Browser:
    def __init__(self,output):
        self.manager=sync_playwright().start();self.browser=self.manager.chromium.launch()
        self.context=self.browser.new_context(storage_state=os.environ.get("DEMO_BROWSER_STATE") or None, viewport={'width':1100,'height':600},device_scale_factor=2,record_video_dir=str(output/'video'),record_video_size={'width':1100,'height':600})
        self.page=self.context.new_page();self.application=None
        self.page.set_content('<html lang="en"><meta charset="utf-8"><style>body{margin:0;background:#101b2a;color:#e7eef6}header{padding:10px 25px;background:#21364b;font:16px sans-serif}header code{display:block;margin-top:5px;font:21px monospace}pre{margin:15px 25px;font:21px/1.25 monospace;white-space:pre}</style><header><span id="context"></span><code id="command"></code></header><pre id="screen" aria-live="polite"></pre></html>')
    def terminal_input(self,command,context):
        self.page.locator('#context').evaluate('(el,text)=>el.textContent=text',context+' · observed PTY output')
        first=command.splitlines()[0] if command else '(interactive input)'
        first=first if len(first)<=78 else first[:75]+'…'
        self.page.locator('#command').evaluate('(el,text)=>el.textContent=text',first)
    def terminal_output(self,text):self.page.locator('#screen').evaluate('(el,text)=>el.textContent=text',text)
    def act(self,action):
        if self.application is None:self.application=self.context.new_page()
        p=self.application;verb=action['verb'];timeout=action.get('timeout_seconds',60)*1000
        if verb=='navigate':p.goto(action['url'],wait_until='domcontentloaded',timeout=timeout)
        elif verb=='click':p.locator(action['locator']).click(timeout=timeout)
        elif verb=='fill':p.locator(action['locator']).fill(action['text'],timeout=timeout)
        elif verb=='wait':p.locator(action['locator']).wait_for(state='visible',timeout=timeout)
        return {'exit_code':0,'url':p.url,'output':p.locator(action.get('focus','body')).inner_text(timeout=timeout)}
    def frame(self,path,adapter,focus=None):
        p=self.page if adapter=='terminal' else self.application
        if focus:p.locator(focus).screenshot(path=str(path))
        else:p.screenshot(path=str(path))
    def hold(self,seconds):self.page.wait_for_timeout(seconds*1000)
    def close(self):
        pages=list(self.context.pages);videos=[p.video for p in pages if p.video]
        self.context.close();paths=[str(v.path()) for v in videos]
        self.browser.close();self.manager.stop();return paths
