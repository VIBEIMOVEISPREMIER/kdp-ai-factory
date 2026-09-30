from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class AIResponse:
    text: str = ""
    raw: Any = None
    model: str = ""

class TextProvider(ABC):
    name = "abstract"
    @abstractmethod
    def available(self) -> bool: ...
    @abstractmethod
    def models(self) -> list[str]: ...
    @abstractmethod
    def generate(self, prompt: str, model: str | None = None, **kwargs) -> AIResponse: ...

class ImageProvider(ABC):
    name = "abstract"
    @abstractmethod
    def available(self) -> bool: ...
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Any: ...
