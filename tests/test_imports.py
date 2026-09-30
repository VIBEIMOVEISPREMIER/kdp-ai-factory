from pathlib import Path
from kdp_factory.imports.engine import import_file, normalize_to_text
def test_txt_import(tmp_path:Path):
    p=tmp_path/"book.txt"; p.write_text("Olá\n\nMundo",encoding="utf-8")
    d=import_file(p); assert d["type"]=="text"; assert "Mundo" in normalize_to_text(d)
