from langchain_core.tools import tool


@tool
def financial_ratios(
    current_assets: float = 0,
    current_liabilities: float = 0,
    total_debt: float = 0,
    total_equity: float = 0,
    net_income: float = 0,
    total_revenue: float = 0,
    total_assets: float = 0,
    cost_of_goods_sold: float = 0,
    average_inventory: float = 0,
    average_receivables: float = 0,
    interest_expense: float = 0,
    ebit: float = 0,
) -> str:
    """Calculate key financial ratios from given financial data.

    Args:
        current_assets: Total current assets.
        current_liabilities: Total current liabilities.
        total_debt: Total debt/borrowings.
        total_equity: Total shareholders' equity.
        net_income: Net profit/income.
        total_revenue: Total sales/revenue.
        total_assets: Total assets.
        cost_of_goods_sold: Cost of goods sold.
        average_inventory: Average inventory.
        average_receivables: Average trade receivables.
        interest_expense: Total interest expense.
        ebit: Earnings before interest and tax.

    Returns:
        Comprehensive financial ratio analysis.
    """
    lines = ["## Financial Ratio Analysis\n"]
    lines.append("| Ratio | Value | Benchmark |")
    lines.append("|---|---|---|")

    # Liquidity Ratios
    if current_liabilities > 0:
        current_ratio = current_assets / current_liabilities
        lines.append(f"| **Current Ratio** | {current_ratio:.2f} | > 1.5 (healthy) |")

        if average_inventory > 0:
            quick_ratio = (current_assets - average_inventory) / current_liabilities
            lines.append(f"| **Quick Ratio** | {quick_ratio:.2f} | > 1.0 (healthy) |")

    # Leverage Ratios
    if total_equity > 0:
        debt_equity = total_debt / total_equity
        lines.append(f"| **Debt-to-Equity** | {debt_equity:.2f} | < 2.0 (conservative) |")

        roe = (net_income / total_equity * 100) if net_income else 0
        lines.append(f"| **Return on Equity (ROE)** | {roe:.1f}% | > 15% (good) |")

    if total_assets > 0:
        debt_ratio = total_debt / total_assets
        lines.append(f"| **Debt Ratio** | {debt_ratio:.2f} | < 0.5 (conservative) |")

        roa = (net_income / total_assets * 100) if net_income else 0
        lines.append(f"| **Return on Assets (ROA)** | {roa:.1f}% | > 5% (good) |")

    # Profitability Ratios
    if total_revenue > 0:
        net_margin = net_income / total_revenue * 100
        lines.append(f"| **Net Profit Margin** | {net_margin:.1f}% | Industry-specific |")

        gross_margin = (total_revenue - cost_of_goods_sold) / total_revenue * 100 if cost_of_goods_sold else 0
        if cost_of_goods_sold > 0:
            lines.append(f"| **Gross Profit Margin** | {gross_margin:.1f}% | Industry-specific |")

    # Efficiency Ratios
    if average_inventory > 0 and cost_of_goods_sold > 0:
        inv_turnover = cost_of_goods_sold / average_inventory
        inv_days = 365 / inv_turnover if inv_turnover > 0 else 0
        lines.append(f"| **Inventory Turnover** | {inv_turnover:.1f}x | Higher = better |")
        lines.append(f"| **Days in Inventory** | {inv_days:.0f} days | Lower = better |")

    if average_receivables > 0 and total_revenue > 0:
        recv_turnover = total_revenue / average_receivables
        recv_days = 365 / recv_turnover if recv_turnover > 0 else 0
        lines.append(f"| **Receivables Turnover** | {recv_turnover:.1f}x | Higher = better |")
        lines.append(f"| **Days Sales Outstanding** | {recv_days:.0f} days | < 45 (good) |")

    # Coverage Ratios
    if interest_expense > 0 and ebit > 0:
        interest_coverage = ebit / interest_expense
        lines.append(f"| **Interest Coverage** | {interest_coverage:.1f}x | > 3.0 (safe) |")

    if len(lines) <= 3:
        return "Insufficient data provided. Please provide at least current assets, current liabilities, and some income/revenue figures."

    lines.append("\n*Note: Benchmarks are general guidelines. Compare with industry peers for meaningful analysis.*")
    return "\n".join(lines)


@tool
def depreciation_calculator(
    asset_cost: float,
    residual_value: float = 0,
    useful_life_years: int = 10,
    method: str = "slm",
    wdv_rate: float = 0,
    block_of_asset: str = "",
) -> str:
    """Calculate depreciation using SLM or WDV method as per Companies Act / Income Tax Act.

    Args:
        asset_cost: Original cost of the asset in INR.
        residual_value: Estimated residual/scrap value (default 0 for IT Act).
        useful_life_years: Useful life in years (for SLM).
        method: Depreciation method - 'slm' (Straight Line Method) or 'wdv' (Written Down Value).
        wdv_rate: WDV depreciation rate percentage (for Income Tax Act).
        block_of_asset: Description of the asset block (for IT Act reference).

    Returns:
        Depreciation schedule.
    """
    lines = [
        f"## Depreciation Calculation\n",
        f"| Parameter | Value |",
        f"|---|---|",
        f"| Asset Cost | ₹{asset_cost:,.0f} |",
        f"| Residual Value | ₹{residual_value:,.0f} |",
        f"| Method | {'Straight Line (SLM)' if method == 'slm' else 'Written Down Value (WDV)'} |",
    ]

    if method == "slm":
        depreciable_amount = asset_cost - residual_value
        annual_dep = depreciable_amount / useful_life_years
        lines.append(f"| Useful Life | {useful_life_years} years |")
        lines.append(f"| Annual Depreciation | ₹{annual_dep:,.0f} |")
        lines.append(f"| SLM Rate | {100 / useful_life_years:.2f}% |")
        lines.append("")

        lines.extend([
            "### Year-wise Schedule:",
            "| Year | Opening | Depreciation | Closing |",
            "|---|---|---|---|",
        ])

        book_value = asset_cost
        for year in range(1, min(useful_life_years + 1, 11)):  # Show max 10 years
            dep = min(annual_dep, book_value - residual_value)
            closing = book_value - dep
            lines.append(f"| {year} | ₹{book_value:,.0f} | ₹{dep:,.0f} | ₹{closing:,.0f} |")
            book_value = closing

        if useful_life_years > 10:
            lines.append(f"| ... | ... | ... | ... |")
            lines.append(f"| {useful_life_years} | - | - | ₹{residual_value:,.0f} |")

    else:  # WDV method
        if wdv_rate <= 0:
            return "Please provide a WDV depreciation rate. Common rates under Income Tax Act: 15% (buildings), 40% (plant & machinery), 60% (computers)."

        lines.append(f"| WDV Rate | {wdv_rate}% |")
        if block_of_asset:
            lines.append(f"| Block of Asset | {block_of_asset} |")
        lines.append("")

        lines.extend([
            "### Year-wise Schedule:",
            "| Year | Opening WDV | Depreciation | Closing WDV |",
            "|---|---|---|---|",
        ])

        wdv = asset_cost
        for year in range(1, 11):
            dep = wdv * wdv_rate / 100
            closing = wdv - dep
            lines.append(f"| {year} | ₹{wdv:,.0f} | ₹{dep:,.0f} | ₹{closing:,.0f} |")
            wdv = closing
            if wdv < 1:
                break

    return "\n".join(lines)
