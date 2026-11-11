"""
Riskora – Comprehensive Backend Integration Tests
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.resolve()
ml_dir = backend_dir.parent / "ml"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(ml_dir))

from fastapi.testclient import TestClient
from main import app

def run_tests():
    with TestClient(app) as client:
        # 1. Health check
        r = client.get("/health")
        assert r.status_code == 200
        health = r.json()
        assert health["status"] == "ok"
        assert health["model_loaded"] is True
        print(f"Health Check: OK (Model: {health['model_name']}, Features: {health['feature_count']})")

        # 2. Test variety of URLs
        test_cases = [
            ("https://www.google.com", "legitimate", "low"),
            ("https://github.com/openai/openai-python", "legitimate", "low"),
            ("http://bank-security-verify.tk/account/login.php?token=xyz", None, "high"),
            ("http://192.168.1.1/admin@paypal.com", None, "high"),
        ]

        for url, expected_pred, expected_min_risk in test_cases:
            r = client.post("/predict", json={"url": url})
            assert r.status_code == 200
            res = r.json()
            pred = res["prediction"]
            risk = res["risk_level"]
            conf = res["confidence"]
            indicators = res["suspicious_indicators"]

            print(f"\nURL: {url}")
            print(f"  Prediction : {pred.upper()} (Confidence: {conf:.2%})")
            print(f"  Risk Level : {risk.upper()}")
            print(f"  Indicators : {len(indicators)}")
            for ind in indicators:
                print(f"    - [{ind['severity'].upper()}] {ind['indicator']}")

            if expected_pred:
                assert pred == expected_pred, f"Expected {expected_pred}, got {pred}"
            if expected_min_risk == "high":
                assert risk in ("high", "medium"), f"Expected elevated risk, got {risk}"

        # 3. Validation tests
        invalid_urls = [
            "ftp://files.example.com",
            "just-a-string",
            "http://",
            "https://",
            "javascript:void(0)",
        ]
        print("\nInput Validation Tests:")
        for bad_url in invalid_urls:
            r = client.post("/predict", json={"url": bad_url})
            assert r.status_code in (400, 422), f"Should reject {bad_url}"
            print(f"  Rejected '{bad_url}' -> HTTP {r.status_code}")

        # 4. Aggregate statistics check
        r = client.get("/statistics")
        assert r.status_code == 200
        stats = r.json()
        print("\nAggregate Statistics:")
        print(f"  Total Scanned : {stats['total_scanned']}")
        print(f"  Phishing      : {stats['phishing_count']}")
        print(f"  Legitimate    : {stats['legitimate_count']}")
        print(f"  Phishing Rate : {stats['phishing_rate']:.1%}")

        print("\nAll integration tests passed with 100% success!")

if __name__ == "__main__":
    run_tests()
