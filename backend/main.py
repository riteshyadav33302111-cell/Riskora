"""
Riskora – FastAPI Backend
==========================
Endpoints:
  GET  /            → welcome message
  GET  /health      → model health check
  POST /predict     → scan a URL
  GET  /statistics  → aggregate session stats

Security notes:
  - Input validated with Pydantic (URL scheme check, length limit).
  - Feature extraction is purely lexical – the backend never fetches the
    user-submitted URL, eliminating SSRF risk.
  - CORS is configured; tighten allowed_origins for production.

Usage (development):
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    URLScanRequest, ScanResult,
    HealthResponse, StatisticsResponse, ErrorResponse,
)
from model import riskora_model

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("riskora")

# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Riskora ML model…")
    try:
        riskora_model.load()
        logger.info(f"Model loaded: {riskora_model.model_name}")
    except FileNotFoundError as exc:
        logger.error(str(exc))
        logger.warning("Server will start but /predict will fail until model is trained.")
    yield
    logger.info("Riskora backend shutting down.")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Riskora – Phishing URL Detection API",
    description=(
        "Machine-learning powered phishing URL detection. "
        "Features are extracted purely from the URL string; "
        "the backend never fetches submitted URLs."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS – allow the Vite dev server and the Vercel deployment
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        # Add your production frontend URL here, e.g.:
        # "https://riskora.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)

# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", summary="Welcome")
async def root():
    return {
        "name": "Riskora",
        "description": "Intelligent Phishing URL Detection System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
)
async def health():
    return HealthResponse(
        status="ok" if riskora_model.is_loaded else "degraded",
        model_loaded=riskora_model.is_loaded,
        model_name=riskora_model.model_name,
        feature_count=riskora_model.feature_count,
    )


@app.post(
    "/predict",
    response_model=ScanResult,
    summary="Scan a URL for phishing",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
)
async def predict(request: URLScanRequest):
    if not riskora_model.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded. Please contact the administrator.",
        )

    try:
        result = riskora_model.predict(request.url)
        logger.info(
            f"Scanned URL (truncated): {request.url[:60]}… → "
            f"{result.prediction} ({result.risk_level} risk, "
            f"conf={result.confidence:.2f})"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Prediction error")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


@app.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Aggregate session statistics",
)
async def statistics():
    counts = riskora_model.scan_counts
    total  = counts["total"]
    phish  = counts["phishing"]
    legit  = counts["legitimate"]

    return StatisticsResponse(
        total_scanned=total,
        phishing_count=phish,
        legitimate_count=legit,
        phishing_rate=round(phish / total, 4) if total > 0 else 0.0,
        model_name=riskora_model.model_name,
        feature_count=riskora_model.feature_count,
    )
