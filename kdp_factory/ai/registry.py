from .router import AIRouter

class Registry:
    def __init__(self):
        self.router=AIRouter()
        self.text=self.router
        self.image=self.router
    def configure_remote(self,url:str,token:str=""):
        self.router.configure_remote(url,token)
    def status(self):
        return self.router.status()
registry=Registry()
def providers(): return {"text":registry.router,"image":registry.router}
def status(): return registry.status()
