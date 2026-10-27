"""
SentinelFraud: Enterprise Transaction Risk & Fraud Detection API
Production-Ready FastAPI Microservice with Real-Time Risk Scoring,
XAI Adverse Action Reason Codes, and Batch Evaluation.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
import engine

app = FastAPI(
    title="SentinelFraud Enterprise API",
    description="High-Throughput Financial Transaction Risk Engine with Hybrid ML + Rule-Based Decisioning & Explainable AI.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class TransactionPayload(BaseModel):
    step: int = Field(..., ge=1, le=744, description="Transaction hour index (1 - 744)")
    types: int = Field(..., ge=0, le=4, description="Transfer type: 0: Cash In, 1: Cash Out, 2: Debit, 3: Payment, 4: Transfer")
    amount: float = Field(..., ge=0.0, description="Transaction monetary amount ($ USD)")
    oldbalanceorig: float = Field(..., ge=0.0, description="Origin account balance prior to transaction")
    newbalanceorig: float = Field(..., ge=0.0, description="Origin account balance subsequent to transaction")
    oldbalancedest: float = Field(..., ge=0.0, description="Destination account balance prior to transaction")
    newbalancedest: float = Field(..., ge=0.0, description="Destination account balance subsequent to transaction")
    isflaggedfraud: Optional[float] = Field(0.0, description="System institutional high-value indicator")

class BatchPayload(BaseModel):
    transactions: List[TransactionPayload]

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_class=PlainTextResponse)
def root():
    return (
        "SentinelFraud Enterprise Risk Engine v2.0 Online\n"
        "API Documentation: Visit /docs for Swagger UI or /redoc for ReDoc.\n"
    )

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    try:
        model = engine.get_model()
        return {
            "status": "healthy",
            "model_loaded": True,
            "version": "2.0.0",
            "features_monitored": 8
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model unavailable: {e}")

@app.post("/predict")
@app.post("/predict/")
def predict(tx: TransactionPayload):
    """
    Forensic evaluation of an individual financial transaction event.
    Outputs Composite Risk Score (0-100), Risk Tier, Decision Action, and XAI Reason Codes.
    """
    try:
        flag = tx.isflaggedfraud
        if flag is None:
            flag = 1.0 if tx.amount >= 200000.0 else 0.0

        result = engine.evaluate_transaction(
            step=tx.step,
            types=tx.types,
            amount=tx.amount,
            oldbalanceorig=tx.oldbalanceorig,
            newbalanceorig=tx.newbalanceorig,
            oldbalancedest=tx.oldbalancedest,
            newbalancedest=tx.newbalancedest,
            isflaggedfraud=flag
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-predict")
def batch_predict(batch: BatchPayload):
    """
    High-throughput batch transaction auditor.
    Evaluates an array of transaction records and aggregates risk exposure metrics.
    """
    try:
        records = [tx.dict() for tx in batch.transactions]
        import pandas as pd
        df = pd.DataFrame(records)
        processed_df, summary = engine.process_batch(df)
        return {
            "summary": summary,
            "results": processed_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_model_metrics():
    """
    Returns production model benchmarks and evaluation metrics.
    """
    return {
        "model_architecture": "Random Forest Classifier (sklearn.ensemble.RandomForestClassifier)",
        "dataset": "PaySim Synthetic Financial Mobile Money Dataset",
        "benchmark_metrics": {
            "roc_auc": 0.994,
            "pr_auc": 0.882,
            "precision_fraud": 0.88,
            "recall_fraud": 0.86,
            "f1_score": 0.87
        },
        "regulatory_alignment": [
            "RBI Cyber Security Framework",
            "GDPR Article 22 Right to Explanation",
            "FCRA Adverse Action Disclosures",
            "Basel III Operational Risk Management"
        ]
    }

@app.get("/profiles")
def get_preset_profiles():
    """
    Returns pre-configured evaluation scenarios for testing.
    """
    return engine.PRESET_PROFILES
