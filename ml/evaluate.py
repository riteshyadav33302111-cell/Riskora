"""
Riskora – Model Evaluation Script
====================================
Loads the saved Random Forest model and prints the verified evaluation report
derived from the PhiUSIIL Phishing URL Dataset.

Usage:
    python ml/evaluate.py
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ML_DIR = Path(__file__).parent
sys.path.insert(0, str(ML_DIR))
from feature_extraction import FEATURE_NAMES, extract_features  # noqa

MODEL_PATH = ML_DIR / "model" / "riskora_model.joblib"
METRICS_PATH = ML_DIR / "model" / "evaluation_metrics.json"


def load_saved_metrics():
    if not METRICS_PATH.exists():
        print("No metrics file found. Run train.py first.")
        return
    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    print("\n" + "=" * 75)
    print("  RISKORA – Evaluation Results (PhiUSIIL Phishing URL Dataset)")
    print("=" * 75)
    print(f"  Best Selected Model : {metrics['best_model']}")
    print(f"  Target Convention   : {metrics.get('target_definition', '1=Phishing, 0=Legitimate')}")
    print(f"  Active Feature Count: {len(metrics['feature_names'])}")

    print("\n" + "-" * 75)
    header = f"{'Algorithm':<22} {'CV Acc':>8} {'CV F1':>8} {'CV AUC':>8} {'Test Acc':>9} {'Test P':>8} {'Test R':>8} {'Test F1':>8} {'Test AUC':>9}"
    print(header)
    print("-" * 75)

    for m in metrics["models"]:
        print(
            f"{m['name']:<22}"
            f" {m['cv_accuracy_mean']:>8.4f}"
            f" {m['cv_f1_mean']:>8.4f}"
            f" {m['cv_roc_auc_mean']:>8.4f}"
            f" {m['test_accuracy']:>9.4f}"
            f" {m['test_precision']:>8.4f}"
            f" {m['test_recall']:>8.4f}"
            f" {m['test_f1']:>8.4f}"
            f" {m['test_roc_auc']:>9.4f}"
        )
    print("-" * 75)


def quick_predict(urls: list[str]):
    if not MODEL_PATH.exists():
        print("Model file not found. Run train.py first.")
        return

    model = joblib.load(MODEL_PATH)
    print("\n" + "=" * 75)
    print("  Sample URL Model Verification Check")
    print("=" * 75)

    for url in urls:
        feats = extract_features(url)
        X = pd.DataFrame([[feats[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0]
        # In our trained model: 1 = Phishing, 0 = Legitimate
        label = "PHISHING" if pred == 1 else "LEGITIMATE"
        confidence = prob[pred]
        print(f"\n  URL         : {url[:70]}")
        print(f"  Prediction  : {label} (Confidence: {confidence:.2%})")
        print(f"  Probability : Legit={prob[0]:.4f}, Phishing={prob[1]:.4f}")


if __name__ == "__main__":
    load_saved_metrics()
    quick_predict([
        "https://www.google.com",
        "https://github.com/openai/openai-python",
        "http://bank-security-verify.tk/account/login.php?token=xyz",
        "http://192.168.1.1/admin@paypal.com",
        "http://free-iphone-winner.xyz/claim?user=test&session=abc",
    ])
