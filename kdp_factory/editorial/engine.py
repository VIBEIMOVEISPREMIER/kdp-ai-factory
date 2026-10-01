from __future__ import annotations
import json, uuid
from pathlib import Path
from .models import Manuscript, Chapter
from ..ai.registry import registry

class EditorialEngine:
    def __init__(self, provider=None):
        self.provider=provider or registry.router
    def outline(self, brief:str, chapters:int=10, model:str|None=None)->dict:
        prompt=f"Crie uma estrutura editorial profissional para um livro. Briefing:\n{brief}\nQuantidade aproximada de capítulos: {chapters}. Responda em JSON com title e chapters, cada capítulo com title e purpose."
        raw=self.provider.generate(prompt,model).text
        try: return json.loads(raw)
        except Exception: return {"title":"","chapters":[{"title":f"Capítulo {i+1}","purpose":""} for i in range(chapters)],"raw":raw}
    def write_chapter(self, title:str, purpose:str, context:str="", model:str|None=None)->str:
        prompt=f"Escreva um capítulo original em português brasileiro. Título: {title}. Objetivo: {purpose}. Contexto: {context}\nUse estrutura clara, coerência, transições e não invente fontes."
        return self.provider.generate(prompt,model).text
    def revise(self,text:str,instructions:str,model:str|None=None)->str:
        return self.provider.generate(f"Revise o texto abaixo conforme as instruções, preservando fatos e intenção.\nInstruções: {instructions}\n\nTEXTO:\n{text}",model).text
    def translate(self,text:str,target_language:str,model:str|None=None)->str:
        return self.provider.generate(f"Traduza o texto integralmente para {target_language}, preservando estrutura, sentido e nomes próprios.\n\n{text}",model).text
    def save(self,manuscript:Manuscript,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({"title":manuscript.title,"language":manuscript.language,"chapters":[c.__dict__ for c in manuscript.chapters],"front_matter":manuscript.front_matter,"back_matter":manuscript.back_matter,"metadata":manuscript.metadata},ensure_ascii=False,indent=2),encoding="utf-8")