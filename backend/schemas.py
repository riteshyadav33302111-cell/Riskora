"""
Riskora – Pydantic Schemas
============================
Request / response models for the FastAPI backend.
"""

from __future__ import annotations
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Dict, Any
import re


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class URLScanRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL must not be empty.")
        if len(v) > 2048:
            raise ValueError("URL exceeds maximum length of 2048 characters.")

        # Must start with http:// or https://
        if not re.match(r"^https?://", v, re.IGNORECASE):
            raise ValueError(
                "URL must begin with http:// or https://. "
                "Example: https://example.com"
            )

        # Basic structure check
        from urllib.parse import urlparse
        parsed = urlparse(v)
        if not parsed.netloc:
            raise ValueError("URL does not contain a valid domain.")

        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class FeatureDetail(BaseModel):
    name: str
    value: Any
    description: str


class SuspiciousIndicator(BaseModel):
    indicator: str
    severity: str         # "low" | "medium" | "high"
    description: str


class ScanResult(BaseModel):
    url: str
    prediction: str             # "phishing" | "legitimate"
    risk_level: str             # "low" | "medium" | "high"
    confidence: float           # 0.0 – 1.0
    phishing_probability: float # raw prob from model
    legitimate_probability: float
    suspicious_indicators: List[SuspiciousIndicator]
    features: List[FeatureDetail]
    model_name: str
    disclaimer: str = (
        "This is an ML-based heuristic assessment and does not constitute "
        "a guaranteed security verdict. Always exercise caution with unknown URLs."
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    feature_count: int


class StatisticsResponse(BaseModel):
    total_scanned: int
    phishing_count: int
    legitimate_count: int
    phishing_rate: float
    model_name: str
    feature_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
