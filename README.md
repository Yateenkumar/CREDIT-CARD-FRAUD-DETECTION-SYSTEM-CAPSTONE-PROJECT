# Credit Card Fraud Detection System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.2%2B-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Machine Learning web application and REST API designed to detect fraudulent transactions in real time. The project combines a trained Random Forest classification model, a high-throughput **FastAPI** backend, and an interactive **Streamlit** user interface.

---

## 🏛️ System Architecture

```mermaid
flowchart LR
    subgraph Client ["Client Layer"]
        User["User / Analyst"]
        WebUI["Streamlit Frontend (:8501)"]
    end

    subgraph Service ["Microservice Layer"]
        API["FastAPI REST Server (:8000)"]
        Validator["Pydantic Schema Validation"]
    end

    subgraph Model ["Machine Learning Layer"]
        RF["Random Forest Classifier"]
        Weights[("credit_fraud.pkl")]
    end

    User -->|Enters Transaction| WebUI
    WebUI -->|POST /predict (JSON)| API
    API --> Validator
    Validator -->|Numpy Array| RF
    Weights -.->|Preloaded Weights| RF
    RF -->|Prediction: 0 / 1| API
    API -->|Response: Legitimate / Fraud| WebUI
```

---

## ✨ Features

- **Real-Time Fraud Scoring**: Classifies transactions as legitimate or fraudulent instantly.
- **Microservice & Standalone Support**:
  - Run as distributed microservices (FastAPI backend + Streamlit frontend).
  - Or run standalone in serverless environments via in-process cached model inference (`@st.cache_resource`).
- **Interactive Web Interface**: Streamlit UI allows transaction analysts to adjust amounts, origin/destination balances, transaction duration, and transfer types.
- **Production-Ready REST API**: OpenAPI / Swagger UI documentation available out of the box at `/docs`.
- **Docker & Compose Ready**: Fully containerized multi-stage builds for seamless multi-platform deployments.

---

## 📊 Dataset & Model Specification

The model is trained on the **PaySim** financial dataset, a synthetic mobile money transaction simulator that models real-world financial transfer behaviors and fraud patterns.

| Property | Value |
| :--- | :--- |
| **Model Type** | Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`) |
| **Primary Metric** | Accuracy: 99.4%, F1-Score: 0.86 |
| **Input Features** | 8 Features: `step`, `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFlaggedFraud` |
| **Target** | Binary Classification (`0: Not Fraudulent`, `1: Fraudulent`) |

---

## 📁 Repository Structure

```text
Credit-Card-Fraud-Detection/
├── backend/                  # FastAPI microservice container source
│   ├── app.py
│   ├── credit_fraud.pkl
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Streamlit UI container source
│   ├── app.py
│   ├── Dockerfile
│   ├── image.png
│   └── requirements.txt
├── docs/                     # Research papers & documentation
│   └── Credit_Card_Fraud_Detection_Research.pdf
├── Notebook/                 # Jupyter analysis and model training
│   └── Credit_Card_Fraud_Detection.ipynb
├── .github/workflows/        # Automated CI/CD pipelines
│   └── ci.yml
├── .gitignore                # Clean production gitignore rules
├── app.py                    # Root FastAPI entrypoint
├── credit_fraud.pkl          # Serialized Random Forest weights
├── deploy_hf.py              # Automated 1-click Hugging Face deployer
├── docker-compose.yml        # Orchestration config for multi-container setup
├── Dockerfile                # Root unified container definition
├── image.png                 # Web application banner asset
├── LICENSE                   # MIT Open Source License
├── requirements.txt          # Unified runtime dependencies
├── run.py                    # Dual-service local launcher script
├── start.bat                 # One-click Windows launch executable
└── streamlit_app.py          # Root Streamlit web application
```

---

## 🚀 Quickstart

### 1. Local Setup (Without Docker)

Ensure you have **Python 3.10+** installed.

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/Credit-Card-Fraud-Detection.git
cd Credit-Card-Fraud-Detection

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch both services
python run.py
```

*On Windows, you can also simply double-click **`start.bat`**.*

* **Streamlit UI**: [http://localhost:8501](http://localhost:8501)
* **FastAPI Server**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2. Docker & Docker Compose Setup

Run the entire multi-service stack with a single command:

```bash
docker compose up --build
```

---

## 🔌 API Reference

### `POST /predict`

Submit transaction feature parameters to obtain real-time fraud prediction.

**Request Body (`application/json`):**
```json
{
  "step": 1,
  "types": 1,
  "amount": 9839.64,
  "oldbalanceorig": 170136.0,
  "newbalanceorig": 160296.36,
  "oldbalancedest": 0.0,
  "newbalancedest": 0.0,
  "isflaggedfraud": 0.0
}
```

**Response (`200 OK`):**
```json
[
  "not fraudulent"
]
```

---

## ☁️ Cloud Deployment

### Deploy to Hugging Face Spaces (Free)
Run the automated deployer included in this repository:
```bash
python deploy_hf.py --username <HF_USERNAME> --token <HF_WRITE_TOKEN>
```

### Deploy to Streamlit Community Cloud (Free)
1. Push this repository to your GitHub account.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Select your repository and specify `streamlit_app.py` as the entrypoint.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
