from __future__ import annotations
import json
from pathlib import Path

TYPE_HINTS={
"childrens":("Infantil","história infantil, crianças, aventura, personagens"),
"coloring":("Colorir e atividades","livro de colorir, atividades infantis, desenhos para colorir"),
"fiction":("Ficção","romance, ficção, narrativa, personagens"),
"educational":("Educativo","educação, aprendizagem, atividades educativas"),
"workbook":("Workbook","exercícios, atividades, prática, desenvolvimento"),
"journal":("Diário / Journal","diário, reflexão, planejamento, organização"),
"cookbook":("Culinária","receitas, culinária, gastronomia, cozinha"),
"study":("Estudo / Apostila","estudo, revisão, aprendizagem, apostila"),
"poetry":("Poesia","poesia, poemas, literatura"),
"notebook":("Caderno","caderno, anotações, organização"),
"custom":("Personalizado","livro, publicação, leitura"),
}

class MetadataEngine:
    FIELDS=("title","subtitle","author","contributors","series","edition","description","language","keywords","categories","audience","reading_age_min","reading_age_max","grade","isbn","publication_rights","publisher","trim_size","bleed","page_count","format")

    def generate(self,title,description,language,audience,model=None,book_type="custom",subject="",**extra):
        label,hints=TYPE_HINTS.get(book_type,TYPE_HINTS["custom"])
        topic=subject.strip() or label
        kws=[x.strip() for x in hints.split(",") if x.strip()]
        if topic and topic.lower() not in [x.lower() for x in kws]: kws.insert(0,topic)
        cats=[label]
        data={"title":title,"subtitle":"","author":"","contributors":[],"series":"","edition":"",
              "description":description or f"{title}: publicação de {topic}.",
              "language":language,"keywords":kws[:7],"categories":cats[:3],"audience":audience or label,
              "reading_age_min":None,"reading_age_max":None,"grade":"","isbn":"",
              "publication_rights":"","publisher":"","trim_size":"","bleed":False,"page_count":None,
              "format":"","book_type":book_type,"subject":topic,"ai_generated":True}
        data.update({k:v for k,v in extra.items() if k in self.FIELDS})
        data["notes"]="Revise antes da publicação. Título, subtítulo, autor e série devem corresponder exatamente aos dados da capa; categorias e palavras-chave devem ser relevantes ao conteúdo."
        return data

    def save(self,data,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

    def package(self,data):
        return json.dumps(data,ensure_ascii=False,indent=2)
