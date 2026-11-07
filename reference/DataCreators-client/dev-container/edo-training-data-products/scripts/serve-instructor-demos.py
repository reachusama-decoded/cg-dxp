#!/usr/bin/env python3
"""Serve a portable static demo bundle with byte ranges for reliable media seeking."""
import argparse,functools,http.server,re
from pathlib import Path

class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        self.byte_range=None
        path=Path(self.translate_path(self.path))
        if path.is_dir():return super().send_head()
        try:stream=path.open('rb')
        except OSError:self.send_error(404,'File not found');return None
        size=path.stat().st_size;requested=self.headers.get('Range');start=0;end=size-1
        if requested:
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested)
            if not match or not any(match.groups()):
                stream.close();self.send_error(416,'Unsupported byte range');return None
            if match[1]:start=int(match[1]);end=min(int(match[2]) if match[2] else end,end)
            else:start=max(0,size-int(match[2]))
            if start>end or start>=size:
                stream.close();self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
            self.byte_range=(start,end);stream.seek(start);self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        else:self.send_response(200)
        self.send_header('Accept-Ranges','bytes');self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Content-Length',str(end-start+1));self.send_header('Last-Modified',self.date_time_string(path.stat().st_mtime));self.end_headers();return stream
    def copyfile(self,source,output):
        if self.byte_range is None:return super().copyfile(source,output)
        remaining=self.byte_range[1]-self.byte_range[0]+1
        while remaining:
            data=source.read(min(65536,remaining))
            if not data:break
            output.write(data);remaining-=len(data)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--host',default='127.0.0.1');ap.add_argument('--port',type=int,default=8000);a=ap.parse_args()
    handler=functools.partial(RangeHandler,directory=str(a.directory.resolve()))
    with http.server.ThreadingHTTPServer((a.host,a.port),handler) as server:
        print(f'Serving instructor demos at http://{a.host}:{server.server_port}/',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
