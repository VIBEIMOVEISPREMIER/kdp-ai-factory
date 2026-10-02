from __future__ import annotations
from pathlib import Path
from typing import Any
import re

TRIM={"6x9":(6,9),"8x10":(8,10),"8.5x11":(8.5,11),"8x11":(8,11),"7x10":(7,10)}

def parse_trim(trim:str)->tuple[float,float]:
    if trim not in TRIM: raise ValueError(f"Formato não suportado: {trim}")
    return TRIM[trim]

class LayoutEngine:
    def __init__(self,trim_size="8.5x11",bleed=False,margins=0.5):
        self.trim_size=trim_size; self.bleed=bleed; self.margins=margins
    def pdf(self,chapters:list[dict[str,str]],output:Path,title="",author="",interior_images:list[str]|None=None):
        try:
            from reportlab.lib.pagesizes import portrait
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image as RLImage
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError as e: raise RuntimeError("Instale reportlab.") from e
        w,h=parse_trim(self.trim_size); output.parent.mkdir(parents=True,exist_ok=True)
        doc=SimpleDocTemplate(str(output),pagesize=(w*inch,h*inch),rightMargin=self.margins*inch,leftMargin=self.margins*inch,topMargin=self.margins*inch,bottomMargin=self.margins*inch)
        styles=getSampleStyleSheet(); story=[]
        if title: story += [Paragraph(title,styles["Title"]),Spacer(1,30)]
        if author: story += [Paragraph(author,styles["Normal"]),PageBreak()]
        for i,ch in enumerate(chapters):
            story.append(Paragraph(ch.get("title",""),styles["Heading1"]))
            for para in re.split(r"\n\s*\n",ch.get("content","")):
                if para.strip(): story += [Paragraph(para.replace("&","&amp;"),styles["BodyText"]),Spacer(1,8)]
            if interior_images and i < len(interior_images):
                from PIL import Image as PILImage
                image_path=interior_images[i]
                iw,ih=PILImage.open(image_path).size
                maxw=(w-2*self.margins)*inch; maxh=(h-2*self.margins)*inch
                scale=min(maxw/iw,maxh/ih)
                story += [Spacer(1,12),RLImage(image_path,width=iw*scale,height=ih*scale),PageBreak()]
            else:
                story.append(PageBreak())
        # Any remaining selected photos become dedicated interior pages.
        if interior_images and len(interior_images) > len(chapters):
            from PIL import Image as PILImage
            for image_path in interior_images[len(chapters):]:
                iw,ih=PILImage.open(image_path).size
                maxw=(w-2*self.margins)*inch; maxh=(h-2*self.margins)*inch
                scale=min(maxw/iw,maxh/ih)
                story += [RLImage(image_path,width=iw*scale,height=ih*scale),PageBreak()]
        doc.build(story)
        return output