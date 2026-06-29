from pathlib import Path

import pandas as pd
from coapy.scholar import get_coauthors


def test_scholar(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert get_coauthors("0000-0002-0141-7006")
    assert Path(tmp_path / "coauthors.xlsx").exists()


def test_coauthors_xlsx_has_multiple_entries(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    get_coauthors("0000-0002-0141-7006")
    df = pd.read_excel(tmp_path / "coauthors.xlsx")
    assert len(df) > 100
