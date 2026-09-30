from dataclasses import dataclass,field
from pathlib import Path
import re, math
@dataclass
class ValidationIssue:
    level:str; code:str; message:str; details:dict=field(default_factory=dict)
class KDPValidator:
    TRIM={"6x9":(6,9),"7x10":(7,10),"8x10":(8,10),"8x11":(8,11),"8.5x11":(8.5,11)}
    def validate_spec(self,spec:dict):
        issues=[]; pages=spec.get("pages",spec.get("target_pages"))
        if pages is not None and int(pages)<24: issues.append(ValidationIssue("error","PAGE_COUNT","A especificação tem menos de 24 páginas.",{"pages":pages}))
        trim=spec.get("trim_size")
        if trim not in self.TRIM: issues.append(ValidationIssue("error","TRIM_SIZE","Formato não reconhecido pelo validador.",{"trim_size":trim}))
        if not spec.get("language"): issues.append(ValidationIssue("error","LANGUAGE","Idioma não definido."))
        margins=spec.get("margins",0.5)
        if isinstance(margins,(int,float)) and margins<=0: issues.append(ValidationIssue("error","MARGINS","Margens devem ser positivas."))
        if spec.get("bleed") and trim in self.TRIM and spec.get("bleed_inches",0.125)<=0: issues.append(ValidationIssue("error","BLEED","Bleed configurado com valor inválido."))
        return issues
    def validate_pdf(self,path:str|Path,spec:dict):
        issues=self.validate_spec(spec); p=Path(path)
        if not p.exists(): return issues+[ValidationIssue("error","FILE_MISSING","PDF não encontrado.",{"path":str(p)})]
        try:
            import fitz
            doc=fitz.open(p); pages=len(doc)
            expected=spec.get("target_pages")
            if expected and pages!=expected: issues.append(ValidationIssue("warning","PAGE_COUNT_MISMATCH","Quantidade de páginas difere da meta.",{"actual":pages,"target":expected}))
            if pages<24: issues.append(ValidationIssue("error","PAGE_COUNT","PDF tem menos de 24 páginas.",{"pages":pages}))
            if doc.metadata.get("format") and not str(doc.metadata.get("format")).lower().startswith("pdf"): issues.append(ValidationIssue("warning","METADATA","Metadados PDF incomuns."))
            w,h=doc[0].rect.width/72,doc[0].rect.height/72
            trim=self.TRIM.get(spec.get("trim_size"))
            bleed=0.25 if spec.get("bleed") else 0
            if trim and (abs(w-(trim[0]+bleed))>.03 or abs(h-(trim[1]+bleed))>.03): issues.append(ValidationIssue("error","PAGE_SIZE","Dimensões da página não correspondem à especificação.",{"actual":[round(w,3),round(h,3)],"expected":[trim[0]+bleed,trim[1]+bleed]}))
            for i,page in enumerate(doc):
                if len(page.get_images(full=True))==0: continue
                for img in page.get_images(full=True):
                    xref=img[0]
                    try:
                        pix=fitz.Pixmap(doc,xref); dpi_x=abs(pix.width/page.rect.width*72); dpi_y=abs(pix.height/page.rect.height*72)
                        if max(dpi_x,dpi_y)<150: issues.append(ValidationIssue("warning","LOW_IMAGE_RESOLUTION","Imagem com resolução potencialmente baixa.",{"page":i+1,"dpi":[round(dpi_x),round(dpi_y)]}))
                    except Exception: pass
        except Exception as e: issues.append(ValidationIssue("error","PDF_READ","Não foi possível analisar o PDF.",{"error":str(e)}))
        return issues
def validate(spec:dict,path:str|None=None):
    v=KDPValidator(); return v.validate_pdf(path,spec) if path else v.validate_spec(spec)
