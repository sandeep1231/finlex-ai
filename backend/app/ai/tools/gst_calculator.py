from langchain_core.tools import tool


GST_RATES = {
    "exempt": 0,
    "nil": 0,
    "5": 5,
    "18": 18,
    "40": 40,
    "3": 3,
    "0.25": 0.25,
    "1.5": 1.5,
    "28": 28,
}


@tool
def calculate_gst(
    amount: float,
    gst_rate: float,
    is_inclusive: bool = False,
    supply_type: str = "intra_state",
) -> str:
    """Calculate GST (Goods and Services Tax) on a given amount.

    Args:
        amount: The amount in INR. If is_inclusive=True, this is the GST-inclusive amount.
        gst_rate: GST rate as a percentage (e.g., 5, 18, 40).
        is_inclusive: Whether the amount already includes GST.
        supply_type: Type of supply - 'intra_state' (CGST+SGST) or 'inter_state' (IGST).

    Returns:
        GST computation breakdown (CGST, SGST/IGST, total).
    """
    if gst_rate < 0:
        return "GST rate cannot be negative."

    if is_inclusive:
        base_amount = amount * 100 / (100 + gst_rate)
        gst_amount = amount - base_amount
    else:
        base_amount = amount
        gst_amount = amount * gst_rate / 100

    total = base_amount + gst_amount

    lines = [
        f"## GST Computation\n",
        f"| Parameter | Value |",
        f"|---|---|",
        f"| {'GST-Inclusive Amount' if is_inclusive else 'Base Amount'} | ₹{amount:,.2f} |",
        f"| GST Rate | {gst_rate}% |",
        f"| Supply Type | {'Intra-State (CGST + SGST)' if supply_type == 'intra_state' else 'Inter-State (IGST)'} |",
        f"| Base Amount (Taxable Value) | ₹{base_amount:,.2f} |",
    ]

    if supply_type == "intra_state":
        half_rate = gst_rate / 2
        half_amount = gst_amount / 2
        lines.extend([
            f"| CGST @ {half_rate}% | ₹{half_amount:,.2f} |",
            f"| SGST @ {half_rate}% | ₹{half_amount:,.2f} |",
        ])
    else:
        lines.append(f"| IGST @ {gst_rate}% | ₹{gst_amount:,.2f} |")

    lines.extend([
        f"| **Total GST** | **₹{gst_amount:,.2f}** |",
        f"| **Total Amount (incl. GST)** | **₹{total:,.2f}** |",
    ])

    return "\n".join(lines)


@tool
def reverse_charge_gst(
    amount: float,
    gst_rate: float,
    service_type: str = "general",
) -> str:
    """Calculate GST under Reverse Charge Mechanism (RCM).

    Args:
        amount: Payment amount in INR (exclusive of GST).
        gst_rate: Applicable GST rate.
        service_type: Type of service under RCM.

    Returns:
        RCM GST computation with ITC eligibility note.
    """
    gst_amount = amount * gst_rate / 100
    total = amount + gst_amount

    return (
        f"## GST — Reverse Charge Mechanism (RCM)\n\n"
        f"| Parameter | Value |\n|---|---|\n"
        f"| Service Type | {service_type} |\n"
        f"| Base Amount | ₹{amount:,.2f} |\n"
        f"| GST Rate (RCM) | {gst_rate}% |\n"
        f"| GST Payable (by recipient) | ₹{gst_amount:,.2f} |\n"
        f"| Total Cost | ₹{total:,.2f} |\n\n"
        f"**Note**: GST paid under RCM is eligible for Input Tax Credit (ITC) "
        f"in the same month's GSTR-3B return, subject to conditions.\n\n"
        f"**Common RCM Services**: Legal services from advocates, import of services, "
        f"goods transport agency (GTA), sponsorship services, director's remuneration."
    )


@tool
def gst_invoice_summary(
    items: str,
    supply_type: str = "intra_state",
) -> str:
    """Generate a GST invoice summary for multiple items with different rates.

    Args:
        items: JSON string of items, each with 'description', 'amount', 'gst_rate', and optional 'hsn_code'. \
Example: '[{"description": "Consulting", "amount": 50000, "gst_rate": 18, "hsn_code": "998231"}]'
        supply_type: 'intra_state' or 'inter_state'.

    Returns:
        Invoice summary with item-wise GST breakdown and totals.
    """
    import json

    try:
        item_list = json.loads(items)
    except json.JSONDecodeError:
        return "Invalid items format. Please provide valid JSON."

    lines = [
        f"## GST Invoice Summary\n",
        f"**Supply Type**: {'Intra-State' if supply_type == 'intra_state' else 'Inter-State'}\n",
    ]

    if supply_type == "intra_state":
        lines.extend([
            "| # | Description | HSN | Amount | CGST | SGST | Total |",
            "|---|---|---|---|---|---|---|",
        ])
    else:
        lines.extend([
            "| # | Description | HSN | Amount | IGST | Total |",
            "|---|---|---|---|---|---|",
        ])

    total_base = 0
    total_gst = 0

    for idx, item in enumerate(item_list, 1):
        desc = item.get("description", "Item")
        amount = float(item.get("amount", 0))
        rate = float(item.get("gst_rate", 18))
        hsn = item.get("hsn_code", "-")

        gst = amount * rate / 100
        total_base += amount
        total_gst += gst

        if supply_type == "intra_state":
            half_gst = gst / 2
            lines.append(
                f"| {idx} | {desc} | {hsn} | ₹{amount:,.2f} | ₹{half_gst:,.2f} ({rate/2}%) | ₹{half_gst:,.2f} ({rate/2}%) | ₹{amount + gst:,.2f} |"
            )
        else:
            lines.append(
                f"| {idx} | {desc} | {hsn} | ₹{amount:,.2f} | ₹{gst:,.2f} ({rate}%) | ₹{amount + gst:,.2f} |"
            )

    grand_total = total_base + total_gst
    lines.extend([
        "",
        f"**Total Taxable Value**: ₹{total_base:,.2f}",
        f"**Total GST**: ₹{total_gst:,.2f}",
        f"**Grand Total**: ₹{grand_total:,.2f}",
    ])

    return "\n".join(lines)
