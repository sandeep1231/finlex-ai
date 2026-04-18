from app.ai.tools.tax_calculator import (
    calculate_income_tax,
    compare_tax_regimes,
    calculate_tds,
    calculate_advance_tax,
)
from app.ai.tools.gst_calculator import (
    calculate_gst,
    reverse_charge_gst,
    gst_invoice_summary,
)
from app.ai.tools.document_drafter import (
    draft_legal_notice,
    draft_engagement_letter,
    draft_board_resolution,
    draft_nda,
    draft_partnership_deed,
    draft_power_of_attorney,
    draft_rent_agreement,
)
from app.ai.tools.financial_tools import (
    financial_ratios,
    depreciation_calculator,
)
from app.ai.tools.capital_gains import (
    calculate_capital_gains,
)
from app.ai.tools.additional_tools import (
    calculate_tcs,
    calculate_hra_exemption,
    calculate_emi,
)


def get_all_tools():
    """Return all available tools for the AI agent."""
    return [
        # Tax calculators
        calculate_income_tax,
        compare_tax_regimes,
        calculate_tds,
        calculate_tcs,
        calculate_advance_tax,
        calculate_capital_gains,
        calculate_hra_exemption,
        calculate_emi,
        # GST calculators
        calculate_gst,
        reverse_charge_gst,
        gst_invoice_summary,
        # Document drafting
        draft_legal_notice,
        draft_engagement_letter,
        draft_board_resolution,
        draft_nda,
        draft_partnership_deed,
        draft_power_of_attorney,
        draft_rent_agreement,
        # Financial tools
        financial_ratios,
        depreciation_calculator,
    ]
