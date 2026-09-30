from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..kdp.cover import CoverSpec, cover_dimensions, spine_width

class CoverBuilder:
    def build(self,spec:CoverSpec,out:Path,front:Path|None=None,back:Path|None=None,title="",author="",dpi=300):
        w_in,h_in=cover_dimensions(spec); W,H=round(w_in*dpi),round(h_in*dpi)
        canvas=Image.new("RGB",(W,H),"white")
        trim_w=round(float(spec.trim_size.split("x")[0])*dpi)
        spine_px=round(spine_width(spec.pages,spec.paper)*dpi)
        def fit(path,tw,th):
            img=Image.open(path).convert("RGB"); ratio=max(tw/img.width,th/img.height)
            img=img.resize((round(img.width*ratio),round(img.height*ratio)))
            l=max(0,(img.width-tw)//2); t=max(0,(img.height-th)//2); return img.crop((l,t,l+tw,t+th))
        if back: canvas.paste(fit(back,trim_w,H),(0,0))
        if front: canvas.paste(fit(front,trim_w,H),(W-trim_w,0))
        draw=ImageDraw.Draw(canvas)
        try: font=ImageFont.truetype("arial.ttf",max(36,round(W/25)))
        except Exception: font=ImageFont.load_default()
        if title: draw.text((W-trim_w+W//30,H//12),title,fill="black",font=font)
        if author: draw.text((W-trim_w+W//30,H-H//10),author,fill="black",font=font)
        if spine_px>0: draw.line((trim_w,0,trim_w,H),fill="gray",width=2); draw.line((trim_w+spine_px,0,trim_w+spine_px,H),fill="gray",width=2)
        out.parent.mkdir(parents=True,exist_ok=True); canvas.save(out,"JPEG",dpi=(dpi,dpi),quality=95); return out
