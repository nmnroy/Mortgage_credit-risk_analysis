"""Tests for data integrity, DuckDB table views, and missing value imputation."""

from pathlib import Path
import duckdb
import pytest

DB_PATH = "mortgage.duckdb"


@pytest.fixture(scope="module")
def db_conn():
    if not Path(DB_PATH).exists():
        pytest.skip(f"{DB_PATH} not found. Run pipeline or generator first.")
    con = duckdb.connect(DB_PATH, read_only=True)
    yield con
    con.close()


def test_required_views_and_tables_exist(db_conn):
    tables = [r[0] for r in db_conn.execute("SELECT table_name FROM information_schema.tables").fetchall()]
    expected = ["orig", "perf", "orig_clean", "perf_clean", "loan_summary"]
    for t in expected:
        assert t in tables, f"Expected table or view '{t}' was not found in DuckDB."


def test_loan_summary_row_counts_and_keys(db_conn):
    res = db_conn.execute("""
        SELECT COUNT(*) AS total_rows,
               COUNT(DISTINCT loan_seq_no) AS distinct_loans,
               COUNT(*) - COUNT(loan_seq_no) AS null_keys
        FROM loan_summary
    """).fetchone()
    total_rows, distinct_loans, null_keys = res
    assert total_rows > 0, "loan_summary is empty"
    assert total_rows == distinct_loans, "Duplicate loan_seq_no found in loan_summary"
    assert null_keys == 0, "Null loan_seq_no found in loan_summary"


def test_orig_clean_ranges(db_conn):
    res = db_conn.execute("""
        SELECT MIN(credit_score) AS min_fico, MAX(credit_score) AS max_fico,
               MIN(orig_ltv) AS min_ltv, MAX(orig_ltv) AS max_ltv,
               MIN(orig_dti) AS min_dti, MAX(orig_dti) AS max_dti
        FROM orig_clean
        WHERE credit_score IS NOT NULL
    """).fetchone()
    min_fico, max_fico, min_ltv, max_ltv, min_dti, max_dti = res
    assert 300 <= min_fico <= 850, f"Min FICO out of bounds: {min_fico}"
    assert 300 <= max_fico <= 850, f"Max FICO out of bounds: {max_fico}"
    assert 1 <= min_ltv <= 200, f"Min LTV out of bounds: {min_ltv}"
    assert 1 <= min_dti <= 100, f"Min DTI out of bounds: {min_dti}"


def test_delinquency_logic_in_perf_clean(db_conn):
    res = db_conn.execute("""
        SELECT COUNT(*) FROM perf_clean
        WHERE dq_months < 0
    """).fetchone()[0]
    assert res == 0, "Negative delinquency months detected in perf_clean"
