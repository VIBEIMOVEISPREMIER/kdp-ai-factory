from dataclasses import dataclass, field
from typing import Any

BOOK_TYPES = ["childrens","fiction","educational","workbook","journal","cookbook","study","poetry","notebook","coloring","custom"]
PIPELINE_STAGES = ["brief","outline","manuscript","revision","assets","layout","cover","validation","export"]

@dataclass
class BookSpec:
    title: str
    book_type: str = "custom"
    language: str = "pt-BR"
    audience: str = ""
    description: str = ""
    target_pages: int | None = None
    trim_size: str = "8.5x11"
    bleed: bool = False
    color: bool = True
    extra: dict[str, Any] = field(default_factory=dict)
