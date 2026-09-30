from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..kdp.cover import CoverSpec, cover_dimensions

class CoverBuilder:
    def build(self,spec:CoverSpec,out:Path,front:Path|None=None,back:Path|None=None,title="",author="",dpi=300):
        w_in,h_in=cover_dimensions(spec); W,H=round(w_in*dpi),round(h_in*dpi); canvas=Image.new("RGB",(W,H),"white")
        spine=round((w_in-2*float(spec.trim_size.split("x")[0]))*dpi); trim_w=round(float(spec.trim_size.split("x")[0])*dpi)
        def fit(img_path,box):
            img=Image.open(img_path).convert("RGB"); target_w,target_h=box; ratio=max(target_w/img.width,target_h/img.height); img=img.resize((round(img.width*ratio),round(img.height*ratio))); left=(img.width-target_w)//2; top=(img.height-target_h)//2; return img.crop((left,top,left+target_w,top+target_h))
        if back: canvas.paste(fit(back,(trim_w,H)),(0,0))
        if front: canvas.paste(fit(front,(trim_w,H)),(W-trim_w,0))
        draw=ImageDraw.Draw(canvas)
        if title:
            try: font=ImageFont.truetype("arial.ttf",max(24,round(W/22)))
            except Exception: font=ImageFont.load_default()
            draw.text((W-trim_w+W//30,H//12),title,fill="black",font=font)
        if author: draw.text((W-trim_w+W//30,H-H//10),author,fill="black")
        out.parent.mkdir(parents=True,exist_ok=True); canvas.save(out,"JPEG",dpi=(dpi,dpi),quality=95); return out
