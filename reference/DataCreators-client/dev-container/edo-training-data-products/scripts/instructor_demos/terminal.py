"""Persistent real PTY. Markers establish command completion, not prompt matching."""
from __future__ import annotations
import codecs, errno, fcntl, os, re, select, signal, struct, subprocess, termios, time, uuid
import pyte

class Terminal:
    def __init__(self,cwd,env,on_output=lambda _:None):
        master,slave=os.openpty()
        flags=termios.tcgetattr(slave); flags[3]&=~termios.ECHO;termios.tcsetattr(slave,termios.TCSANOW,flags)
        fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',16,78,0,0))
        self.process=subprocess.Popen(['bash','--noprofile','--norc','-i'],stdin=slave,stdout=slave,stderr=slave,cwd=cwd,env={**env,'PS1':'demo $ ','PS2':'> ','TERM':'xterm-256color','COLUMNS':'88','LINES':'26'},start_new_session=True,preexec_fn=lambda:fcntl.ioctl(0,termios.TIOCSCTTY,0))
        os.close(slave);self.master=master;self.decoder=codecs.getincrementaldecoder('utf-8')('replace');self.on_output=on_output
        self.screen=pyte.Screen(78,16);self.stream=pyte.Stream(self.screen)
        self.raw='';self.events=[];self.pending=None;self.presentation_pending=''
    @property
    def display(self): return '\n'.join(line.rstrip() for line in self.screen.display).strip()
    def feed(self,text):
        # pyte processes actual ANSI cursor operations. The DOM only presents
        # that observed screen; it never executes a canned transcript.
        self.stream.feed(text);self.on_output(self.display)
    def pump(self,timeout=.05):
        if not select.select([self.master],[],[],timeout)[0]: return ''
        try: data=os.read(self.master,65536)
        except OSError as e:
            if e.errno==errno.EIO:return ''
            raise
        text=self.decoder.decode(data);self.raw+=text;self.events.append({'time':time.monotonic(),'kind':'output','text':text})
        visible=self.presentation_pending+text;self.presentation_pending=''
        visible=re.sub(r'\x1e[^\x1f]*\x1f','',visible)
        if '\x1e' in visible:
            visible,self.presentation_pending=visible.split('\x1e',1)
            self.presentation_pending='\x1e'+self.presentation_pending
        self.feed(visible);return text
    def send(self,text):
        self.events.append({'time':time.monotonic(),'kind':'input','text':text});os.write(self.master,text.encode())
    def run(self,command=None,input_text=None,complete=True,wait_for=None,timeout=120,control=None):
        start=len(self.raw); marker=None
        if command is not None:
            self.feed('demo $ '+command+'\r\n') # visibly label real input as input
            marker='DEMO_'+uuid.uuid4().hex
            self.pending=marker
            self.send(command+"\n__demo_rc=$?; printf '\\n\\036"+marker+":%s\\037\\n' \"$__demo_rc\"\n")
        elif input_text is not None:self.send(input_text)
        elif control:self.send({'ctrl-c':'\x03','ctrl-d':'\x04','enter':'\n'}[control])
        if marker is None and complete: marker=self.pending
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            self.pump()
            output=self.raw[start:]
            found=re.search('\x1e'+re.escape(marker)+r':(-?\d+)\x1f',output) if marker and complete else None
            if found:
                # Completion marker is protocol, never a teaching frame.
                self.feed('\r\x1b[2K');self.pending=None
                return {'exit_code':int(found[1]),'output':re.sub(r'\x1eDEMO_[a-f0-9]+:-?\d+\x1f','',output)}
            if not complete and wait_for and re.search(wait_for,output):return {'exit_code':None,'output':output}
            if self.process.poll() is not None: raise RuntimeError('Terminal session exited before checkpoint')
        raise TimeoutError('No declared terminal completion/state within '+str(timeout)+' seconds')
    def close(self):
        # Interactive job control creates several process groups in our session.
        # Stop all of those groups, including a nested shell/background job.
        groups={self.process.pid}
        for path in __import__('pathlib').Path('/proc').glob('[0-9]*/stat'):
            try:
                fields=path.read_text().rsplit(')',1)[1].split()
                if int(fields[3])==self.process.pid:groups.add(int(fields[2]))
            except (OSError,ValueError,IndexError):pass
        for group in groups:
            try:os.killpg(group,signal.SIGTERM)
            except ProcessLookupError:pass
        if self.process.poll() is None:
            try:self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:os.killpg(self.process.pid,signal.SIGKILL);self.process.wait()
        for group in groups:
            try:os.killpg(group,signal.SIGKILL)
            except ProcessLookupError:pass
        os.close(self.master)
