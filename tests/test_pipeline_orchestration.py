"""Tests for pipeline orchestrator verification and outputs check."""

import subprocess
import sys
from pathlib import Path


def test_run_pipeline_verify_flag():
    proc = subprocess.run(
        [sys.executable, "run_pipeline.py", "--verify"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"run_pipeline.py --verify failed:\n{proc.stdout}\n{proc.stderr}"
    assert "Outputs Check:" in proc.stdout
    assert "0 missing" in proc.stdout


def test_tableau_excel_structure():
    excel_path = Path("outputs/tableau/tableau_data.xlsx")
    assert excel_path.exists(), "tableau_data.xlsx was not generated"
    import openpyxl
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    expected_sheets = ["kpi", "trend", "vintage_curves", "calendar_d90", "risk_grid", "el_vintage", "stress_waterfall", "stress_vintage", "roll_rate"]
    for s in expected_sheets:
        assert s in wb.sheetnames, f"Sheet '{s}' missing from {excel_path}"
    wb.close()
