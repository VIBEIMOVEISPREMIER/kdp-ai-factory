from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def _font(size, bold=False):
    candidates=[r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in candidates:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def _fit(draw,text,font,max_width):
    lines=[]; line=""
    for word in (text or "").split():
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=font)[2] <= max_width: line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def create_cover(project_dir:Path,title:str,author:str,description:str,trim_size:str="6x9",pages:int=100,back_image:str|None=None,front_image:str|None=None):
    tw,th=map(float,trim_size.split("x")); spine=max(0.002252*pages,0.06); bleed=.125; dpi=300
    W=int((tw*2+spine+bleed*2)*dpi); H=int((th+bleed*2)*dpi); pagew=int(tw*dpi); pageh=int(th*dpi); top=int(bleed*dpi); backx=top; frontx=top+pagew+int(spine*dpi)
    img=Image.new("RGB",(W,H),(246,242,232)); d=ImageDraw.Draw(img)
    def place(path,x):
        if path and Path(path).exists():
            src=Image.open(path).convert("RGB"); src.thumbnail((pagew,pageh)); img.paste(src,(x+(pagew-src.width)//2,top+(pageh-src.height)//2)); return True
        return False
    if not place(back_image,backx):
        d.rectangle((backx,top,backx+pagew,top+pageh),fill=(236,230,214)); f=_font(50,True); sf=_font(32)
        d.text((backx+80,top+100),"SOBRE O LIVRO",font=f,fill=(35,62,58)); y=top+220
        for line in _fit(d,description or "Uma publicação criada com o KDP AI Factory.",sf,pagew-160)[:14]:
            d.text((backx+80,y),line,font=sf,fill=(45,45,45)); y+=48
    if not place(front_image,frontx):
        d.rectangle((frontx,top,frontx+pagew,top+pageh),fill=(35,62,58)); f=_font(110,True); af=_font(52)
        lines=_fit(d,title,f,int(pagew*.82)); y=top+int(pageh*.25)
        for line in lines:
            bw=d.textbbox((0,0),line,font=f)[2]; d.text((frontx+(pagew-bw)//2,y),line,font=f,fill="white"); y+=125
        if author:
            bw=d.textbbox((0,0),author,font=af)[2]; d.text((frontx+(pagew-bw)//2,top+int(pageh*.82)),author,font=af,fill="white")
    sx=backx+pagew; d.rectangle((sx,top,sx+int(spine*dpi),top+pageh),fill=(35,62,58))
    out=project_dir/"exports"; out.mkdir(parents=True,exist_ok=True)
    full_png=out/"cover_full.png"; full_jpg=out/"cover_full.jpg"; front_png=out/"cover_front.png"; front_jpg=out/"cover_front.jpg"; pdf=out/"cover_full.pdf"
    img.save(full_png,dpi=(dpi,dpi)); img.save(full_jpg,quality=95,dpi=(dpi,dpi))
    front=img.crop((frontx,top,frontx+pagew,top+pageh)); front.save(front_png,dpi=(dpi,dpi)); front.save(front_jpg,quality=95,dpi=(dpi,dpi))
    c=canvas.Canvas(str(pdf),pagesize=(W/dpi*72,H/dpi*72)); c.drawImage(ImageReader(img),0,0,width=W/dpi*72,height=H/dpi*72); c.showPage(); c.save()
    return {"pdf":str(pdf),"png":str(full_png),"jpg":str(full_jpg),"front_png":str(front_png),"front_jpg":str(front_jpg)}
