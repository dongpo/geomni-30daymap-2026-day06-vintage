"""Original seeded paper grain; no third-party artwork or fonts copied."""
from pathlib import Path
from PIL import Image,ImageDraw
import random,base64
R=Path(__file__).resolve().parents[1];rng=random.Random(1904)
im=Image.new('RGBA',(256,256),(0,0,0,0));px=im.load()
for y in range(256):
 for x in range(256):
  a=rng.randrange(0,29);px[x,y]=(83,64,38,a) if rng.random()<.47 else (255,248,222,a)
d=ImageDraw.Draw(im)
for _ in range(65):
 x,y=rng.randrange(256),rng.randrange(256);d.line((x,y,x+rng.randint(2,10),y+rng.choice([-1,0,1])),fill=(90,72,43,rng.randint(8,22)),width=1)
im.save(R/'demo/paper-grain.png')
url='data:image/png;base64,'+base64.b64encode((R/'demo/paper-grain.png').read_bytes()).decode()
(R/'demo/paper-texture.css').write_text('main::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:1;background-image:url("'+url+'");opacity:.48;mix-blend-mode:multiply}aside{background-image:url("'+url+'")}')
