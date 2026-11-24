"""
Generate synthetic Freddie Mac SFLLD-formatted sample files.

Produces pipe-delimited files matching Freddie Mac Single-Family Loan-Level
Dataset layout (31 origination columns, 35 monthly performance columns) for
vintages 2012, 2016, 2019, 2021, and 2023.

This allows complete local pipeline reproducibility and unit/integration testing
without needing access to the proprietary multi-gigabyte raw files.

Usage:
    python generate_sample_data.py [--loans-per-vintage 500] [--out-dir data/raw]
"""

import argparse
import os
import random
from datetime import datetime
from pathlib import Path


def generate_vintage_data(vintage: int, n_loans: int, raw_dir: Path, seed: int = 42):
    random.seed(seed + vintage)
    orig_file = raw_dir / f"sample_orig_{vintage}.txt"
    perf_file = raw_dir / f"sample_perf_{vintage}.txt"

    states = ["CA", "TX", "FL", "NY", "IL", "PA", "OH", "NC", "MI", "GA", "WA", "CO", "AZ"]
    purposes = ["P", "C", "N"]
    channels = ["R", "B", "C"]
    prop_types = ["SF", "CO", "PU"]
    occupancies = ["P", "I", "S"]

    orig_rows = []
    perf_rows = []

    # Origination date setup
    orig_year = vintage
    orig_month = random.randint(1, 6)
    start_date = datetime(orig_year, orig_month, 1)
    as_of_date = datetime(2026, 3, 1)

    # Base interest rates by vintage
    rate_map = {2012: 3.65, 2016: 3.75, 2019: 3.95, 2021: 2.95, 2023: 6.85}
    base_rate = rate_map.get(vintage, 4.5)

    for i in range(1, n_loans + 1):
        loan_id = f"F{str(vintage)[2:]}Q{random.randint(1,4)}{i:06d}"

        # Borrower risk profile
        fico = int(random.gauss(740, 50))
        fico = max(580, min(850, fico))
        if random.random() < 0.01:
            fico = 9999  # Freddie Mac missing code

        ltv = int(random.gauss(78, 12))
        ltv = max(45, min(105, ltv))

        dti = int(random.gauss(34, 9))
        dti = max(15, min(52, dti))
        if random.random() < 0.02:
            dti = 999

        upb = int(random.gauss(270000, 75000) / 1000) * 1000
        upb = max(60000, min(850000, upb))

        rate = round(base_rate + random.uniform(-0.5, 0.75), 3)
        term = 360
        num_borrowers = 2 if random.random() > 0.45 else 1
        first_time = "Y" if (ltv > 85 and random.random() > 0.4) else "N"
        mi_pct = 0
        if ltv > 80:
            mi_pct = 12 if ltv <= 85 else (25 if ltv <= 90 else 30)

        purpose = random.choice(purposes)
        channel = random.choice(channels)
        prop_state = random.choice(states)
        prop_type = random.choice(prop_types)
        occupancy = random.choices(occupancies, weights=[0.88, 0.08, 0.04])[0]
        postal = f"{random.randint(10000, 99950):05d}"
        msa = f"{random.randint(10000, 48000)}" if random.random() > 0.2 else ""
        first_pay_str = f"{orig_year}{orig_month+1:02d}"
        mat_year = orig_year + (term // 12)
        mat_str = f"{mat_year}{orig_month:02d}"

        # 31 origination columns
        orig_cols = [
            str(fico),                   # 1. credit_score
            first_pay_str,               # 2. first_payment_date
            first_time,                  # 3. first_time_homebuyer
            mat_str,                     # 4. maturity_date
            msa,                         # 5. msa
            str(mi_pct),                 # 6. mi_pct
            "1",                         # 7. num_units
            occupancy,                   # 8. occupancy_status
            str(min(ltv + random.randint(0, 5), 105)), # 9. orig_cltv
            str(dti),                    # 10. orig_dti
            str(upb),                    # 11. orig_upb
            str(ltv),                    # 12. orig_ltv
            str(rate),                   # 13. orig_interest_rate
            channel,                     # 14. channel
            "N",                         # 15. ppm_flag
            "FRM",                       # 16. amortization_type
            prop_state,                  # 17. property_state
            prop_type,                   # 18. property_type
            postal,                      # 19. postal_code
            loan_id,                     # 20. loan_seq_no
            purpose,                     # 21. loan_purpose
            str(term),                   # 22. orig_loan_term
            str(num_borrowers),          # 23. num_borrowers
            "Other sellers",             # 24. seller_name
            "N",                         # 25. super_conforming_flag
            "",                          # 26. pre_harp_loan_seq_no
            "9",                         # 27. program_indicator
            "N",                         # 28. harp_indicator
            "2",                         # 29. property_valuation_method
            "N",                         # 30. interest_only_indicator
            "",                          # 31. orig_unknown_31
        ]
        orig_rows.append("|".join(orig_cols))

        # Monthly performance progression
        cur_date = datetime(orig_year, orig_month + 1, 1)
        cur_upb = float(upb)
        loan_age = 0
        rem_term = term
        dq = 0
        is_active = True
        status_code = ""
        ever_modified = False

        # Loan default / delinquency propensity
        risk_score = 0.0
        if fico < 660:
            risk_score += 0.035
        elif fico < 720:
            risk_score += 0.015
        if ltv > 90:
            risk_score += 0.025
        if dti > 43:
            risk_score += 0.015
        if vintage == 2023:
            risk_score += 0.020  # higher rates and tighter borrower budgets

        # Monthly loop
        while cur_date <= as_of_date and is_active:
            loan_age += 1
            rem_term = max(0, rem_term - 1)
            cur_period_str = cur_date.strftime("%Y%m")

            # COVID Forbearance shock (April 2020 - Dec 2021)
            in_covid = (datetime(2020, 3, 1) <= cur_date <= datetime(2021, 6, 1))
            forb_flag = ""
            if in_covid and random.random() < 0.08:
                forb_flag = "F"
                if random.random() < 0.6:
                    dq = min(6, dq + 1)

            # Delinquency transition simulation
            if not in_covid or forb_flag != "F":
                roll_dice = random.random()
                if dq == 0:
                    if roll_dice < (0.005 + risk_score * 0.4):
                        dq = 1
                elif dq == 1:
                    if roll_dice < 0.55:
                        dq = 0  # cure
                    elif roll_dice < 0.85:
                        dq = 2  # roll forward
                    else:
                        dq = 1  # persist
                elif dq == 2:
                    if roll_dice < 0.30:
                        dq = 1
                    elif roll_dice < 0.75:
                        dq = 3
                    else:
                        dq = 2
                else:  # dq >= 3
                    if roll_dice < 0.15:
                        dq = 2
                    elif roll_dice < 0.25 and not in_covid:
                        # Termination via default
                        status_code = random.choices(["02", "03", "09"], weights=[0.4, 0.3, 0.3])[0]
                        is_active = False
                    else:
                        dq = min(12, dq + 1)

            # Prepayment simulation
            if is_active and dq == 0:
                prep_prob = 0.015 if vintage in (2012, 2016, 2019) and cur_date.year in (2020, 2021) else 0.004
                if random.random() < prep_prob:
                    status_code = "01"
                    is_active = False

            # Amortize UPB slightly each month
            monthly_principal = (upb / term) * (1.0 + 0.002 * loan_age)
            cur_upb = max(0.0, cur_upb - monthly_principal)

            dq_str = f"{dq:02d}"
            is_reo = False
            if dq >= 6 and random.random() < 0.05:
                dq_str = "RA"
                is_reo = True

            zb_code = status_code if not is_active else ""
            zb_date = cur_period_str if not is_active else ""
            zb_upb = f"{cur_upb:.2f}" if not is_active else ""

            # Loss components for defaults
            act_loss = ""
            net_proceeds = ""
            tot_exp = ""
            mi_rec = ""
            if zb_code in ("02", "03", "09"):
                loss_severity = 0.24 + (0.08 if prop_state in ("NY", "FL", "IL") else -0.04)
                loss_amount = round(cur_upb * max(0.05, loss_severity), 2)
                act_loss = str(loss_amount)
                net_proceeds = str(round(cur_upb * (1.0 - loss_severity) * 0.9, 2))
                tot_exp = str(round(cur_upb * 0.08, 2))
                mi_rec = str(round(cur_upb * 0.15, 2)) if mi_pct > 0 else "0"

            # Estimated current LTV (ELTV)
            hpi_factor = 1.0 + (0.04 * (cur_date.year - orig_year))
            est_val = (upb / (ltv / 100.0)) * hpi_factor
            eltv = int(round(100.0 * cur_upb / max(1.0, est_val)))

            # 35 performance columns
            perf_cols = [
                loan_id,                     # 1. loan_seq_no
                cur_period_str,              # 2. reporting_period
                f"{cur_upb:.2f}",            # 3. current_upb
                dq_str,                      # 4. delinquency_status
                str(loan_age),               # 5. loan_age
                str(rem_term),               # 6. remaining_months
                "",                          # 7. defect_settlement_date
                "Y" if ever_modified else "N", # 8. modification_flag
                zb_code,                     # 9. zero_balance_code
                zb_date,                     # 10. zero_balance_date
                str(rate),                   # 11. current_interest_rate
                "0.0",                       # 12. non_interest_bearing_upb
                cur_period_str,              # 13. last_paid_installment_date
                mi_rec,                      # 14. mi_recoveries
                net_proceeds,                # 15. net_sale_proceeds
                "",                          # 16. non_mi_recoveries
                tot_exp,                     # 17. total_expenses
                "",                          # 18. legal_costs
                "",                          # 19. maintenance_costs
                "",                          # 20. taxes_insurance
                "",                          # 21. misc_expenses
                act_loss,                    # 22. actual_loss
                "",                          # 23. cumulative_mod_cost
                "",                          # 24. step_mod_flag
                "",                          # 25. payment_deferral
                str(eltv),                   # 26. eltv
                zb_upb,                      # 27. zero_balance_removal_upb
                "",                          # 28. delinquent_accrued_interest
                "",                          # 29. delinquency_due_to_disaster
                forb_flag,                   # 30. borrower_assistance_status
                "",                          # 31. current_month_mod_cost
                f"{cur_upb:.2f}",            # 32. interest_bearing_upb
                "",                          # 33. mi_cancellation_indicator
                "Other servicers",           # 34. servicer_name
                "",                          # 35. perf_unknown_amount_35
            ]
            perf_rows.append("|".join(perf_cols))

            # Next month
            month_next = cur_date.month + 1
            year_next = cur_date.year
            if month_next > 12:
                month_next = 1
                year_next += 1
            cur_date = datetime(year_next, month_next, 1)

    orig_file.write_text("\n".join(orig_rows) + "\n", encoding="utf-8")
    perf_file.write_text("\n".join(perf_rows) + "\n", encoding="utf-8")
    print(f"  ✓ Vintage {vintage}: {len(orig_rows):,} orig loans, {len(perf_rows):,} monthly perf records")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic sample Freddie Mac SFLLD data")
    parser.add_argument("--loans-per-vintage", type=int, default=500, help="Number of loans per vintage (default: 500)")
    parser.add_argument("--out-dir", type=str, default="data/raw", help="Output directory (default: data/raw)")
    args = parser.parse_args()

    raw_dir = Path(args.out_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[Data Generator] Generating synthetic Freddie Mac loan files in {raw_dir}...")
    vintages = [2012, 2016, 2019, 2021, 2023]
    for v in vintages:
        generate_vintage_data(vintage=v, n_loans=args.loans_per_vintage, raw_dir=raw_dir)

    print(f"\n[Data Generator] Done. Generated 5 vintages ({args.loans_per_vintage * len(vintages):,} loans total) in {raw_dir}\n")


if __name__ == "__main__":
    main()
