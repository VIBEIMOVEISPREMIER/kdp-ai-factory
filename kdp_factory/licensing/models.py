from pydantic import BaseModel, Field


class LicenseActivationRequest(BaseModel):
    license_token: str = Field(min_length=20, max_length=10000)
