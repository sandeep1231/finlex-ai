import pytest
import json


class TestTaxCalculator:
    """Tests for income tax calculation logic."""

    def test_new_regime_basic(self):
        """Test new regime slabs for FY 2025-26."""
        from app.ai.tools.tax_calculator import calculate_income_tax

        result = json.loads(calculate_income_tax.invoke({
            "gross_income": "1500000",
            "regime": "new",
            "financial_year": "2025-26",
        }))
        assert result["regime"] == "new"
        assert result["gross_income"] == 1500000
        assert result["tax_payable"] > 0

    def test_old_regime_basic(self):
        """Test old regime slabs."""
        from app.ai.tools.tax_calculator import calculate_income_tax

        result = json.loads(calculate_income_tax.invoke({
            "gross_income": "1000000",
            "regime": "old",
            "financial_year": "2025-26",
            "deductions": "150000",
        }))
        assert result["regime"] == "old"
        assert result["taxable_income"] < result["gross_income"]

    def test_compare_regimes(self):
        """Test comparison of old vs new regime."""
        from app.ai.tools.tax_calculator import compare_tax_regimes

        result = json.loads(compare_tax_regimes.invoke({
            "gross_income": "1200000",
            "deductions": "200000",
        }))
        assert "old_regime" in result
        assert "new_regime" in result
        assert "recommendation" in result

    def test_zero_income(self):
        """Test zero income edge case."""
        from app.ai.tools.tax_calculator import calculate_income_tax

        result = json.loads(calculate_income_tax.invoke({
            "gross_income": "0",
            "regime": "new",
        }))
        assert result["tax_payable"] == 0


class TestGSTCalculator:
    """Tests for GST calculation logic."""

    def test_intrastate_gst(self):
        """Test intrastate GST (CGST + SGST)."""
        from app.ai.tools.gst_calculator import calculate_gst

        result = json.loads(calculate_gst.invoke({
            "amount": "10000",
            "gst_rate": "18",
            "is_interstate": "false",
        }))
        assert result["cgst"] == 900
        assert result["sgst"] == 900
        assert result["igst"] == 0

    def test_interstate_gst(self):
        """Test interstate GST (IGST only)."""
        from app.ai.tools.gst_calculator import calculate_gst

        result = json.loads(calculate_gst.invoke({
            "amount": "10000",
            "gst_rate": "18",
            "is_interstate": "true",
        }))
        assert result["igst"] == 1800
        assert result["cgst"] == 0
        assert result["sgst"] == 0


class TestTDSCalculator:
    """Tests for TDS calculations."""

    def test_salary_tds(self):
        """Test TDS on salary."""
        from app.ai.tools.tax_calculator import calculate_tds

        result = json.loads(calculate_tds.invoke({
            "amount": "100000",
            "section": "192",
        }))
        assert result["section"] == "192"

    def test_professional_fees_tds(self):
        """Test TDS on professional fees."""
        from app.ai.tools.tax_calculator import calculate_tds

        result = json.loads(calculate_tds.invoke({
            "amount": "50000",
            "section": "194J",
        }))
        assert result["tds_amount"] > 0


class TestDocumentDrafter:
    """Tests for document drafting tools."""

    def test_draft_nda(self):
        """Test NDA drafting."""
        from app.ai.tools.document_drafter import draft_nda

        result = draft_nda.invoke({
            "party_one": "ABC Pvt Ltd",
            "party_two": "XYZ Corp",
            "duration_months": "24",
        })
        assert "ABC Pvt Ltd" in result
        assert "XYZ Corp" in result
        assert "24" in result

    def test_draft_legal_notice(self):
        """Test legal notice drafting."""
        from app.ai.tools.document_drafter import draft_legal_notice

        result = draft_legal_notice.invoke({
            "sender_name": "John Doe",
            "recipient_name": "Jane Smith",
            "subject": "Breach of Contract",
            "facts": "Failed to deliver goods as per agreement dated 01/01/2025",
            "relief_sought": "Refund of advance payment",
        })
        assert "John Doe" in result
        assert "Breach of Contract" in result


class TestFinancialTools:
    """Tests for financial calculation tools."""

    def test_financial_ratios(self):
        """Test financial ratio calculation."""
        from app.ai.tools.financial_tools import financial_ratios

        result = json.loads(financial_ratios.invoke({
            "current_assets": "500000",
            "current_liabilities": "250000",
            "total_debt": "300000",
            "total_equity": "700000",
            "net_income": "150000",
            "revenue": "1000000",
            "total_assets": "1500000",
        }))
        assert result["liquidity_ratios"]["current_ratio"] == 2.0
        assert "debt_to_equity" in result["leverage_ratios"]

    def test_depreciation_slm(self):
        """Test straight-line depreciation."""
        from app.ai.tools.financial_tools import depreciation_calculator

        result = json.loads(depreciation_calculator.invoke({
            "asset_cost": "100000",
            "salvage_value": "10000",
            "useful_life_years": "10",
            "method": "SLM",
        }))
        assert result["method"] == "SLM"
        assert result["annual_depreciation"] == 9000
