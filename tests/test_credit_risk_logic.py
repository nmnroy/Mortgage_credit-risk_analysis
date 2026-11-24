"""Tests for credit risk principles, roll-rate probabilities, and stress tests."""

from pathlib import Path
import duckdb
import pandas as pd
import pytest


def test_roll_rate_matrix_transition_probabilities():
    rr_file = Path("outputs/roll_rate.csv")
    if not rr_file.exists():
        pytest.skip("outputs/roll_rate.csv does not exist.")
    df = pd.read_csv(rr_file)
    for period in df.period.unique():
        sub = df[df.period == period]
        row_sums = sub.groupby("from_state")["pct"].sum()
        for state, s in row_sums.items():
            # Transitions from each delinquency state should sum to ~100%
            assert 95.0 <= s <= 105.0, f"Roll rate row sum for state {state} in {period} is {s:.2f}%, expected ~100%"


def test_expected_loss_identity():
    el_seg = Path("outputs/el_segment.csv")
    if not el_seg.exists():
        pytest.skip("outputs/el_segment.csv does not exist.")
    df = pd.read_csv(el_seg)
    assert not df.empty, "el_segment.csv is empty"
    assert (df.el_pit_bps >= 0).all(), "Negative expected loss bps encountered"
    assert (df.ead_mn >= 0).all(), "Negative EAD encountered"


def test_stress_test_loss_amplification():
    wf_file = Path("outputs/stress_waterfall.csv")
    if not wf_file.exists():
        pytest.skip("outputs/stress_waterfall.csv does not exist.")
    df = pd.read_csv(wf_file)
    assert len(df) >= 2, "Stress waterfall should contain at least baseline and stressed total"
    base_el = df.el_mn.iloc[0]
    stress_el = df.el_mn.iloc[-1]
    assert stress_el >= base_el, f"Stressed EL ({stress_el}) should be >= Baseline EL ({base_el})"


def test_lgd_summary_ranges():
    lgd_file = Path("outputs/lgd_summary.csv")
    if not lgd_file.exists():
        pytest.skip("outputs/lgd_summary.csv does not exist.")
    df = pd.read_csv(lgd_file)
    assert not df.empty, "lgd_summary.csv is empty"
    assert (df.severity_pct >= 0).all(), "Negative severity percentage detected"
    assert (df.severity_pct <= 100).all(), "Severity percentage > 100% detected"
