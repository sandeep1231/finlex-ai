"""
End-to-end test script for FinLex AI backend.
Tests all API endpoints: health, calculators, auth, chat, documents, conversations.
"""
import requests
import json
import time
import sys

BASE = "http://localhost:8000"
API = f"{BASE}/api/v1"

PASS = 0
FAIL = 0
ERRORS = []

def test(name, response, expected_status=200, check_fn=None):
    global PASS, FAIL, ERRORS
    ok = response.status_code == expected_status
    detail = ""
    if ok and check_fn:
        try:
            ok = check_fn(response)
            if not ok:
                detail = "check_fn returned False"
        except Exception as e:
            ok = False
            detail = str(e)
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        try:
            body = response.text[:200]
        except:
            body = "no body"
        msg = f"FAIL  {name} - got {response.status_code}, expected {expected_status}. {detail} {body}"
        ERRORS.append(msg)
        print(f"  {msg}")
    return ok


print("=" * 60)
print("FINLEX AI - END-TO-END API TESTS")
print("=" * 60)

# ============================================================
# 1. HEALTH CHECK
# ============================================================
print("\n--- 1. Health Check ---")
r = requests.get(f"{BASE}/health")
test("GET /health", r, 200, lambda r: r.json()["status"] == "healthy")

# ============================================================
# 2. CALCULATOR ENDPOINTS (No auth required)
# ============================================================
print("\n--- 2. Calculator Endpoints ---")

# Income Tax - New Regime
r = requests.post(f"{API}/calculator/income-tax", json={
    "gross_income": 1500000,
    "regime": "new",
    "age_category": "below_60",
    "is_salaried": True
})
test("POST /calculator/income-tax (new regime)", r, 200,
     lambda r: "result" in r.json() and len(r.json()["result"]) > 50)

# Income Tax - Old Regime
r = requests.post(f"{API}/calculator/income-tax", json={
    "gross_income": 1500000,
    "regime": "old",
    "age_category": "below_60",
    "deductions_80c": 150000,
    "deductions_80d": 25000,
    "hra_exemption": 200000,
    "is_salaried": True
})
test("POST /calculator/income-tax (old regime)", r, 200,
     lambda r: "result" in r.json())

# Compare Regimes
r = requests.post(f"{API}/calculator/compare-regimes", json={
    "gross_income": 1500000,
    "age_category": "below_60",
    "deductions_80c": 150000,
    "deductions_80d": 25000,
    "is_salaried": True
})
test("POST /calculator/compare-regimes", r, 200,
     lambda r: "result" in r.json())

# GST
r = requests.post(f"{API}/calculator/gst", json={
    "amount": 100000,
    "gst_rate": 18,
    "is_inclusive": False,
    "supply_type": "intra_state"
})
test("POST /calculator/gst (intra-state)", r, 200,
     lambda r: "result" in r.json())

r = requests.post(f"{API}/calculator/gst", json={
    "amount": 100000,
    "gst_rate": 18,
    "is_inclusive": True,
    "supply_type": "inter_state"
})
test("POST /calculator/gst (inter-state inclusive)", r, 200,
     lambda r: "result" in r.json())

# TDS
r = requests.post(f"{API}/calculator/tds", json={
    "payment_amount": 500000,
    "section": "194C",
    "payee_type": "individual"
})
test("POST /calculator/tds", r, 200,
     lambda r: "result" in r.json())

# Advance Tax
r = requests.post(f"{API}/calculator/advance-tax", json={
    "estimated_annual_tax": 200000,
    "tax_already_paid": 45000,
    "current_quarter": 3
})
test("POST /calculator/advance-tax", r, 200,
     lambda r: "result" in r.json())

# Financial Ratios
r = requests.post(f"{API}/calculator/financial-ratios", json={
    "current_assets": 5000000,
    "current_liabilities": 2000000,
    "total_assets": 15000000,
    "total_equity": 9000000,
    "net_income": 2000000,
    "total_revenue": 12000000,
    "cost_of_goods_sold": 7000000,
    "total_debt": 4000000,
    "interest_expense": 400000,
    "ebit": 2800000
})
test("POST /calculator/financial-ratios", r, 200,
     lambda r: "result" in r.json())

# Depreciation
r = requests.post(f"{API}/calculator/depreciation", json={
    "asset_cost": 1000000,
    "useful_life_years": 10,
    "method": "slm",
    "residual_value": 100000
})
test("POST /calculator/depreciation (SLM)", r, 200,
     lambda r: "result" in r.json())

r = requests.post(f"{API}/calculator/depreciation", json={
    "asset_cost": 1000000,
    "useful_life_years": 10,
    "method": "wdv",
    "wdv_rate": 15
})
test("POST /calculator/depreciation (WDV)", r, 200,
     lambda r: "result" in r.json())

# ============================================================
# 3. AUTH ENDPOINTS (require Bearer token)
# ============================================================
print("\n--- 3. Auth Endpoints ---")

# Without token - should get 403
r = requests.get(f"{API}/auth/me")
test("GET /auth/me without token → 403", r, 403)

# With invalid token - should get 401
r = requests.get(f"{API}/auth/me", headers={"Authorization": "Bearer invalid-token"})
test("GET /auth/me with bad token → 401", r, 401)

# ============================================================
# 4. CHAT ENDPOINTS (require Bearer token)
# ============================================================
print("\n--- 4. Chat Endpoints ---")

# Without token
r = requests.post(f"{API}/chat/", json={"message": "hello"})
test("POST /chat/ without token → 403", r, 403)

r = requests.get(f"{API}/chat/conversations")
test("GET /chat/conversations without token → 403", r, 403)

# ============================================================
# 5. DOCUMENT ENDPOINTS (require Bearer token)
# ============================================================
print("\n--- 5. Document Endpoints ---")

r = requests.get(f"{API}/documents/")
test("GET /documents/ without token → 403", r, 403)

# ============================================================
# 6. CORS HEADERS
# ============================================================
print("\n--- 6. CORS Headers ---")

r = requests.options(f"{BASE}/health", headers={
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "GET",
})
test("OPTIONS /health CORS preflight", r, 200,
     lambda r: r.headers.get("access-control-allow-origin") == "http://localhost:3000")

# ============================================================
# 7. RATE LIMITING
# ============================================================
print("\n--- 7. Rate Limit Headers ---")
r = requests.get(f"{BASE}/health")
test("Rate limit not triggered on normal request", r, 200)

# ============================================================
# 8. OPENAPI/DOCS
# ============================================================
print("\n--- 8. API Documentation ---")
r = requests.get(f"{BASE}/docs")
test("GET /docs (Swagger UI)", r, 200,
     lambda r: "swagger" in r.text.lower() or "openapi" in r.text.lower())

r = requests.get(f"{BASE}/openapi.json")
test("GET /openapi.json", r, 200,
     lambda r: r.json().get("info", {}).get("title") == "FinLex AI")

# ============================================================
# 9. INVALID ENDPOINTS
# ============================================================
print("\n--- 9. Error Handling ---")
r = requests.get(f"{API}/nonexistent")
test("GET /api/v1/nonexistent → 404", r, 404)

r = requests.post(f"{API}/calculator/income-tax", json={})
# Should fail validation
test("POST /calculator/income-tax empty body → 422", r, 422)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
print("=" * 60)

if ERRORS:
    print("\nFAILED TESTS:")
    for e in ERRORS:
        print(f"  - {e}")

sys.exit(1 if FAIL > 0 else 0)
