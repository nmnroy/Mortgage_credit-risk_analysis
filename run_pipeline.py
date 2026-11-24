"""
Mortgage Credit Risk Analysis & Stress Testing - End-to-End Pipeline Orchestrator.

Orchestrates all data loading, SQL analytics, PD scorecard modeling, expected
loss estimation, stress testing, and visualization steps.

Usage:
    python run_pipeline.py --all            # Run entire pipeline from data to charts
    python run_pipeline.py --demo           # Generate sample data if needed & run all
    python run_pipeline.py --stage 6        # Run only Stage 6 (Scorecard modeling)
    python run_pipeline.py --plots          # Regenerate all PNG visualizations
    python run_pipeline.py --verify         # Verify outputs and check data integrity
"""

import argparse
import glob
import subprocess
import sys
import time
from pathlib import Path

STAGES = {
    1: {
        "name": "Data Ingestion (Raw Files -> DuckDB)",
        "scripts": ["load_data.py"],
    },
    2: {
        "name": "Data Cleaning Views & Loan Summary Table",
        "scripts": ["clean_views.py", "loan_summary.py"],
    },
    3: {
        "name": "Delinquency Dynamics, Vintage Curves & Roll Rates",
        "scripts": [
            "vintage_curves.py",
            "plot_vintage_curves.py",
            "calendar_d90.py",
            "roll_rate.py",
        ],
    },
    4: {
        "name": "Risk Drivers, FICO x LTV Matrix & LGD Estimation",
        "scripts": [
            "risk_drivers.py",
            "plot_risk_drivers.py",
            "lgd.py",
        ],
    },
    5: {
        "name": "Segment PD, Expected Loss & Fed Stress Testing",
        "scripts": [
            "pd_model.py",
            "expected_loss.py",
            "stress_test.py",
            "plot_stress.py",
        ],
    },
    6: {
        "name": "Statistical PD Scorecard & Out-of-Time Backtesting",
        "scripts": [
            "pd_features.py",
            "pd_logit.py",
            "pd_backtest.py",
            "el_scorecard.py",
        ],
    },
    7: {
        "name": "Tableau & BI Reporting Prep",
        "scripts": ["tableau_prep.py"],
    },
}

PLOT_SCRIPTS = [
    "plot_vintage_curves.py",
    "calendar_d90.py",
    "plot_risk_drivers.py",
    "plot_stress.py",
]

EXPECTED_OUTPUTS = [
    "outputs/vintage_curves.csv",
    "outputs/vintage_curves.png",
    "outputs/calendar_d90.csv",
    "outputs/calendar_d90.png",
    "outputs/roll_rate.csv",
    "outputs/risk_drivers.csv",
    "outputs/risk_drivers_lift.png",
    "outputs/risk_grid.csv",
    "outputs/risk_grid_heatmap.png",
    "outputs/lgd_summary.csv",
    "outputs/pd_segment.csv",
    "outputs/el_segment.csv",
    "outputs/el_vintage.csv",
    "outputs/stress_waterfall.csv",
    "outputs/stress_waterfall.png",
    "outputs/stress_vintage.csv",
    "outputs/stress_vintage.png",
    "outputs/stress_sensitivity.csv",
    "outputs/pd_model_coefficients.csv",
    "outputs/pd_model_metrics.csv",
    "outputs/pd_backtest_deciles.csv",
    "outputs/pd_backtest_time.csv",
    "outputs/pd_backtest_time.png",
    "outputs/pd_calibration.png",
    "outputs/el_scorecard_summary.csv",
    "outputs/el_scorecard_vintage.csv",
    "outputs/tableau/tableau_data.xlsx",
]


def run_script(script_name: str) -> bool:
    print(f"  ▶ Running {script_name}...")
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True,
        )
        elapsed = time.time() - t0
        print(f"  ✓ {script_name} completed in {elapsed:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - t0
        print(f"  ✗ {script_name} FAILED after {elapsed:.2f}s (Exit code {e.returncode})")
        if e.stdout:
            print("--- Standard Output ---")
            print(e.stdout[-800:] if len(e.stdout) > 800 else e.stdout)
        if e.stderr:
            print("--- Error Output ---")
            print(e.stderr[-800:] if len(e.stderr) > 800 else e.stderr)
        return False


def verify_outputs():
    print("\n" + "=" * 60)
    print("Verifying Pipeline Outputs in outputs/")
    print("=" * 60)
    found = 0
    missing = 0
    for out in EXPECTED_OUTPUTS:
        p = Path(out)
        if p.exists():
            size_kb = p.stat().st_size / 1024
            print(f"  ✓ {out:<38} ({size_kb:>7.1f} KB)")
            found += 1
        else:
            print(f"  ✗ {out:<38} (MISSING)")
            missing += 1

    print("-" * 60)
    print(f"Outputs Check: {found}/{len(EXPECTED_OUTPUTS)} verified. {missing} missing.")
    return missing == 0


def ensure_data():
    raw_files = list(glob.glob("data/raw/sample_orig_*.txt"))
    if not raw_files:
        print("[Setup] No raw data files detected in data/raw/.")
        print("[Setup] Generating synthetic Freddie Mac SFLLD dataset for demo/testing...")
        run_script("generate_sample_data.py")


def main():
    parser = argparse.ArgumentParser(description="End-to-End Mortgage Credit Risk Pipeline Runner")
    parser.add_argument("--all", action="store_true", help="Run full pipeline end-to-end")
    parser.add_argument("--demo", action="store_true", help="Generate sample data if needed and run all")
    parser.add_argument("--stage", type=int, choices=range(1, 8), help="Run specific stage (1 to 7)")
    parser.add_argument("--plots", action="store_true", help="Regenerate all figures/plots")
    parser.add_argument("--verify", action="store_true", help="Verify all expected output files")
    args = parser.parse_args()

    if not any([args.all, args.demo, args.stage, args.plots, args.verify]):
        parser.print_help()
        sys.exit(0)

    start_all = time.time()

    if args.verify:
        ok = verify_outputs()
        sys.exit(0 if ok else 1)

    if args.plots:
        print("\n" + "=" * 60)
        print("Regenerating Visualizations from Processed Outputs")
        print("=" * 60)
        success = True
        for s in PLOT_SCRIPTS:
            if not run_script(s):
                success = False
        print(f"\nCompleted in {time.time() - start_all:.2f}s")
        sys.exit(0 if success else 1)

    if args.demo:
        ensure_data()

    stages_to_run = [args.stage] if args.stage else range(1, 8)

    print("\n" + "=" * 60)
    print("Mortgage Credit Risk Pipeline Execution")
    print("=" * 60)

    for stg in stages_to_run:
        meta = STAGES[stg]
        print(f"\n[Stage {stg}] {meta['name']}")
        print("-" * 60)
        for s in meta["scripts"]:
            if not run_script(s):
                print(f"\n[PIPELINE HALTED] Failed at Stage {stg}: {s}")
                sys.exit(1)

    print("\n" + "=" * 60)
    print(f"Pipeline executed successfully in {time.time() - start_all:.2f}s!")
    print("=" * 60)
    verify_outputs()


if __name__ == "__main__":
    main()
