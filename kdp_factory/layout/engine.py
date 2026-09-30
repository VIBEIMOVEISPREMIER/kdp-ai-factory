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
    def pdf(self,chapters:list[dict[str,str]],output:Path,title="",author=""):
        try:
            from reportlab.lib.pagesizes import portrait
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError as e: raise RuntimeError("Instale reportlab.") from e
        w,h=parse_trim(self.trim_size); output.parent.mkdir(parents=True,exist_ok=True)
        doc=SimpleDocTemplate(str(output),pagesize=(w*inch,h*inch),rightMargin=self.margins*inch,leftMargin=self.margins*inch,topMargin=self.margins*inch,bottomMargin=self.margins*inch)
        styles=getSampleStyleSheet(); story=[]
        if title: story += [Paragraph(title,styles["Title"]),Spacer(1,30)]
        if author: story += [Paragraph(author,styles["Normal"]),PageBreak()]
        for ch in chapters:
            story.append(Paragraph(ch.get("title",""),styles["Heading1"]))
            for para in re.split(r"\n\s*\n",ch.get("content","")):
                if para.strip(): story += [Paragraph(para.replace("&","&amp;"),styles["BodyText"]),Spacer(1,8)]
            story.append(PageBreak())
        doc.build(story)
        return output