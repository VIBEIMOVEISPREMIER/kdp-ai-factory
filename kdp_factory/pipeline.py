from .jobs import create_task, update_task
from .ai.ollama import OllamaProvider

DEFAULT_STAGES = [
 ("brief","Briefing"),
 ("outline","Estrutura"),
 ("manuscript","Manuscrito"),
 ("revision","Revisão"),
 ("assets","Imagens e recursos"),
 ("layout","Diagramação"),
 ("cover","Capa"),
 ("validation","Validação"),
 ("export","Exportação")
]

def create_pipeline(project_id):
    return [create_task(project_id, label) for _,label in DEFAULT_STAGES]

def run_text_step(prompt, model=None):
    return OllamaProvider().generate(prompt, model=model)
