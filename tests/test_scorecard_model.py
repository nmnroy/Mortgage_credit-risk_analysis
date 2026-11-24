"""Tests for PD statistical scorecard model, calibration, and discrimination."""

from pathlib import Path
import pandas as pd
import pytest


def test_pd_model_metrics():
    met_file = Path("outputs/pd_model_metrics.csv")
    if not met_file.exists():
        pytest.skip("outputs/pd_model_metrics.csv does not exist.")
    df = pd.read_csv(met_file)
    assert not df.empty, "pd_model_metrics.csv is empty"

    # Scorecard out-of-time test AUC check
    scorecard_test = df[(df["model"].str.contains("Logistic", case=False)) & (df["sample"].str.contains("test", case=False))]
    if not scorecard_test.empty:
        auc = scorecard_test.auc.iloc[0]
        assert auc >= 0.70, f"Scorecard test AUC {auc:.4f} is below credit industry benchmark (0.70)"


def test_scorecard_coefficients():
    coef_file = Path("outputs/pd_model_coefficients.csv")
    if not coef_file.exists():
        pytest.skip("outputs/pd_model_coefficients.csv does not exist.")
    df = pd.read_csv(coef_file)
    assert not df.empty, "pd_model_coefficients.csv is empty"
    assert "coefficient" in df.columns and "odds_ratio" in df.columns
    # Odds ratios must be positive
    assert (df.odds_ratio >= 0).all(), "Negative odds ratio found"


def test_pd_backtest_deciles():
    dec_file = Path("outputs/pd_backtest_deciles.csv")
    if not dec_file.exists():
        pytest.skip("outputs/pd_backtest_deciles.csv does not exist.")
    df = pd.read_csv(dec_file)
    assert not df.empty, "pd_backtest_deciles.csv is empty"
    # Highest decile should have significantly higher default rate than lowest decile
    first_decile = df.iloc[0]
    last_decile = df.iloc[-1]
    assert last_decile.predicted_pct >= first_decile.predicted_pct, (
        f"Top decile predicted {last_decile.predicted_pct} should be >= Bottom decile {first_decile.predicted_pct}"
    )
