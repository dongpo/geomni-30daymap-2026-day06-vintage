from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os,re
os.chdir(Path(__file__).resolve().parents[1])
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  path=self.translate_path(self.path)
  if self.headers.get('Range') and os.path.isfile(path):
   f=open(path,'rb');size=os.fstat(f.fileno()).st_size;m=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range'])
   if not m:f.close();self.send_error(416);return
   start=int(m[1]);end=min(int(m[2]) if m[2] else size-1,size-1)
   if start>end:f.close();self.send_error(416);return
   self.send_response(206);self.send_header('Content-Type',self.guess_type(path));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',end-start+1);self.end_headers();f.seek(start);self.remaining=end-start+1;return f
  self.remaining=None;return super().send_head()
 def copyfile(self,source,outputfile):
  if self.remaining is None:return super().copyfile(source,outputfile)
  left=self.remaining
  while left:
   b=source.read(min(left,65536))
   if not b:break
   outputfile.write(b);left-=len(b)
print('Local review: http://127.0.0.1:8766/demo/',flush=True)
ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
