"""
Riskora – ML Model Wrapper & Hybrid Risk Scoring Engine
=========================================================
Combines trained scikit-learn model inference with structural cybersecurity
heuristics and trusted authority domain verification.

Key principles:
  1. Lexical-only analysis: Zero network requests to target URL (No SSRF).
  2. Ground truth alignment: Model trained on PhiUSIIL dataset with 27 URL features.
  3. Defense-in-depth: ML probability calibrated with deterministic indicators
     (IP domains, abuse TLDs, credential tricks, obfuscation).
  4. Reputable authority verification: Zero false alarms on major root domains.
"""

from __future__ import annotations

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from urllib.parse import urlparse

# Ensure backend, ml, and root directory are always on sys.path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
ML_DIR = ROOT_DIR / "ml"

for _p in (str(BACKEND_DIR), str(ML_DIR), str(ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import joblib
import numpy as np
import pandas as pd

from feature_extraction import (  # noqa: E402
    extract_features,
    FEATURE_NAMES,
    FEATURE_DESCRIPTIONS,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_TLDS,
)
from schemas import ScanResult, SuspiciousIndicator, FeatureDetail  # noqa: E402

MODEL_PATH   = ML_DIR / "model" / "riskora_model.joblib"
METRICS_PATH = ML_DIR / "model" / "evaluation_metrics.json"

# Highly reputable reference domains to avoid false-positive alert fatigue
TOP_REPUTABLE_DOMAINS = {
    "google.com", "www.google.com",
    "github.com", "www.github.com",
    "microsoft.com", "www.microsoft.com",
    "apple.com", "www.apple.com",
    "amazon.com", "www.amazon.com",
    "wikipedia.org", "en.wikipedia.org",
    "youtube.com", "www.youtube.com",
    "linkedin.com", "www.linkedin.com",
    "cloudflare.com", "www.cloudflare.com",
    "mozilla.org", "www.mozilla.org",
    "python.org", "www.python.org",
    "stackoverflow.com", "www.stackoverflow.com",
}


# ---------------------------------------------------------------------------
# Suspicious Indicator Extractor
# ---------------------------------------------------------------------------
def _build_suspicious_indicators(url: str, feats: Dict[str, Any],
                                 phishing_prob: float) -> list[SuspiciousIndicator]:
    indicators: List[SuspiciousIndicator] = []
    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()
    bare_domain = domain[4:] if domain.startswith("www.") else domain

    # 1. Raw IP address as domain (High)
    if feats.get("IsDomainIP") or feats.get("is_domain_ip"):
        indicators.append(SuspiciousIndicator(
            indicator="IP address used as domain",
            severity="high",
            description="Phishing sites frequently use raw numeric IP addresses to bypass domain reputation scanners.",
        ))

    # 2. Free or high-abuse TLDs (High)
    if feats.get("has_suspicious_tld"):
        indicators.append(SuspiciousIndicator(
            indicator="High-abuse Top-Level Domain",
            severity="high",
            description=f"The domain uses a TLD commonly associated with automated spam campaigns: {', '.join(SUSPICIOUS_TLDS[:6])}…",
        ))

    # 3. Credential deception symbol '@' (High)
    if feats.get("has_at_symbol"):
        indicators.append(SuspiciousIndicator(
            indicator="'@' character in URL",
            severity="high",
            description="Browsers interpret 'user@domain' by navigating to the destination after the '@', misleading the user.",
        ))

    # 4. URL encoding obfuscation (Medium)
    if feats.get("HasObfuscation") or feats.get("has_obfuscation_chars"):
        indicators.append(SuspiciousIndicator(
            indicator="Hexadecimal / URL-encoded characters",
            severity="medium",
            description="Percent-encoded characters can be used to hide malicious keywords or path targets.",
        ))

    # 5. Suspicious action keywords in path or query (Medium)
    url_lower = url.lower()
    found_keywords = []
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in url_lower:
            # Skip if the keyword matches the legitimate brand's own domain
            if kw in bare_domain and any(bare_domain.startswith(f"{kw}.") for kw in [kw]):
                continue
            found_keywords.append(kw)

    if found_keywords:
        indicators.append(SuspiciousIndicator(
            indicator=f"Targeted security keyword(s): {', '.join(found_keywords[:4])}",
            severity="medium",
            description="Keywords such as 'login', 'verify', or 'account' in non-standard paths indicate potential credential harvesting.",
        ))

    # 6. Unencrypted plain HTTP (Medium)
    if not (feats.get("IsHTTPS") or feats.get("is_https")):
        indicators.append(SuspiciousIndicator(
            indicator="Unencrypted HTTP connection",
            severity="medium",
            description="The URL uses unencrypted HTTP. Login or credential submission over HTTP is inherently insecure.",
        ))

    # 7. Deep subdomains (Medium)
    no_subdomains = feats.get("NoOfSubDomain", 0)
    if no_subdomains >= 3:
        indicators.append(SuspiciousIndicator(
            indicator=f"Excessive subdomain depth ({no_subdomains} levels)",
            severity="medium",
            description="Phishing kits often nest trusted brand names inside deep subdomains of an unrelated attacker domain.",
        ))

    # 8. Excessive URL length (Low)
    url_len = feats.get("URLLength", len(url))
    if url_len > 120:
        indicators.append(SuspiciousIndicator(
            indicator=f"Unusually long URL structure ({url_len} chars)",
            severity="low",
            description="Abnormally long URLs are often used to conceal redirected targets or serialized token payloads.",
        ))

    # 9. Non-standard port (Low)
    if feats.get("has_port"):
        indicators.append(SuspiciousIndicator(
            indicator="Explicit non-standard port specified",
            severity="low",
            description="Web traffic on non-standard ports (other than 80 or 443) may bypass inspection policies.",
        ))

    # 10. Multiple hyphens in domain (Low)
    domain_hyphens = feats.get("domain_hyphen_count", 0)
    if domain_hyphens >= 3:
        indicators.append(SuspiciousIndicator(
            indicator=f"High domain hyphen count ({domain_hyphens})",
            severity="low",
            description="Attackers frequently separate concatenated words with multiple hyphens to mimic authentic brand names.",
        ))

    return indicators


# ---------------------------------------------------------------------------
# Composite Risk Scoring
# ---------------------------------------------------------------------------
def _compute_risk_level(phishing_prob: float, indicators: List[SuspiciousIndicator]) -> str:
    high_count = sum(1 for ind in indicators if ind.severity == "high")
    med_count  = sum(1 for ind in indicators if ind.severity == "medium")

    # High severity indicators elevate risk directly
    if high_count >= 2 or (high_count >= 1 and (phishing_prob >= 0.25 or med_count >= 1)):
        return "high"
    if high_count >= 1 or phishing_prob >= 0.70:
        return "high" if phishing_prob >= 0.50 else "medium"

    if phishing_prob >= 0.40 or med_count >= 2:
        return "medium"

    return "low"


# ---------------------------------------------------------------------------
# RiskoraModel Class
# ---------------------------------------------------------------------------
class RiskoraModel:
    def __init__(self):
        self._pipeline = None
        self._model_name = "Random Forest"
        self._feature_count = len(FEATURE_NAMES)
        self._scan_counts = {"total": 0, "phishing": 0, "legitimate": 0}

    def load(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Please run `python ml/train.py` first."
            )
        self._pipeline = joblib.load(MODEL_PATH)
        if METRICS_PATH.exists():
            with open(METRICS_PATH) as f:
                metrics = json.load(f)
            self._model_name = metrics.get("best_model", "Random Forest")
        return self

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def feature_count(self) -> int:
        return self._feature_count

    @property
    def scan_counts(self) -> dict:
        return dict(self._scan_counts)

    def predict(self, url: str) -> ScanResult:
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Call load() first.")

        # Extract features (purely lexical – no HTTP request)
        feats = extract_features(url)
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()

        # Build feature details table
        feature_details = [
            FeatureDetail(
                name=name,
                value=feats[name],
                description=FEATURE_DESCRIPTIONS.get(name, ""),
            )
            for name in FEATURE_NAMES
        ]

        # 1. Authority domain fast-path
        if hostname in TOP_REPUTABLE_DOMAINS:
            self._scan_counts["total"] += 1
            self._scan_counts["legitimate"] += 1
            return ScanResult(
                url=url,
                prediction="legitimate",
                risk_level="low",
                confidence=0.995,
                phishing_probability=0.005,
                legitimate_probability=0.995,
                suspicious_indicators=[],
                features=feature_details,
                model_name=self._model_name,
            )

        # 2. Scikit-learn Pipeline Inference
        X = pd.DataFrame([[feats[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
        probs = self._pipeline.predict_proba(X)[0]
        # In our calibrated model: class 1 = Phishing, class 0 = Legitimate
        phishing_prob   = float(probs[1])
        legitimate_prob = float(probs[0])

        indicators = _build_suspicious_indicators(url, feats, phishing_prob)
        high_indicators = sum(1 for ind in indicators if ind.severity == "high")

        # Determine prediction: high probability or critical security red flags
        if phishing_prob >= 0.50 or high_indicators >= 2:
            prediction = "phishing"
            confidence = max(phishing_prob, 0.85 if high_indicators >= 2 else phishing_prob)
        else:
            prediction = "legitimate"
            confidence = legitimate_prob

        risk_level = _compute_risk_level(phishing_prob, indicators)

        # Update session telemetry
        self._scan_counts["total"] += 1
        if prediction == "phishing":
            self._scan_counts["phishing"] += 1
        else:
            self._scan_counts["legitimate"] += 1

        return ScanResult(
            url=url,
            prediction=prediction,
            risk_level=risk_level,
            confidence=round(confidence, 4),
            phishing_probability=round(phishing_prob, 4),
            legitimate_probability=round(legitimate_prob, 4),
            suspicious_indicators=indicators,
            features=feature_details,
            model_name=self._model_name,
        )


# Singleton instance
riskora_model = RiskoraModel()
