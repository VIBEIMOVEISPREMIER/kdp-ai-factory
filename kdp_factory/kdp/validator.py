from dataclasses import dataclass,field
@dataclass
class ValidationIssue:
 level:str
 code:str
 message:str
 details:dict=field(default_factory=dict)
class KDPValidator:
 def validate_spec(self,spec:dict):
  issues=[]
  pages=spec.get("pages")
  if pages is not None and pages<24: issues.append(ValidationIssue("error","PAGE_COUNT","Número de páginas abaixo do mínimo configurado.",{"pages":pages}))
  if not spec.get("trim_size"): issues.append(ValidationIssue("error","TRIM_SIZE","Tamanho do livro não definido."))
  if not spec.get("language"): issues.append(ValidationIssue("error","LANGUAGE","Idioma não definido."))
  return issues
