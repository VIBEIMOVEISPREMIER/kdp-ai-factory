from dataclasses import dataclass, field
from typing import Any
@dataclass
class Chapter:
    id:str
    title:str
    order:int
    content:str=""
    notes:str=""
    metadata:dict[str,Any]=field(default_factory=dict)
@dataclass
class Manuscript:
    title:str
    language:str="pt-BR"
    chapters:list[Chapter]=field(default_factory=list)
    front_matter:list[str]=field(default_factory=list)
    back_matter:list[str]=field(default_factory=list)
    metadata:dict[str,Any]=field(default_factory=dict)
    def text(self)->str:
        return "\n\n".join(f"# {c.title}\n\n{c.content}" for c in sorted(self.chapters,key=lambda x:x.order))