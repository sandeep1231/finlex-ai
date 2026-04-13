import json
from typing import Optional

from langchain_core.tools import tool


INCOME_TAX_SLABS_NEW_REGIME = [
    {"min": 0, "max": 400000, "rate": 0},
    {"min": 400001, "max": 800000, "rate": 5},
    {"min": 800001, "max": 1200000, "rate": 10},
    {"min": 1200001, "max": 1600000, "rate": 15},
    {"min": 1600001, "max": 2000000, "rate": 20},
    {"min": 2000001, "max": 2400000, "rate": 25},
    {"min": 2400001, "max": None, "rate": 30},
]

INCOME_TAX_SLABS_OLD_REGIME = {
    "below_60": [
        {"min": 0, "max": 250000, "rate": 0},
        {"min": 250001, "max": 500000, "rate": 5},
        {"min": 500001, "max": 1000000, "rate": 20},
        {"min": 1000001, "max": None, "rate": 30},
    ],
    "60_to_80": [
        {"min": 0, "max": 300000, "rate": 0},
        {"min": 300001, "max": 500000, "rate": 5},
        {"min": 500001, "max": 1000000, "rate": 20},
        {"min": 1000001, "max": None, "rate": 30},
    ],
    "above_80": [
        {"min": 0, "max": 500000, "rate": 0},
        {"min": 500001, "max": 1000000, "rate": 20},
        {"min": 1000001, "max": None, "rate": 30},
    ],
}

SURCHARGE_NEW_REGIME = [
    {"min": 0, "max": 5000000, "rate": 0},
    {"min": 5000001, "max": 10000000, "rate": 10},
    {"min": 10000001, "max": 20000000, "rate": 15},
    {"min": 20000001, "max": None, "rate": 25},
]

SURCHARGE_OLD_REGIME = [
    {"min": 0, "max": 5000000, "rate": 0},
    {"min": 5000001, "max": 10000000, "rate": 10},
    {"min": 10000001, "max": 20000000, "rate": 15},
    {"min": 20000001, "max": 50000000, "rate": 25},
    {"min": 50000001, "max": None, "rate": 37},
]

CESS_RATE = 4  # Health & Education Cess


def _compute_slab_tax(taxable_income: float, slabs: list[dict]) -> float:
    """Compute tax based on slab rates."""
    tax = 0.0
    for slab in slabs:
        slab_min = slab["min"]
        slab_max = slab["max"]
        rate = slab["rate"]

        if taxable_income <= 0:
            break

        if slab_max is None:
            taxable_in_slab = max(0, taxable_income - slab_min + 1)
        else:
            taxable_in_slab = max(0, min(taxable_income, slab_max) - slab_min + 1)

        tax += taxable_in_slab * rate / 100

    return tax


def _get_surcharge(total_income: float, base_tax: float, surcharge_slabs: list[dict]) -> float:
    """Compute surcharge with marginal relief."""
    surcharge_rate = 0
    for slab in surcharge_slabs:
        if slab["max"] is None or total_income <= slab["max"]:
            surcharge_rate = slab["rate"]
            break
        surcharge_rate = slab["rate"]

    return base_tax * surcharge_rate / 100


@tool
def calculate_income_tax(
    gross_income: float,
    regime: str = "new",
    age_category: str = "below_60",
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    deductions_80ccd_1b: float = 0,
    hra_exemption: float = 0,
    home_loan_interest: float = 0,
    other_deductions: float = 0,
    is_salaried: bool = True,
) -> str:
    """Calculate Indian income tax for FY 2025-26 (AY 2026-27) under Old or New Regime.

    Args:
        gross_income: Total gross income in INR.
        regime: Tax regime - 'new' (default) or 'old'.
        age_category: Age category - 'below_60', '60_to_80', or 'above_80'. Used for Old Regime.
        deductions_80c: Deductions under Section 80C (max ₹1,50,000). Old Regime only.
        deductions_80d: Deductions under Section 80D (medical insurance). Old Regime only.
        deductions_80ccd_1b: Additional NPS deduction under 80CCD(1B) (max ₹50,000). Old Regime only.
        hra_exemption: HRA exemption amount. Old Regime only.
        home_loan_interest: Home loan interest deduction u/s 24(b) (max ₹2,00,000 self-occupied). Old Regime only.
        other_deductions: Any other deductions. Old Regime only.
        is_salaried: Whether the person is salaried (affects standard deduction).

    Returns:
        Detailed tax computation as a formatted string.
    """
    result_lines = [
        f"## Income Tax Computation — FY 2025-26 (AY 2026-27)",
        f"**Regime**: {'New Regime (Section 115BAC)' if regime == 'new' else 'Old Regime'}",
        f"**Gross Income**: ₹{gross_income:,.0f}",
        "",
    ]

    if regime == "new":
        standard_deduction = 75000 if is_salaried else 0
        taxable_income = max(0, gross_income - standard_deduction)

        result_lines.append(f"**Standard Deduction**: ₹{standard_deduction:,.0f}")
        result_lines.append(f"**Taxable Income**: ₹{taxable_income:,.0f}")
        result_lines.append("")

        base_tax = _compute_slab_tax(taxable_income, INCOME_TAX_SLABS_NEW_REGIME)

        # Rebate u/s 87A for new regime
        rebate = 0
        if taxable_income <= 1200000:
            rebate = min(base_tax, 60000)

        tax_after_rebate = max(0, base_tax - rebate)
        surcharge = _get_surcharge(taxable_income, tax_after_rebate, SURCHARGE_NEW_REGIME)
        cess = (tax_after_rebate + surcharge) * CESS_RATE / 100
        total_tax = tax_after_rebate + surcharge + cess

        result_lines.extend([
            "### Slab-wise Computation (New Regime):",
            "| Income Slab | Rate | Tax |",
            "|---|---|---|",
            f"| Up to ₹4,00,000 | 0% | ₹0 |",
            f"| ₹4,00,001 – ₹8,00,000 | 5% | ₹{min(max(0, min(taxable_income, 800000) - 400000), 400000) * 5 / 100:,.0f} |",
            f"| ₹8,00,001 – ₹12,00,000 | 10% | ₹{max(0, min(max(0, taxable_income - 800000), 400000)) * 10 / 100:,.0f} |",
            f"| ₹12,00,001 – ₹16,00,000 | 15% | ₹{max(0, min(max(0, taxable_income - 1200000), 400000)) * 15 / 100:,.0f} |",
            f"| ₹16,00,001 – ₹20,00,000 | 20% | ₹{max(0, min(max(0, taxable_income - 1600000), 400000)) * 20 / 100:,.0f} |",
            f"| ₹20,00,001 – ₹24,00,000 | 25% | ₹{max(0, min(max(0, taxable_income - 2000000), 400000)) * 25 / 100:,.0f} |",
            f"| Above ₹24,00,000 | 30% | ₹{max(0, taxable_income - 2400000) * 30 / 100:,.0f} |",
            "",
            f"**Base Tax**: ₹{base_tax:,.0f}",
            f"**Rebate u/s 87A**: ₹{rebate:,.0f}" + (" (income ≤ ₹12L)" if rebate > 0 else ""),
            f"**Tax after Rebate**: ₹{tax_after_rebate:,.0f}",
            f"**Surcharge**: ₹{surcharge:,.0f}",
            f"**Health & Education Cess (4%)**: ₹{cess:,.0f}",
            f"### **Total Tax Liability: ₹{total_tax:,.0f}**",
        ])

    else:  # old regime
        standard_deduction = 50000 if is_salaried else 0
        capped_80c = min(deductions_80c, 150000)
        capped_80d = min(deductions_80d, 100000)
        capped_80ccd_1b = min(deductions_80ccd_1b, 50000)
        capped_home_loan = min(home_loan_interest, 200000)

        total_deductions = (
            standard_deduction + capped_80c + capped_80d +
            capped_80ccd_1b + hra_exemption + capped_home_loan + other_deductions
        )
        taxable_income = max(0, gross_income - total_deductions)

        result_lines.extend([
            "### Deductions Breakdown:",
            f"| Deduction | Amount |",
            f"|---|---|",
            f"| Standard Deduction | ₹{standard_deduction:,.0f} |",
            f"| Section 80C | ₹{capped_80c:,.0f} |",
            f"| Section 80D | ₹{capped_80d:,.0f} |",
            f"| Section 80CCD(1B) NPS | ₹{capped_80ccd_1b:,.0f} |",
            f"| HRA Exemption | ₹{hra_exemption:,.0f} |",
            f"| Home Loan Interest 24(b) | ₹{capped_home_loan:,.0f} |",
            f"| Other Deductions | ₹{other_deductions:,.0f} |",
            f"| **Total Deductions** | **₹{total_deductions:,.0f}** |",
            "",
            f"**Taxable Income**: ₹{taxable_income:,.0f}",
            "",
        ])

        slabs = INCOME_TAX_SLABS_OLD_REGIME.get(age_category, INCOME_TAX_SLABS_OLD_REGIME["below_60"])
        base_tax = _compute_slab_tax(taxable_income, slabs)

        # Rebate u/s 87A for old regime
        rebate = 0
        if taxable_income <= 500000:
            rebate = min(base_tax, 12500)

        tax_after_rebate = max(0, base_tax - rebate)
        surcharge = _get_surcharge(taxable_income, tax_after_rebate, SURCHARGE_OLD_REGIME)
        cess = (tax_after_rebate + surcharge) * CESS_RATE / 100
        total_tax = tax_after_rebate + surcharge + cess

        result_lines.extend([
            f"**Base Tax**: ₹{base_tax:,.0f}",
            f"**Rebate u/s 87A**: ₹{rebate:,.0f}" + (" (income ≤ ₹5L)" if rebate > 0 else ""),
            f"**Tax after Rebate**: ₹{tax_after_rebate:,.0f}",
            f"**Surcharge**: ₹{surcharge:,.0f}",
            f"**Health & Education Cess (4%)**: ₹{cess:,.0f}",
            f"### **Total Tax Liability: ₹{total_tax:,.0f}**",
        ])

    result_lines.append("")
    result_lines.append("*Disclaimer: This is an indicative computation. Please verify with a qualified CA.*")
    return "\n".join(result_lines)


@tool
def compare_tax_regimes(
    gross_income: float,
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    deductions_80ccd_1b: float = 0,
    hra_exemption: float = 0,
    home_loan_interest: float = 0,
    other_deductions: float = 0,
    is_salaried: bool = True,
) -> str:
    """Compare income tax under Old and New Regime to recommend the better option.

    Args:
        gross_income: Total gross income in INR.
        deductions_80c: Deductions under Section 80C (max ₹1,50,000).
        deductions_80d: Deductions under Section 80D.
        deductions_80ccd_1b: Additional NPS deduction under 80CCD(1B).
        hra_exemption: HRA exemption amount.
        home_loan_interest: Home loan interest deduction u/s 24(b).
        other_deductions: Any other deductions.
        is_salaried: Whether the person is salaried.

    Returns:
        Comparison of tax under both regimes with recommendation.
    """
    new_result = calculate_income_tax.invoke({
        "gross_income": gross_income, "regime": "new", "is_salaried": is_salaried,
    })
    old_result = calculate_income_tax.invoke({
        "gross_income": gross_income, "regime": "old", "is_salaried": is_salaried,
        "deductions_80c": deductions_80c, "deductions_80d": deductions_80d,
        "deductions_80ccd_1b": deductions_80ccd_1b, "hra_exemption": hra_exemption,
        "home_loan_interest": home_loan_interest, "other_deductions": other_deductions,
    })

    # Extract tax amounts from results
    def _extract_tax(result_text: str) -> float:
        for line in result_text.split("\n"):
            if "Total Tax Liability" in line:
                amount_str = line.split("₹")[-1].replace(",", "").replace("*", "").strip()
                try:
                    return float(amount_str)
                except ValueError:
                    return 0.0
        return 0.0

    new_tax = _extract_tax(new_result)
    old_tax = _extract_tax(old_result)
    savings = abs(new_tax - old_tax)

    recommendation = "New Regime" if new_tax <= old_tax else "Old Regime"

    return (
        f"## Tax Regime Comparison — FY 2025-26\n\n"
        f"| Regime | Total Tax |\n|---|---|\n"
        f"| New Regime | ₹{new_tax:,.0f} |\n"
        f"| Old Regime | ₹{old_tax:,.0f} |\n\n"
        f"### Recommendation: **{recommendation}** saves ₹{savings:,.0f}\n\n"
        f"---\n\n### New Regime Details:\n{new_result}\n\n"
        f"---\n\n### Old Regime Details:\n{old_result}"
    )


@tool
def calculate_tds(
    payment_amount: float,
    section: str,
    payee_type: str = "individual",
    pan_available: bool = True,
) -> str:
    """Calculate TDS (Tax Deducted at Source) for a given payment.

    Args:
        payment_amount: Amount of payment in INR.
        section: TDS section (e.g., '194C', '194J', '194I', '194H', '194A').
        payee_type: Type of payee - 'individual' or 'company'.
        pan_available: Whether the payee has provided PAN.

    Returns:
        TDS computation with applicable rate and amount.
    """
    TDS_RATES = {
        "192": {"threshold": 250000, "individual": "slab", "company": "slab", "desc": "Salary"},
        "194A": {"threshold": 50000, "individual": 10, "company": 10, "desc": "Interest (bank/PO)"},
        "194B": {"threshold": 10000, "individual": 30, "company": 30, "desc": "Lottery/game winnings"},
        "194BA": {"threshold": 0, "individual": 30, "company": 30, "desc": "Online gaming winnings"},
        "194C": {"threshold": 30000, "individual": 1, "company": 2, "desc": "Contractor payment"},
        "194D": {"threshold": 20000, "individual": 5, "company": 10, "desc": "Insurance commission"},
        "194H": {"threshold": 20000, "individual": 2, "company": 2, "desc": "Commission/brokerage"},
        "194I_land": {"threshold": 600000, "individual": 10, "company": 10, "desc": "Rent (land/building)"},
        "194I_plant": {"threshold": 600000, "individual": 2, "company": 2, "desc": "Rent (plant/machinery)"},
        "194IA": {"threshold": 5000000, "individual": 1, "company": 1, "desc": "Property transfer"},
        "194IB": {"threshold": 50000, "individual": 2, "company": None, "desc": "Rent by individual/HUF"},
        "194J": {"threshold": 50000, "individual": 10, "company": 10, "desc": "Professional/technical fees"},
        "194K": {"threshold": 10000, "individual": 10, "company": 10, "desc": "Mutual fund dividend"},
        "194N": {"threshold": 10000000, "individual": 2, "company": 2, "desc": "Cash withdrawal"},
        "194O": {"threshold": 500000, "individual": 0.1, "company": 0.1, "desc": "E-commerce payment"},
        "194Q": {"threshold": 5000000, "individual": 0.1, "company": 0.1, "desc": "Purchase of goods"},
        "194R": {"threshold": 20000, "individual": 10, "company": 10, "desc": "Perquisite/benefit"},
        "194S": {"threshold": 50000, "individual": 1, "company": 1, "desc": "Crypto/VDA transfer"},
        "194T": {"threshold": 20000, "individual": None, "company": 10, "desc": "Partner payment from firm"},
    }

    section_clean = section.upper().replace("SEC ", "").replace("SECTION ", "").strip()
    rate_info = TDS_RATES.get(section_clean)

    if not rate_info:
        return f"Section {section} not found in TDS rate chart. Available sections: {', '.join(TDS_RATES.keys())}"

    threshold = rate_info["threshold"]
    rate_key = "individual" if payee_type == "individual" else "company"
    rate = rate_info.get(rate_key)

    if rate is None:
        return f"Section {section_clean} is not applicable for {payee_type}."

    if rate == "slab":
        return f"TDS under Section {section_clean} ({rate_info['desc']}) is deducted at applicable slab rates. Use the income tax calculator for computation."

    if payment_amount < threshold:
        return (
            f"## TDS Computation — Section {section_clean}\n"
            f"**Nature**: {rate_info['desc']}\n"
            f"**Payment Amount**: ₹{payment_amount:,.0f}\n"
            f"**Threshold**: ₹{threshold:,.0f}\n\n"
            f"**No TDS applicable** — payment is below the threshold of ₹{threshold:,.0f}."
        )

    effective_rate = rate
    if not pan_available:
        effective_rate = max(rate * 2, 20)

    tds_amount = payment_amount * effective_rate / 100
    net_payment = payment_amount - tds_amount

    return (
        f"## TDS Computation — Section {section_clean}\n\n"
        f"| Parameter | Value |\n|---|---|\n"
        f"| Nature | {rate_info['desc']} |\n"
        f"| Payment Amount | ₹{payment_amount:,.0f} |\n"
        f"| Threshold | ₹{threshold:,.0f} |\n"
        f"| Payee Type | {payee_type.title()} |\n"
        f"| PAN Available | {'Yes' if pan_available else 'No'} |\n"
        f"| TDS Rate | {effective_rate}%{' (higher rate — no PAN)' if not pan_available else ''} |\n"
        f"| **TDS Amount** | **₹{tds_amount:,.0f}** |\n"
        f"| Net Payment | ₹{net_payment:,.0f} |\n\n"
        f"**TDS Payment Due**: 7th of the following month\n\n"
        f"*Disclaimer: Verify rates with the latest CBDT notifications.*"
    )


@tool
def calculate_advance_tax(
    estimated_annual_tax: float,
    tax_already_paid: float = 0,
    current_quarter: int = 1,
) -> str:
    """Calculate advance tax installments for the financial year.

    Args:
        estimated_annual_tax: Estimated total tax liability for the year in INR.
        tax_already_paid: Tax already paid (TDS + advance tax paid so far) in INR.
        current_quarter: Current quarter (1=Apr-Jun, 2=Jul-Sep, 3=Oct-Dec, 4=Jan-Mar).

    Returns:
        Advance tax installment schedule.
    """
    installments = [
        {"quarter": 1, "due_date": "June 15", "cumulative_pct": 15},
        {"quarter": 2, "due_date": "September 15", "cumulative_pct": 45},
        {"quarter": 3, "due_date": "December 15", "cumulative_pct": 75},
        {"quarter": 4, "due_date": "March 15", "cumulative_pct": 100},
    ]

    balance_tax = max(0, estimated_annual_tax - tax_already_paid)

    if balance_tax < 10000:
        return (
            f"**No advance tax required.** Balance tax liability ₹{balance_tax:,.0f} "
            f"is less than ₹10,000 (threshold under Section 208)."
        )

    lines = [
        f"## Advance Tax Schedule — FY 2025-26\n",
        f"**Estimated Annual Tax**: ₹{estimated_annual_tax:,.0f}",
        f"**Tax Already Paid (TDS/Advance)**: ₹{tax_already_paid:,.0f}",
        f"**Balance Tax**: ₹{balance_tax:,.0f}\n",
        f"| Installment | Due Date | Cumulative % | Amount Due |",
        f"|---|---|---|---|",
    ]

    for inst in installments:
        cumulative_amount = estimated_annual_tax * inst["cumulative_pct"] / 100
        amount_due = max(0, cumulative_amount - tax_already_paid)
        status = "✅ Due" if inst["quarter"] >= current_quarter else "⏳ Past"
        lines.append(
            f"| Q{inst['quarter']} | {inst['due_date']} | {inst['cumulative_pct']}% | ₹{amount_due:,.0f} ({status}) |"
        )

    lines.append(f"\n**Interest u/s 234C**: Applicable if advance tax is not paid on time (1% per month of deferment).")
    return "\n".join(lines)
