from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .licensing_service import LicenseService

app = FastAPI(title="KDP AI Factory License Server", version="1.0.0")
service = LicenseService()

class TrialRequest(BaseModel):
    machine_id: str = Field(min_length=32, max_length=128)

class ActivationRequest(BaseModel):
    machine_id: str = Field(min_length=32, max_length=128)
    license_token: str = Field(min_length=20, max_length=20000)

class PaymentCheckRequest(BaseModel):
    tx_id: str = Field(min_length=20, max_length=200)
    asset: str = Field(pattern=r"^(USDT|BNB)$")

@app.get("/health")
def health():
    return {"ok": True, "service": "kdp-ai-factory-license-server"}

@app.post("/v1/trial/register")
def register_trial(payload: TrialRequest):
    return service.register_trial(payload.machine_id)

@app.post("/v1/license/activate")
def activate(payload: ActivationRequest):
    result = service.activate(payload.machine_id, payload.license_token)
    if not result["valid"]:
        raise HTTPException(status_code=403, detail=result["reason"])
    return result

@app.post("/v1/payment/check")
def check_payment(payload: PaymentCheckRequest):
    try:
        return service.verify_payment(payload.tx_id, payload.asset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
