from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ai.tools.tax_calculator import (
    calculate_income_tax,
    compare_tax_regimes,
    calculate_tds,
    calculate_advance_tax,
)
from app.ai.tools.gst_calculator import calculate_gst, reverse_charge_gst
from app.ai.tools.financial_tools import financial_ratios, depreciation_calculator

router = APIRouter()


class IncomeTaxRequest(BaseModel):
    gross_income: float = Field(..., gt=0)
    regime: str = Field(default="new", pattern="^(new|old)$")
    age_category: str = Field(default="below_60", pattern="^(below_60|60_to_80|above_80)$")
    deductions_80c: float = Field(default=0, ge=0)
    deductions_80d: float = Field(default=0, ge=0)
    deductions_80ccd_1b: float = Field(default=0, ge=0)
    hra_exemption: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)
    other_deductions: float = Field(default=0, ge=0)
    is_salaried: bool = True


class GSTRequest(BaseModel):
    amount: float = Field(..., gt=0)
    gst_rate: float = Field(..., ge=0)
    is_inclusive: bool = False
    supply_type: str = Field(default="intra_state", pattern="^(intra_state|inter_state)$")


class TDSRequest(BaseModel):
    payment_amount: float = Field(..., gt=0)
    section: str
    payee_type: str = Field(default="individual", pattern="^(individual|company)$")
    pan_available: bool = True


class AdvanceTaxRequest(BaseModel):
    estimated_annual_tax: float = Field(..., gt=0)
    tax_already_paid: float = Field(default=0, ge=0)
    current_quarter: int = Field(default=1, ge=1, le=4)


class FinancialRatiosRequest(BaseModel):
    current_assets: float = 0
    current_liabilities: float = 0
    total_debt: float = 0
    total_equity: float = 0
    net_income: float = 0
    total_revenue: float = 0
    total_assets: float = 0
    cost_of_goods_sold: float = 0
    average_inventory: float = 0
    average_receivables: float = 0
    interest_expense: float = 0
    ebit: float = 0


class DepreciationRequest(BaseModel):
    asset_cost: float = Field(..., gt=0)
    residual_value: float = Field(default=0, ge=0)
    useful_life_years: int = Field(default=10, gt=0)
    method: str = Field(default="slm", pattern="^(slm|wdv)$")
    wdv_rate: float = Field(default=0, ge=0)
    block_of_asset: str = ""


@router.post("/income-tax")
async def api_calculate_income_tax(req: IncomeTaxRequest):
    """Calculate income tax under Old or New Regime for FY 2025-26."""
    result = calculate_income_tax.invoke(req.model_dump())
    return {"result": result}


@router.post("/compare-regimes")
async def api_compare_regimes(req: IncomeTaxRequest):
    """Compare tax liability under Old vs New Regime."""
    result = compare_tax_regimes.invoke({
        "gross_income": req.gross_income,
        "deductions_80c": req.deductions_80c,
        "deductions_80d": req.deductions_80d,
        "deductions_80ccd_1b": req.deductions_80ccd_1b,
        "hra_exemption": req.hra_exemption,
        "home_loan_interest": req.home_loan_interest,
        "other_deductions": req.other_deductions,
        "is_salaried": req.is_salaried,
    })
    return {"result": result}


@router.post("/gst")
async def api_calculate_gst(req: GSTRequest):
    """Calculate GST (CGST/SGST or IGST) on a given amount."""
    result = calculate_gst.invoke(req.model_dump())
    return {"result": result}


@router.post("/tds")
async def api_calculate_tds(req: TDSRequest):
    """Calculate TDS for a given payment and section."""
    result = calculate_tds.invoke(req.model_dump())
    return {"result": result}


@router.post("/advance-tax")
async def api_calculate_advance_tax(req: AdvanceTaxRequest):
    """Calculate advance tax installment schedule."""
    result = calculate_advance_tax.invoke(req.model_dump())
    return {"result": result}


@router.post("/financial-ratios")
async def api_financial_ratios(req: FinancialRatiosRequest):
    """Calculate key financial ratios from provided data."""
    result = financial_ratios.invoke(req.model_dump())
    return {"result": result}


@router.post("/depreciation")
async def api_depreciation(req: DepreciationRequest):
    """Calculate depreciation using SLM or WDV method."""
    result = depreciation_calculator.invoke(req.model_dump())
    return {"result": result}
