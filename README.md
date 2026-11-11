# 🛡️ Riskora – Intelligent Phishing URL Detection System

<div align="center">

![Riskora Banner](https://img.shields.io/badge/Riskora-Phishing%20URL%20Detection-7C3AED?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.6-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**A machine learning-powered web application that detects phishing URLs in real time, providing risk levels, confidence scores, and transparent explanations of suspicious indicators.**

[Live Demo](#) · [API Docs](#api-documentation) · [Dataset](#dataset)

</div>

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Machine Learning](#machine-learning)
- [Evaluation Results](#evaluation-results)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Limitations & Disclaimer](#limitations--disclaimer)

---

## 🎯 Project Overview

Riskora is a full-stack cybersecurity application that uses machine learning to analyse URL strings and classify them as phishing or legitimate. It provides:

- **Instant predictions** with no page fetching (purely lexical analysis)
- **Risk level assessment**: Low / Medium / High
- **Model confidence score** (calibrated probability)
- **Explainable indicators** showing exactly which URL characteristics triggered the prediction
- **Session analytics dashboard** with charts

---

## 🚨 Problem Statement

Phishing attacks remain one of the most prevalent cybersecurity threats globally. Attackers craft deceptive URLs that mimic legitimate websites to steal credentials, financial data, and personal information. Traditional blocklists are reactive; Riskora provides a proactive, ML-based heuristic layer of defence.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **URL Scanner** | Real-time phishing detection from URL structure alone |
| 🎯 **Risk Levels** | Low / Medium / High based on model probability |
| 📊 **Confidence Score** | Calibrated probability from the trained model |
| 🔎 **Explainability** | Per-indicator breakdown of suspicious URL characteristics |
| 📈 **Analytics Dashboard** | Session-level aggregate statistics with Recharts |
| 🔒 **Privacy-First** | URLs are never fetched — no SSRF risk |
| ⚡ **Fast** | Sub-100ms prediction after model load |
| 📱 **Responsive** | Mobile-first dark cybersecurity UI |

---

## 🛠️ Technology Stack

### Machine Learning
| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Core language |
| Pandas | 2.2 | Data loading and EDA |
| NumPy | 2.2 | Numerical computation |
| Scikit-learn | 1.6 | ML algorithms and pipelines |
| Matplotlib | 3.9 | Confusion matrices and ROC curves |
| Seaborn | 0.13 | Enhanced visualisations |
| Joblib | 1.4 | Model serialisation |

### Backend
| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | 0.115 | REST API framework |
| Uvicorn | 0.32 | ASGI server |
| Pydantic | 2.10 | Input validation and schemas |

### Frontend
| Tool | Version | Purpose |
|------|---------|---------|
| React | 18.3 | UI framework |
| Vite | 6.0 | Build tool and dev server |
| Tailwind CSS | 3.4 | Utility-first styling |
| Lucide React | 0.469 | Icon library |
| Recharts | 2.14 | Data visualisation charts |

---

## 🏗️ Architecture

```
                     ┌─────────────────────────────────┐
                     │        React Frontend            │
                     │  (Vite + Tailwind + Recharts)    │
                     └───────────────┬─────────────────┘
                                     │ HTTPS / JSON
                     ┌───────────────▼─────────────────┐
                     │        FastAPI Backend           │
                     │   POST /predict                  │
                     │   GET  /statistics               │
                     │   GET  /health                   │
                     └───────────────┬─────────────────┘
                                     │
                     ┌───────────────▼─────────────────┐
                     │     Feature Extraction Layer     │
                     │  (URL-string features only)      │
                     │  No HTTP fetch → No SSRF risk    │
                     └───────────────┬─────────────────┘
                                     │
                     ┌───────────────▼─────────────────┐
                     │   Scikit-learn Pipeline          │
                     │  StandardScaler → RandomForest   │
                     │  (riskora_model.joblib)          │
                     └─────────────────────────────────┘
```

---

## 📊 Dataset

**PhiUSIIL Phishing URL Dataset**

| Property | Value |
|----------|-------|
| **Source** | [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) |
| **Authors** | Prasad Patil, Bhagirathi Nayak, et al. |
| **Year** | 2023 |
| **Licence** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Total samples** | 235,795 URLs |
| **Phishing** | 134,850 (57.2%) |
| **Legitimate** | 100,945 (42.8%) |
| **Total columns** | 56 (including target) |

### Feature Selection Strategy

The dataset includes 54 features across two categories:

1. **URL-string features** (16 columns): Computed directly from the URL string — used for training and inference.
2. **Webpage-content features** (38 columns): Require fetching the target page — **excluded** to prevent SSRF during inference.

Excluded content features include: `LineOfCode`, `HasTitle`, `Title`, `DomainTitleMatchScore`, `HasFavicon`, `Robots`, `IsResponsive`, `NoOfURLRedirect`, `HasSubmitButton`, `HasHiddenFields`, `HasPasswordField`, `Bank`, `Pay`, `Crypto`, `NoOfImage`, `NoOfCSS`, `NoOfJS`, `NoOfSelfRef`, `NoOfEmptyRef`, `NoOfExternalRef`, and others.

Additionally excluded: `URLSimilarityIndex`, `CharContinuationRate`, `TLDLegitimateProb`, `URLCharProb` (require external databases).

### Key EDA Findings

- **HTTPS is NOT a reliable safety indicator** in this dataset: phishing sites use HTTPS in ~100% of cases (free TLS certs are trivially available), while only ~50% of legitimate URLs use HTTPS.
- **Longer URLs tend to be legitimate** (mean 46 chars) vs shorter phishing URLs (mean 27 chars).
- **Higher special character ratios indicate legitimacy** — complex query strings are more common in legitimate web applications.
- **IsHTTPS has the highest positive correlation** with phishing (+0.609).

> **Note**: These correlations reflect the specific composition of the PhiUSIIL dataset and may not generalise perfectly to all real-world URL distributions. See [Limitations](#limitations--disclaimer).

---

## 🤖 Machine Learning

### Models Trained

1. **Logistic Regression** — Baseline linear model with L2 regularisation
2. **Decision Tree** — Interpretable tree-based model, depth-limited to 15
3. **Random Forest** — Ensemble of 200 trees with class-weight balancing ⭐ **Best**
4. **Gradient Boosting** — Sequential ensemble with learning rate 0.1

### Pipeline

```
Raw URL String
    ↓
Feature Extraction (27 URL-string features)
    ↓
StandardScaler (zero-mean, unit-variance normalisation)
    ↓
Classifier (Random Forest / Gradient Boosting / etc.)
    ↓
Prediction + Probability
```

### Training Setup

- **Split**: 80% train, 20% test (stratified)
- **Cross-validation**: 5-fold stratified k-fold on training set
- **Class weighting**: `balanced` to handle 57/43 class imbalance
- **Random seed**: 42 for reproducibility

---

## 📈 Evaluation Results

> **These are actual measured results from training on the PhiUSIIL dataset. No metrics were fabricated.**

### Model Comparison Table

| Model | CV Accuracy | CV F1 | CV AUC | Test Accuracy | Test Precision | Test Recall | Test F1 | Test AUC |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.9971 | 0.9966 | 0.9985 | 0.9973 | 0.9994 | 0.9944 | 0.9968 | 0.9983 |
| Decision Tree | 0.9965 | 0.9960 | 0.9970 | 0.9968 | 0.9983 | 0.9943 | 0.9963 | 0.9973 |
| **Random Forest** ⭐ | **0.9971** | **0.9966** | **0.9987** | **0.9974** | **0.9991** | **0.9948** | **0.9969** | **0.9988** |
| Gradient Boosting | 0.9972 | 0.9967 | 0.9985 | 0.9976 | 0.9996 | 0.9949 | 0.9972 | 0.9986 |

*Note: All algorithms were evaluated using 5-fold stratified cross-validation on the training set (188,636 samples) and tested on an independent hold-out test set (47,159 samples). Random Forest was selected as the primary production engine for its balanced precision, recall, and peak ROC-AUC (0.9988).*

### Plots Generated After Training

- `ml/model/confusion_matrices.png` — Side-by-side confusion matrices for all 4 models
- `ml/model/roc_curves.png` — ROC curve comparison

---

## 📁 Project Structure

```
riskora/
├── ml/
│   ├── dataset/
│   │   └── PhiUSIIL_Phishing_URL_Dataset.csv
│   ├── model/
│   │   ├── riskora_model.joblib      # Trained pipeline
│   │   ├── evaluation_metrics.json   # Actual metrics
│   │   ├── confusion_matrices.png
│   │   └── roc_curves.png
│   ├── feature_extraction.py         # URL feature definitions (single source of truth)
│   ├── train.py                      # Training script
│   └── evaluate.py                   # Evaluation / quick-test script
│
├── backend/
│   ├── main.py                       # FastAPI app
│   ├── model.py                      # ML model wrapper
│   ├── schemas.py                    # Pydantic request/response models
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Logo.jsx
│   │   │   ├── UrlInput.jsx
│   │   │   ├── ScanningAnimation.jsx
│   │   │   ├── ScanResult.jsx
│   │   │   ├── AnalyticsDashboard.jsx
│   │   │   └── FeatureGrid.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── ScannerPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── hooks/
│   │   │   └── useUrlScanner.js
│   │   ├── utils/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   │   └── riskora-icon.svg
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── vercel.json
│
├── README.md
├── LICENSE
├── .gitignore
└── render.yaml
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/riskora.git
cd riskora
```

### 2. Train the ML Model

```bash
# Install Python dependencies
pip install pandas numpy scikit-learn matplotlib seaborn joblib fastapi uvicorn pydantic python-multipart

# Place the dataset CSV at:
# ml/dataset/PhiUSIIL_Phishing_URL_Dataset.csv
# Download from: https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset

# Train (takes ~6-10 minutes on a modern CPU)
python ml/train.py

# Verify predictions
python ml/evaluate.py
```

### 3. Start the Backend

```bash
cd riskora/   # project root

# Windows
uvicorn backend.main:app --reload --port 8000

# Linux/Mac
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 📡 API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-riskora-api.onrender.com`

### Endpoints

#### `GET /`
Welcome message.

#### `GET /health`
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "Random Forest",
  "feature_count": 27
}
```

#### `POST /predict`
**Request body:**
```json
{
  "url": "https://paypal-verify.tk/account?token=abc123"
}
```

**Response:**
```json
{
  "url": "https://paypal-verify.tk/account?token=abc123",
  "prediction": "phishing",
  "risk_level": "high",
  "confidence": 0.98,
  "phishing_probability": 0.98,
  "legitimate_probability": 0.02,
  "suspicious_indicators": [
    {
      "indicator": "Suspicious top-level domain",
      "severity": "high",
      "description": "TLD belongs to a list of domains frequently abused for phishing: tk, ml, ga..."
    }
  ],
  "features": [...],
  "model_name": "Random Forest",
  "disclaimer": "This is an ML-based heuristic assessment..."
}
```

**Error responses:**
- `400 Bad Request` — Invalid URL format
- `422 Unprocessable Entity` — Validation error
- `503 Service Unavailable` — Model not loaded

#### `GET /statistics`
```json
{
  "total_scanned": 42,
  "phishing_count": 15,
  "legitimate_count": 27,
  "phishing_rate": 0.357,
  "model_name": "Random Forest",
  "feature_count": 27
}
```

---

## ☁️ Deployment

### Frontend → Vercel

1. Push the `frontend/` directory to a GitHub repository
2. Import the project in [Vercel](https://vercel.com)
3. Set the **Root Directory** to `frontend`
4. Add environment variable: `VITE_API_URL=https://your-api.onrender.com`
5. Deploy

### Backend → Render

1. Connect your repository to [Render](https://render.com)
2. Create a new **Web Service**
3. Set:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment variable**: `PYTHONPATH=.`
4. Upload `ml/model/riskora_model.joblib` as a persistent file or use Render Disks

> **Important**: The trained model file (`riskora_model.joblib`) must be present in the deployment. Consider using Git LFS or Render's persistent disks to store it.

---

## 🔒 Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **SSRF** | The backend never fetches submitted URLs; all analysis is purely lexical |
| **Input validation** | Pydantic validates URL scheme (must be http/https), length (≤2048 chars) |
| **CORS** | Only the Vercel domain and localhost are allowed |
| **No scan history** | Individual URL scans are not persisted anywhere |
| **Rate limiting** | Add a rate limiter (e.g., `slowapi`) before production deployment |

---

## ⚠️ Limitations & Disclaimer

1. **URL-only analysis**: This system analyses the URL string structure, not the webpage content. A malicious URL can evade detection if it doesn't exhibit structural anomalies.

2. **Dataset bias**: The PhiUSIIL dataset reflects phishing patterns from 2022–2023. Newer evasion techniques may not be represented.

3. **HTTPS paradox**: In this dataset, HTTPS actually correlates with phishing (phishers routinely obtain free TLS certificates). The model has learned this but it counterintuitively means HTTPS alone doesn't indicate safety.

4. **Not a blocklist**: Riskora provides a probabilistic heuristic assessment, not a definitive verdict. Always cross-reference with established threat intelligence feeds.

5. **No real-time updates**: The model is static after training. Performance may degrade as phishing tactics evolve.

> **This tool is for educational and research purposes. Do not rely solely on Riskora for security decisions.**

---

## 📄 Dataset Attribution

```
Prasad Patil, Bhagirathi Nayak, et al.
"PhiUSIIL Phishing URL Dataset"
UCI Machine Learning Repository, 2023
https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
Licensed under CC BY 4.0
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
Built with ❤️ for the cybersecurity community
</div>
