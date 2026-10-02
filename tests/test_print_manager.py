from pathlib import Path
import fitz
from PIL import Image

from kdp_factory import print_manager


def test_print_pdf_from_pdf_and_image(monkeypatch, tmp_path):
    project = tmp_path / "project"
    (project / "imports" / "print").mkdir(parents=True)
    pdf_path = project / "imports" / "print" / "apostila.pdf"
    doc = fitz.open()
    page = doc.new_page(width=400, height=600)
    page.insert_text((40, 60), "Página de teste", fontsize=24)
    doc.save(pdf_path)
    doc.close()

    image_path = project / "imports" / "print" / "foto.png"
    Image.new("RGB", (800, 500), "white").save(image_path)

    monkeypatch.setattr("kdp_factory.projects.project_dir", lambda _: project)
    out = print_manager.build_print_pdf(
        "p1",
        [
            {"path": "imports/print/apostila.pdf", "name": "apostila.pdf"},
            {"path": "imports/print/foto.png", "name": "foto.png"},
        ],
        {"paper_size": "A4", "orientation": "portrait", "fit": "contain", "margin_mm": 5, "grayscale": False, "name": "teste"},
    )

    assert out.exists()
    result = fitz.open(out)
    assert result.page_count == 2
    assert abs(result[0].rect.width - 595.276) < 1
    assert abs(result[0].rect.height - 841.89) < 1
    result.close()
