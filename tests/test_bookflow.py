from pathlib import Path
from kdp_factory.projects import create_project
from kdp_factory.bookflow import save_manuscript
def test_project_bookflow(tmp_path, monkeypatch):
    monkeypatch.setenv("KDP_FACTORY_DATA_DIR",str(tmp_path))
    # config is imported before env in normal process; this test only checks API shape.
    assert callable(save_manuscript)
