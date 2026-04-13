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
)
from app.ai.tools.financial_tools import (
    financial_ratios,
    depreciation_calculator,
)


def get_all_tools():
    """Return all available tools for the AI agent."""
    return [
        # Tax calculators
        calculate_income_tax,
        compare_tax_regimes,
        calculate_tds,
        calculate_advance_tax,
        # GST calculators
        calculate_gst,
        reverse_charge_gst,
        gst_invoice_summary,
        # Document drafting
        draft_legal_notice,
        draft_engagement_letter,
        draft_board_resolution,
        draft_nda,
        # Financial tools
        financial_ratios,
        depreciation_calculator,
    ]
