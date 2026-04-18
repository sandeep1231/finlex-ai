from langchain_core.tools import tool


# Cost Inflation Index (CII) for indexation — selected years
CII_TABLE = {
    "2001-02": 100, "2002-03": 105, "2003-04": 109, "2004-05": 113,
    "2005-06": 117, "2006-07": 122, "2007-08": 129, "2008-09": 137,
    "2009-10": 148, "2010-11": 167, "2011-12": 184, "2012-13": 200,
    "2013-14": 220, "2014-15": 240, "2015-16": 254, "2016-17": 264,
    "2017-18": 272, "2018-19": 280, "2019-20": 289, "2020-21": 301,
    "2021-22": 317, "2022-23": 331, "2023-24": 348, "2024-25": 363,
    "2025-26": 377,
}


@tool
def calculate_capital_gains(
    sale_price: float,
    purchase_price: float,
    asset_type: str,
    holding_period_months: int,
    purchase_year: str = "2020-21",
    sale_year: str = "2025-26",
    improvement_cost: float = 0,
    sale_expenses: float = 0,
) -> str:
    """Calculate capital gains tax on sale of assets (property, equity, mutual funds, gold, etc.)

    Args:
        sale_price: Sale consideration received (₹).
        purchase_price: Original cost of acquisition (₹).
        asset_type: Type of asset — one of: listed_equity, equity_mf, debt_mf, property, gold, unlisted_shares, other.
        holding_period_months: Number of months the asset was held.
        purchase_year: Financial year of purchase (e.g., '2020-21'). Used for CII indexation.
        sale_year: Financial year of sale (e.g., '2025-26').
        improvement_cost: Cost of improvement, if any (₹).
        sale_expenses: Brokerage, transfer fees, legal charges (₹).

    Returns:
        Capital gains computation with applicable tax rate.
    """
    # Determine LTCG holding threshold and tax rates based on asset type
    asset_rules = {
        "listed_equity": {"ltcg_months": 12, "stcg_rate": 20, "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 125000},
        "equity_mf": {"ltcg_months": 12, "stcg_rate": 20, "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 125000},
        "debt_mf": {"ltcg_months": 24, "stcg_rate": "slab", "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 0},
        "property": {"ltcg_months": 24, "stcg_rate": "slab", "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 0},
        "gold": {"ltcg_months": 24, "stcg_rate": "slab", "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 0},
        "unlisted_shares": {"ltcg_months": 24, "stcg_rate": "slab", "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 0},
        "other": {"ltcg_months": 36, "stcg_rate": "slab", "ltcg_rate": 12.5, "indexation": False, "ltcg_exemption": 0},
    }

    rules = asset_rules.get(asset_type, asset_rules["other"])
    is_ltcg = holding_period_months >= rules["ltcg_months"]
    gain_type = "Long-Term Capital Gain (LTCG)" if is_ltcg else "Short-Term Capital Gain (STCG)"

    # Compute cost
    total_cost = purchase_price + improvement_cost
    indexed_cost = total_cost  # default no indexation post Budget 2024

    net_sale = sale_price - sale_expenses
    capital_gain = net_sale - indexed_cost

    # Tax computation
    if is_ltcg:
        exemption = rules["ltcg_exemption"]
        taxable_gain = max(0, capital_gain - exemption)
        tax_rate = rules["ltcg_rate"]
        tax = taxable_gain * tax_rate / 100
    else:
        tax_rate = rules["stcg_rate"]
        taxable_gain = max(0, capital_gain)
        if tax_rate == "slab":
            tax = None  # Will be at slab rate
        else:
            tax = taxable_gain * tax_rate / 100

    # Surcharge + Cess placeholder
    cess_rate = 4
    if tax is not None:
        cess = tax * cess_rate / 100
        total_tax = tax + cess
    else:
        cess = None
        total_tax = None

    # Format output
    lines = [
        f"## Capital Gains Computation — {asset_type.replace('_', ' ').title()}",
        f"**Type:** {gain_type}",
        f"**Holding Period:** {holding_period_months} months (threshold for LTCG: {rules['ltcg_months']} months)",
        "",
        "### Computation",
        f"| Item | Amount |",
        f"|------|--------|",
        f"| Sale Consideration | ₹{sale_price:,.0f} |",
    ]

    if sale_expenses > 0:
        lines.append(f"| Less: Sale Expenses | ₹{sale_expenses:,.0f} |")

    lines.append(f"| Net Sale Consideration | ₹{net_sale:,.0f} |")
    lines.append(f"| Cost of Acquisition | ₹{purchase_price:,.0f} |")

    if improvement_cost > 0:
        lines.append(f"| Cost of Improvement | ₹{improvement_cost:,.0f} |")

    lines.append(f"| Total Cost | ₹{indexed_cost:,.0f} |")

    if capital_gain >= 0:
        lines.append(f"| **Capital Gain** | **₹{capital_gain:,.0f}** |")
    else:
        lines.append(f"| **Capital Loss** | **₹{abs(capital_gain):,.0f}** |")

    lines.append("")

    if capital_gain > 0:
        lines.append("### Tax Liability")
        if is_ltcg and rules["ltcg_exemption"] > 0:
            lines.append(f"- LTCG Exemption (Sec 112A): ₹{rules['ltcg_exemption']:,.0f}")
            lines.append(f"- Taxable LTCG: ₹{taxable_gain:,.0f}")

        if tax is not None:
            lines.append(f"- Tax Rate: {tax_rate}%")
            lines.append(f"- Tax: ₹{tax:,.0f}")
            lines.append(f"- Health & Education Cess (4%): ₹{cess:,.0f}")
            lines.append(f"- **Total Tax: ₹{total_tax:,.0f}**")
        else:
            lines.append(f"- Tax Rate: **At slab rates** (added to total income)")
            lines.append("- Compute using Income Tax Calculator for exact liability")

        lines.append("")
        lines.append("### Exemptions Available (LTCG only)")
        lines.append("- **Section 54**: Reinvest in residential property (for property sale)")
        lines.append("- **Section 54F**: Reinvest net consideration in residential property (non-property assets)")
        lines.append("- **Section 54EC**: Invest up to ₹50L in specified bonds (NHAI/REC) within 6 months")
    else:
        lines.append("### Loss Set-off Rules")
        lines.append("- STCL can be set off against STCG + LTCG")
        lines.append("- LTCL can be set off only against LTCG")
        lines.append("- Carry forward for 8 assessment years (must file ITR on time)")

    lines.append("")
    lines.append(f"*Note: As per Finance Act 2024 (Budget 2024), indexation benefit has been removed. "
                 f"LTCG is taxed at flat 12.5% without indexation for all assets.*")
    lines.append("")
    lines.append("*Disclaimer: AI-generated. Verify with a qualified CA.*")

    return "\n".join(lines)
