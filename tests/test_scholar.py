from pathlib import Path

from coapy.scholar import get_coauthors

def test_scholar(monkeypatch, tmp_path):
  monkeypatch.chdir(tmp_path)
  assert get_coauthors()
  assert Path("coauthors.csv").exists()
