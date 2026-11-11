"""
Riskora – Model Training Script (v3 – Calibrated Target)
=========================================================
Trains four classifiers on the PhiUSIIL Phishing URL Dataset.

TARGET CONVENTION CLARIFICATION:
  In the official PhiUSIIL dataset (Patil & Nayak et al., 2023):
    - label == 1 denotes LEGITIMATE URLs (134,850 samples)
    - label == 0 denotes PHISHING URLs   (100,945 samples)
  
  For our cybersecurity ML pipeline, we map:
    - y = 1 -> PHISHING (positive detection class)
    - y = 0 -> LEGITIMATE (negative baseline class)
  
  This ensures:
    - Recall = % of phishing attacks detected
    - Precision = % of phishing alerts that are true attacks
    - ROC-AUC measures true positive rate (phishing) vs false alarm rate

Models trained and compared:
  1. Logistic Regression
  2. Decision Tree
  3. Random Forest
  4. Gradient Boosting

Dataset: PhiUSIIL Phishing URL Dataset
Source : https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

from __future__ import annotations

import os
import sys
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    ConfusionMatrixDisplay,
)

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
ML_DIR = Path(__file__).parent
DATASET_PATH = ML_DIR / "dataset" / "PhiUSIIL_Phishing_URL_Dataset.csv"
MODEL_DIR = ML_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ML_DIR))
from feature_extraction import FEATURE_NAMES, extract_features  # noqa: E402

# Original URL-only columns from PhiUSIIL dataset
ORIGINAL_URL_FEATURES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
]

SUPPLEMENTARY_FEATURES = [
    "url_entropy",
    "has_suspicious_tld",
    "has_at_symbol",
    "has_port",
    "url_path_depth",
    "domain_hyphen_count",
    "suspicious_keyword_count",
    "no_of_dots",
    "no_of_hyphens",
    "query_param_count",
    "domain_has_numbers",
]

ALL_FEATURES = ORIGINAL_URL_FEATURES + SUPPLEMENTARY_FEATURES
assert ALL_FEATURES == FEATURE_NAMES


# ---------------------------------------------------------------------------
# 1. Load dataset & establish ground truth
# ---------------------------------------------------------------------------
def load_dataset() -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("1. LOADING DATASET & VALIDATING GROUND TRUTH")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH, encoding="utf-8-sig", low_memory=False)
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    print(f"   Shape: {df.shape}")
    print(f"   Raw dataset label distribution:")
    print(df["label"].value_counts().to_string())
    print("   -> In PhiUSIIL: 1 = Legitimate (134,850), 0 = Phishing (100,945)")

    n_dup = df.duplicated().sum()
    if n_dup > 0:
        df = df.drop_duplicates()
        print(f"   Dropped duplicates -> {df.shape}")

    df = df.dropna(subset=["URL", "label"])
    return df


# ---------------------------------------------------------------------------
# 2. Feature Engineering
# ---------------------------------------------------------------------------
def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    print("\n" + "=" * 60)
    print("2. FEATURE ENGINEERING (URL-only features, no HTTP requests)")
    print("=" * 60)

    # 1. Dataset-native URL features
    X_orig = df[ORIGINAL_URL_FEATURES].copy().reset_index(drop=True)
    X_orig = X_orig.apply(pd.to_numeric, errors="coerce").fillna(0)

    # 2. Supplementary heuristic features
    print(f"   Computing {len(SUPPLEMENTARY_FEATURES)} supplementary features from {len(df)} URLs…")
    t0 = time.time()
    supp_rows = []
    for url in df["URL"]:
        feats = extract_features(str(url))
        supp_rows.append([feats[f] for f in SUPPLEMENTARY_FEATURES])
    X_supp = pd.DataFrame(supp_rows, columns=SUPPLEMENTARY_FEATURES)
    print(f"   Done in {time.time() - t0:.1f}s")

    X = pd.concat([X_orig, X_supp], axis=1)

    # TARGET: 1 = Phishing, 0 = Legitimate
    y = (df["label"] == 0).astype(int).reset_index(drop=True)

    print(f"\n   Feature matrix shape: {X.shape}")
    print(f"   Model Target (y: 1=Phishing, 0=Legitimate):")
    print(f"     Phishing   (1): {(y == 1).sum():,}")
    print(f"     Legitimate (0): {(y == 0).sum():,}")

    corr = X.corrwith(y).sort_values()
    print(f"\n   Top 5 features correlating with PHISHING (1):")
    print(corr.tail(5).to_string())
    print(f"\n   Top 5 features correlating with LEGITIMATE (0):")
    print(corr.head(5).to_string())

    return X, y


# ---------------------------------------------------------------------------
# 3. Train / Test Split
# ---------------------------------------------------------------------------
def split_data(X, y):
    print("\n" + "=" * 60)
    print("3. TRAIN / TEST SPLIT (80/20 Stratified)")
    print("=" * 60)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"   Train set: {X_train.shape} | Test set: {X_test.shape}")
    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------------------------
# 4. Pipelines
# ---------------------------------------------------------------------------
def build_pipelines() -> dict:
    return {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                max_iter=1000, C=1.0, solver="lbfgs",
                class_weight="balanced", random_state=42,
            )),
        ]),
        "Decision Tree": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", DecisionTreeClassifier(
                max_depth=15, min_samples_split=10, min_samples_leaf=5,
                class_weight="balanced", random_state=42,
            )),
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=100, max_depth=20, min_samples_split=5,
                min_samples_leaf=2, n_jobs=-1, class_weight="balanced",
                random_state=42,
            )),
        ]),
        "Gradient Boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.1,
                subsample=0.8, random_state=42,
            )),
        ]),
    }


# ---------------------------------------------------------------------------
# 5. Training & Evaluation
# ---------------------------------------------------------------------------
def evaluate_model(name, pipeline, X_train, y_train, X_test, y_test) -> dict:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = cross_validate(
        pipeline, X_train, y_train,
        cv=cv,
        scoring=["accuracy", "precision", "recall", "f1", "roc_auc"],
        n_jobs=-1,
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    return {
        "name": name,
        "pipeline": pipeline,
        "cv_accuracy_mean": float(cv_results["test_accuracy"].mean()),
        "cv_accuracy_std":  float(cv_results["test_accuracy"].std()),
        "cv_precision_mean": float(cv_results["test_precision"].mean()),
        "cv_recall_mean":    float(cv_results["test_recall"].mean()),
        "cv_f1_mean":       float(cv_results["test_f1"].mean()),
        "cv_roc_auc_mean":  float(cv_results["test_roc_auc"].mean()),
        "test_accuracy":    float(accuracy_score(y_test, y_pred)),
        "test_precision":   float(precision_score(y_test, y_pred)),
        "test_recall":      float(recall_score(y_test, y_pred)),
        "test_f1":          float(f1_score(y_test, y_pred)),
        "test_roc_auc":     float(roc_auc_score(y_test, y_prob)),
        "y_pred": y_pred,
        "y_prob": y_prob,
    }


def train_all(X_train, X_test, y_train, y_test) -> list[dict]:
    print("\n" + "=" * 60)
    print("4. MODEL TRAINING & 5-FOLD CROSS-VALIDATION")
    print("=" * 60)
    pipelines = build_pipelines()
    results = []
    for name, pipeline in pipelines.items():
        print(f"\n   ▶ {name}…", end=" ", flush=True)
        t0 = time.time()
        res = evaluate_model(name, pipeline, X_train, y_train, X_test, y_test)
        print(f"done ({time.time() - t0:.1f}s)")
        results.append(res)
    return results


# ---------------------------------------------------------------------------
# 6. Comparison
# ---------------------------------------------------------------------------
def print_comparison(results) -> dict:
    print("\n" + "=" * 60)
    print("5. MODEL COMPARISON RESULTS")
    print("=" * 60)
    h = f"{'Model':<22} {'CV Acc':>8} {'CV F1':>8} {'CV AUC':>8} {'Test Acc':>10} {'Test P':>8} {'Test R':>8} {'Test F1':>8} {'Test AUC':>10}"
    print(f"\n{h}")
    print("-" * len(h))
    for r in results:
        print(
            f"{r['name']:<22}"
            f" {r['cv_accuracy_mean']:>8.4f}"
            f" {r['cv_f1_mean']:>8.4f}"
            f" {r['cv_roc_auc_mean']:>8.4f}"
            f" {r['test_accuracy']:>10.4f}"
            f" {r['test_precision']:>8.4f}"
            f" {r['test_recall']:>8.4f}"
            f" {r['test_f1']:>8.4f}"
            f" {r['test_roc_auc']:>10.4f}"
        )
    best = max(results, key=lambda r: r["test_roc_auc"])
    print(f"\n   ★ Best model (by ROC-AUC): {best['name']}")
    return best


# ---------------------------------------------------------------------------
# 7. Plots
# ---------------------------------------------------------------------------
def plot_confusion_matrices(results, y_test):
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    if n == 1:
        axes = [axes]
    for ax, res in zip(axes, results):
        cm = confusion_matrix(y_test, res["y_pred"])
        disp = ConfusionMatrixDisplay(cm, display_labels=["Legitimate", "Phishing"])
        disp.plot(ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(res["name"], fontsize=11, fontweight="bold")
    plt.suptitle("Confusion Matrices – Hold-out Test Set (y=1: Phishing)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = MODEL_DIR / "confusion_matrices.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   Saved → {out}")


def plot_roc_comparison(results, y_test):
    from sklearn.metrics import roc_curve
    plt.figure(figsize=(8, 6))
    for res in results:
        fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
        plt.plot(fpr, tpr, label=f"{res['name']} (AUC={res['test_roc_auc']:.4f})", lw=2)
    plt.plot([0, 1], [0, 1], "k--", lw=1)
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity / Recall)")
    plt.title("ROC Curves – Phishing Detection Performance")
    plt.legend(loc="lower right")
    plt.tight_layout()
    out = MODEL_DIR / "roc_curves.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   Saved → {out}")


# ---------------------------------------------------------------------------
# 8. Save
# ---------------------------------------------------------------------------
def save_best_model(best, results, y_test):
    print("\n" + "=" * 60)
    print("6. SAVING MODEL & METRICS")
    print("=" * 60)
    model_path = MODEL_DIR / "riskora_model.joblib"
    joblib.dump(best["pipeline"], model_path)
    print(f"   Model saved → {model_path}")

    metrics = {
        "best_model": best["name"],
        "target_definition": "1=Phishing, 0=Legitimate",
        "dataset_source": "UCI Machine Learning Repository - PhiUSIIL Phishing URL Dataset",
        "feature_names": FEATURE_NAMES,
        "models": [],
    }
    for r in results:
        metrics["models"].append({
            "name": r["name"],
            "cv_accuracy_mean": round(r["cv_accuracy_mean"], 6),
            "cv_accuracy_std":  round(r["cv_accuracy_std"], 6),
            "cv_precision_mean": round(r["cv_precision_mean"], 6),
            "cv_recall_mean":    round(r["cv_recall_mean"], 6),
            "cv_f1_mean":       round(r["cv_f1_mean"], 6),
            "cv_roc_auc_mean":  round(r["cv_roc_auc_mean"], 6),
            "test_accuracy":    round(r["test_accuracy"], 6),
            "test_precision":   round(r["test_precision"], 6),
            "test_recall":      round(r["test_recall"], 6),
            "test_f1":          round(r["test_f1"], 6),
            "test_roc_auc":     round(r["test_roc_auc"], 6),
            "classification_report": classification_report(
                y_test, r["y_pred"],
                target_names=["Legitimate", "Phishing"],
                output_dict=True,
            ),
        })

    metrics_path = MODEL_DIR / "evaluation_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"   Metrics saved → {metrics_path}")
    return metrics


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n" + "█" * 60)
    print("  RISKORA – ML Training Pipeline (Ground Truth Calibrated)")
    print("█" * 60)
    t_start = time.time()

    df = load_dataset()
    X, y = engineer_features(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    results = train_all(X_train, X_test, y_train, y_test)
    best = print_comparison(results)

    print("\n" + "=" * 60)
    print("5b. GENERATING EVALUATION PLOTS")
    print("=" * 60)
    plot_confusion_matrices(results, y_test)
    plot_roc_comparison(results, y_test)

    metrics = save_best_model(best, results, y_test)

    total = time.time() - t_start
    best_m = next(m for m in metrics["models"] if m["name"] == metrics["best_model"])
    print(f"\n{'█' * 60}")
    print(f"  Training successfully completed in {total:.1f}s")
    print(f"  Best Model   : {metrics['best_model']}")
    print(f"  Test ROC-AUC : {best_m['test_roc_auc']}")
    print(f"  Test F1      : {best_m['test_f1']}")
    print(f"  Test Accuracy: {best_m['test_accuracy']}")
    print(f"{'█' * 60}\n")


if __name__ == "__main__":
    main()
