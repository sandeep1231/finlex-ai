from langchain_core.tools import tool


# TCS Rates FY 2025-26
TCS_RATES = {
    "206C(1)_scrap": {"desc": "Sale of scrap", "rate": 1, "threshold": 0},
    "206C(1)_timber": {"desc": "Sale of timber/forest produce", "rate": 2.5, "threshold": 0},
    "206C(1)_minerals": {"desc": "Sale of minerals (coal, lignite, iron ore)", "rate": 1, "threshold": 0},
    "206C(1)_tendu_leaves": {"desc": "Sale of tendu leaves", "rate": 5, "threshold": 0},
    "206C(1)_motor_vehicle": {"desc": "Sale of motor vehicle > ₹10L", "rate": 1, "threshold": 1000000},
    "206C(1F)_motor_vehicle": {"desc": "Motor vehicle > ₹10L (any mode of payment)", "rate": 1, "threshold": 1000000},
    "206C(1G)_remittance": {"desc": "Foreign remittance under LRS", "rate": 20, "threshold": 700000, "education_rate": 5, "medical_rate": 5},
    "206C(1G)_tour_package": {"desc": "Overseas tour package", "rate": 20, "threshold": 700000},
    "206C(1H)_goods": {"desc": "Sale of goods > ₹50L", "rate": 0.1, "threshold": 5000000},
}


@tool
def calculate_tcs(
    transaction_amount: float,
    section: str = "206C(1H)_goods",
    is_pan_available: bool = True,
) -> str:
    """Calculate Tax Collected at Source (TCS) for various transactions.

    Args:
        transaction_amount: Total transaction value (₹).
        section: TCS section — one of: 206C(1)_scrap, 206C(1)_timber, 206C(1)_minerals,
            206C(1)_tendu_leaves, 206C(1)_motor_vehicle, 206C(1F)_motor_vehicle,
            206C(1G)_remittance, 206C(1G)_tour_package, 206C(1H)_goods.
        is_pan_available: Whether buyer's PAN is available (higher rate if not).

    Returns:
        TCS computation with applicable rates and amount.
    """
    rate_info = TCS_RATES.get(section)
    if not rate_info:
        return f"❌ Unknown TCS section: {section}. Available: {', '.join(TCS_RATES.keys())}"

    threshold = rate_info["threshold"]
    rate = rate_info["rate"]
    desc = rate_info["desc"]

    # Higher rate for non-PAN: 5% or double, whichever is higher (Sec 206CC)
    if not is_pan_available:
        rate = max(rate * 2, 5)
        pan_note = f" (Higher rate applied — PAN not available, Sec 206CC)"
    else:
        pan_note = ""

    # Amount on which TCS applies
    if threshold > 0 and transaction_amount > threshold:
        taxable_amount = transaction_amount - threshold
    elif threshold > 0:
        return (
            f"## TCS Computation — {desc}\n\n"
            f"**Section:** {section}\n"
            f"**Transaction Amount:** ₹{transaction_amount:,.0f}\n"
            f"**Threshold:** ₹{threshold:,.0f}\n\n"
            f"✅ **No TCS applicable** — Transaction amount is below the threshold of ₹{threshold:,.0f}.\n\n"
            f"*Disclaimer: AI-generated. Verify with a qualified CA.*"
        )
    else:
        taxable_amount = transaction_amount

    tcs_amount = taxable_amount * rate / 100
    total_collection = transaction_amount + tcs_amount

    lines = [
        f"## TCS Computation — {desc}",
        f"**Section:** {section}{pan_note}",
        "",
        "| Item | Amount |",
        "|------|--------|",
        f"| Transaction Value | ₹{transaction_amount:,.0f} |",
    ]
    if threshold > 0:
        lines.append(f"| Threshold (exempt) | ₹{threshold:,.0f} |")
        lines.append(f"| Taxable Amount | ₹{taxable_amount:,.0f} |")

    lines.extend([
        f"| TCS Rate | {rate}% |",
        f"| **TCS Amount** | **₹{tcs_amount:,.0f}** |",
        f"| Total Collection from Buyer | ₹{total_collection:,.0f} |",
        "",
        "### Key Notes",
        f"- TCS is collected **from the buyer** at the time of receipt of consideration",
        f"- Seller must deposit TCS by 7th of the next month",
        f"- TCS return: Form 27EQ (quarterly)",
        f"- Buyer can claim credit of TCS against income tax liability",
    ])

    if "1G" in section:
        lines.extend([
            "",
            "### LRS / Tour Package Special Rules",
            "- First ₹7L in a FY: No TCS (effective from Oct 2023)",
            "- For education (with loan from financial institution): 0.5% above ₹7L",
            "- For education (without loan): 5% above ₹7L",
            "- For medical treatment: 5% above ₹7L",
            "- All other purposes: 20% above ₹7L",
        ])

    lines.append("")
    lines.append("*Disclaimer: AI-generated. Verify with a qualified CA.*")

    return "\n".join(lines)


@tool
def calculate_hra_exemption(
    basic_salary_annual: float,
    da_annual: float,
    hra_received_annual: float,
    rent_paid_annual: float,
    is_metro: bool = True,
) -> str:
    """Calculate HRA exemption under Section 10(13A) for salaried employees.

    Args:
        basic_salary_annual: Annual basic salary (₹).
        da_annual: Annual Dearness Allowance forming part of salary (₹).
        hra_received_annual: Annual HRA received from employer (₹).
        rent_paid_annual: Annual rent paid for accommodation (₹).
        is_metro: True if living in metro city (Delhi, Mumbai, Chennai, Kolkata).

    Returns:
        HRA exemption computation under Section 10(13A).
    """
    salary = basic_salary_annual + da_annual
    metro_pct = 50 if is_metro else 40

    # Three conditions for HRA exemption (least of):
    actual_hra = hra_received_annual
    pct_of_salary = salary * metro_pct / 100
    rent_minus_10pct = max(0, rent_paid_annual - salary * 10 / 100)

    exemption = min(actual_hra, pct_of_salary, rent_minus_10pct)
    taxable_hra = hra_received_annual - exemption

    city_type = "Metro (Delhi/Mumbai/Chennai/Kolkata)" if is_metro else "Non-Metro"

    lines = [
        "## HRA Exemption Calculation — Section 10(13A)",
        f"**City Type:** {city_type}",
        "",
        "### Salary Components",
        f"| Component | Annual Amount |",
        f"|-----------|-------------|",
        f"| Basic Salary | ₹{basic_salary_annual:,.0f} |",
        f"| Dearness Allowance | ₹{da_annual:,.0f} |",
        f"| **Salary (Basic + DA)** | **₹{salary:,.0f}** |",
        f"| HRA Received | ₹{hra_received_annual:,.0f} |",
        f"| Rent Paid | ₹{rent_paid_annual:,.0f} |",
        "",
        "### Exemption Computation (Least of the following)",
        f"| Condition | Amount |",
        f"|-----------|--------|",
        f"| (a) Actual HRA received | ₹{actual_hra:,.0f} |",
        f"| (b) {metro_pct}% of Salary (Basic + DA) | ₹{pct_of_salary:,.0f} |",
        f"| (c) Rent paid − 10% of Salary | ₹{rent_minus_10pct:,.0f} |",
        "",
        f"### Result",
        f"| Item | Amount |",
        f"|------|--------|",
        f"| **HRA Exempt** | **₹{exemption:,.0f}** |",
        f"| HRA Taxable | ₹{taxable_hra:,.0f} |",
        "",
        "### Important Notes",
        "- HRA exemption is available **only under the Old Tax Regime**",
        "- Rent receipts required if rent > ₹1,00,000/year",
        "- Landlord's PAN required if rent > ₹1,00,000/month",
        "- If living with parents, rent agreement + payment proof needed",
        "- Cannot claim both HRA exemption and deduction u/s 80GG",
        "",
        "*Disclaimer: AI-generated. Verify with a qualified CA.*",
    ]

    return "\n".join(lines)


@tool
def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
) -> str:
    """Calculate EMI and loan amortization schedule for home/vehicle/personal loans.

    Args:
        principal: Loan principal amount (₹).
        annual_interest_rate: Annual interest rate (e.g., 8.5 for 8.5%).
        tenure_months: Loan tenure in months (e.g., 240 for 20 years).

    Returns:
        EMI amount, total interest, and year-wise amortization summary.
    """
    r = annual_interest_rate / 12 / 100  # Monthly rate

    if r == 0:
        emi = principal / tenure_months
    else:
        emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)

    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    lines = [
        "## EMI & Loan Amortization Calculator",
        "",
        "### Loan Details",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| Principal | ₹{principal:,.0f} |",
        f"| Interest Rate | {annual_interest_rate}% p.a. |",
        f"| Tenure | {tenure_months} months ({tenure_months // 12} years {tenure_months % 12} months) |",
        "",
        f"### EMI Summary",
        f"| Item | Amount |",
        f"|------|--------|",
        f"| **Monthly EMI** | **₹{emi:,.0f}** |",
        f"| Total Interest Payable | ₹{total_interest:,.0f} |",
        f"| Total Payment (Principal + Interest) | ₹{total_payment:,.0f} |",
        "",
        "### Year-wise Amortization",
        "| Year | Principal Paid | Interest Paid | Outstanding |",
        "|------|---------------|---------------|-------------|",
    ]

    balance = principal
    for year in range(1, min(tenure_months // 12 + 2, 31)):
        year_principal = 0
        year_interest = 0
        for _ in range(12):
            if balance <= 0:
                break
            interest_component = balance * r
            principal_component = min(emi - interest_component, balance)
            year_principal += principal_component
            year_interest += interest_component
            balance -= principal_component

        if year_principal > 0:
            lines.append(
                f"| {year} | ₹{year_principal:,.0f} | ₹{year_interest:,.0f} | ₹{max(0, balance):,.0f} |"
            )

    lines.extend([
        "",
        "### Tax Benefits on Loans",
        "- **Home Loan (Self-Occupied):** Interest deduction u/s 24(b) up to ₹2,00,000; Principal u/s 80C up to ₹1,50,000",
        "- **Home Loan (Let-Out):** Entire interest deductible u/s 24(b); No cap",
        "- **Education Loan:** Entire interest deductible u/s 80E for 8 years from repayment start",
        "- **Electric Vehicle Loan:** Interest deduction u/s 80EEB up to ₹1,50,000",
        "",
        "*Note: Tax benefits available only under the Old Tax Regime (except Sec 24(b) for let-out property).*",
        "",
        "*Disclaimer: AI-generated. Verify with a qualified professional.*",
    ])

    return "\n".join(lines)
