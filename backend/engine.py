"""
Enterprise Fraud Detection & Decision Engine
Combines Machine Learning (Random Forest) with Rule-Based Heuristics
and Explainable AI (XAI) Adverse Action Reason Codes.
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credit_fraud.pkl")
_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        if os.path.exists(MODEL_PATH):
            _MODEL = joblib.load(MODEL_PATH)
        else:
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    return _MODEL

# Type Mapping
TRANSACTION_TYPES = {
    0: "Cash In",
    1: "Cash Out",
    2: "Debit",
    3: "Payment",
    4: "Transfer"
}

PRESET_PROFILES = {
    "1. Routine Payment (Coffee/Groceries)": {
        "step": 12,
        "types": 3,  # Payment
        "amount": 28.50,
        "oldbalanceorig": 3450.00,
        "newbalanceorig": 3421.50,
        "oldbalancedest": 125000.00,
        "newbalancedest": 125028.50,
        "isflaggedfraud": 0,
        "description": "Low-value merchant payment with intact balances."
    },
    "2. Routine Salary Deposit (Cash In)": {
        "step": 24,
        "types": 0,  # Cash In
        "amount": 4200.00,
        "oldbalanceorig": 1200.00,
        "newbalanceorig": 5400.00,
        "oldbalancedest": 850000.00,
        "newbalancedest": 845800.00,
        "isflaggedfraud": 0,
        "description": "Inflow transaction with positive balance delta."
    },
    "3. Suspicious Elevated Transfer (Review Needed)": {
        "step": 150,
        "types": 4,  # Transfer
        "amount": 18500.00,
        "oldbalanceorig": 22000.00,
        "newbalanceorig": 3500.00,
        "oldbalancedest": 0.00,
        "newbalancedest": 18500.00,
        "isflaggedfraud": 0,
        "description": "High proportion of account balance sent to newly registered destination."
    },
    "4. Account Takeover / Drain (Critical Fraud)": {
        "step": 45,
        "types": 1,  # Cash Out
        "amount": 181954.00,
        "oldbalanceorig": 181954.00,
        "newbalanceorig": 0.00,
        "oldbalancedest": 0.00,
        "newbalancedest": 0.00,
        "isflaggedfraud": 0,
        "description": "Classic ATO attack: 100% of origin funds drained; destination reflects instant withdrawal."
    },
    "5. High-Value Flagged Wire (Critical Fraud)": {
        "step": 210,
        "types": 4,  # Transfer
        "amount": 350000.00,
        "oldbalanceorig": 350000.00,
        "newbalanceorig": 0.00,
        "oldbalancedest": 0.00,
        "newbalancedest": 0.00,
        "isflaggedfraud": 1,
        "description": "Wire transfer exceeding institutional $200k threshold with total origin liquidation."
    }
}

def evaluate_transaction(step: int, types: int, amount: float,
                         oldbalanceorig: float, newbalanceorig: float,
                         oldbalancedest: float, newbalancedest: float,
                         isflaggedfraud: float) -> dict:
    """
    Evaluates a transaction using both ML probability and heuristic rule engine,
    outputting a calibrated Risk Score (0-100), Risk Tier, and XAI Reason Codes.
    """
    model = get_model()
    
    # 1. Machine Learning Inference
    features = np.array([[step, types, amount, oldbalanceorig, newbalanceorig,
                          oldbalancedest, newbalancedest, isflaggedfraud]])
    
    # Probability of class 1 (Fraud)
    probabilities = model.predict_proba(features)[0]
    ml_prob = float(probabilities[1])  # 0.0 to 1.0
    ml_risk_score = ml_prob * 100.0

    # 2. Rule-Based Heuristic Evaluation
    reasons = []
    rule_score_delta = 0.0

    # Check A: Account Liquidation (Account Takeover signature)
    if oldbalanceorig > 0 and newbalanceorig == 0 and amount >= (oldbalanceorig * 0.95):
        reasons.append({
            "code": "RC_ACC_DRAIN",
            "severity": "CRITICAL",
            "title": "Origin Account Drained (ATO Signature)",
            "detail": f"Entire liquid balance (${oldbalanceorig:,.2f}) completely depleted in a single event."
        })
        rule_score_delta += 40.0

    # Check B: Destination Ghost Balance (Mule / Cash-out anomaly)
    if types in [1, 4] and oldbalancedest == 0 and newbalancedest == 0 and amount > 5000:
        reasons.append({
            "code": "RC_GHOST_DEST",
            "severity": "HIGH",
            "title": "Destination Zero-Balance Anomaly",
            "detail": f"Transfer of ${amount:,.2f} registered at destination account with zero ending balance (instant extraction)."
        })
        rule_score_delta += 30.0

    # Check C: High-Risk Category Transfer
    if types in [1, 4] and amount > 50000:
        reasons.append({
            "code": "RC_HIGH_VALUE_CHANNEL",
            "severity": "MEDIUM",
            "title": "Elevated Volume via High-Risk Channel",
            "detail": f"${amount:,.2f} routed via {TRANSACTION_TYPES.get(types, 'Unknown')} channel."
        })
        rule_score_delta += 15.0

    # Check D: Balance Arithmetic Mismatch (Data Tampering / Forgery)
    expected_orig = oldbalanceorig - amount
    if expected_orig >= 0 and abs(expected_orig - newbalanceorig) > 5.0 and types not in [0]:
        reasons.append({
            "code": "RC_ARITH_MISMATCH",
            "severity": "HIGH",
            "title": "Ledger Balance Arithmetic Mismatch",
            "detail": f"New balance (${newbalanceorig:,.2f}) differs from expected (${expected_orig:,.2f})."
        })
        rule_score_delta += 20.0

    # Check E: Institutional High-Value Flag (> $200k)
    if isflaggedfraud == 1 or amount >= 200000:
        reasons.append({
            "code": "RC_REG_THRESHOLD",
            "severity": "HIGH",
            "title": "Institutional High-Value Threshold Exceeded",
            "detail": f"Transaction volume exceeds standard statutory monitoring threshold of $200,000."
        })
        rule_score_delta += 25.0

    # 3. Composite Risk Score Synthesis (Calibrated 0 to 100)
    # Blend ML model weight with rule adjustments
    composite_score = min(100.0, max(0.0, (ml_risk_score * 0.70) + (min(rule_score_delta, 60.0) * 0.50)))
    
    # If ML model alone is > 85%, composite risk is at least 85%
    if ml_risk_score >= 85.0:
        composite_score = max(composite_score, ml_risk_score)
    
    # If safe transaction with 0 ML risk and 0 rules, lock to low
    if ml_risk_score < 5.0 and rule_score_delta == 0:
        composite_score = min(composite_score, 12.0)

    # 4. Decision Tiers & Mitigation Action
    if composite_score < 30.0:
        risk_tier = "LOW"
        decision = "AUTO_APPROVE"
        decision_label = "Approved (Low Risk)"
        badge_color = "green"
        recommendation = "Transaction within normal behavioral parameters. Immediate clearance granted."
    elif composite_score < 70.0:
        risk_tier = "MEDIUM"
        decision = "STEP_UP_2FA"
        decision_label = "Hold: Step-Up Authentication Required"
        badge_color = "orange"
        recommendation = "Elevated risk profile detected. Trigger biometric/SMS OTP step-up verification or route to fraud analyst queue."
    else:
        risk_tier = "HIGH"
        decision = "DECLINE_AND_FREEZE"
        decision_label = "Declined: Critical Fraud Risk"
        badge_color = "red"
        recommendation = "Transaction blocked automatically. Alert AML compliance unit and temporarily restrict account egress."

    if not reasons:
        reasons.append({
            "code": "RC_NORMAL_BEHAVIOR",
            "severity": "INFO",
            "title": "Standard Transaction Pattern",
            "detail": "Account liquidity, transfer velocity, and counterparty balances align with baseline norms."
        })

    # Top feature drivers from model
    feature_names = ["Duration (Hours)", "Transfer Type", "Amount", "Origin Old Balance", 
                     "Origin New Balance", "Dest Old Balance", "Dest New Balance", "Threshold Flag"]
    feature_values = [step, types, amount, oldbalanceorig, newbalanceorig, oldbalancedest, newbalancedest, isflaggedfraud]
    importances = getattr(model, "feature_importances_", [0.1, 0.07, 0.18, 0.25, 0.03, 0.07, 0.30, 0.001])

    driver_breakdown = []
    for name, val, imp in zip(feature_names, feature_values, importances):
        driver_breakdown.append({
            "feature": name,
            "value": val,
            "importance": round(imp * 100, 2)
        })
    driver_breakdown = sorted(driver_breakdown, key=lambda x: x["importance"], reverse=True)

    return {
        "risk_score": round(composite_score, 1),
        "ml_probability": round(ml_prob * 100, 1),
        "risk_tier": risk_tier,
        "decision": decision,
        "decision_label": decision_label,
        "badge_color": badge_color,
        "recommendation": recommendation,
        "reasons": reasons,
        "feature_drivers": driver_breakdown,
        "is_fraud": 1 if composite_score >= 50.0 else 0
    }

def process_batch(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Evaluates a batch dataframe of transactions, returning enriched results
    and summary metrics (exposure saved, fraud rate, tier distribution).
    """
    required_cols = ["step", "types", "amount", "oldbalanceorig", 
                     "newbalanceorig", "oldbalancedest", "newbalancedest", "isflaggedfraud"]
    
    # Normalize column names to lowercase stripped
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Check missing columns
    for col in required_cols:
        if col not in df.columns:
            if col == "isflaggedfraud":
                df["isflaggedfraud"] = (df["amount"] >= 200000).astype(float)
            elif col == "step":
                df["step"] = 1
            else:
                raise ValueError(f"Missing required CSV column: '{col}'")

    results = []
    for _, row in df.iterrows():
        res = evaluate_transaction(
            step=int(row["step"]),
            types=int(row["types"]),
            amount=float(row["amount"]),
            oldbalanceorig=float(row["oldbalanceorig"]),
            newbalanceorig=float(row["newbalanceorig"]),
            oldbalancedest=float(row["oldbalancedest"]),
            newbalancedest=float(row["newbalancedest"]),
            isflaggedfraud=float(row["isflaggedfraud"])
        )
        results.append({
            "Risk Score": res["risk_score"],
            "Risk Tier": res["risk_tier"],
            "Decision": res["decision_label"],
            "Is Fraud": "Yes" if res["is_fraud"] == 1 else "No",
            "Primary Reason": res["reasons"][0]["title"]
        })

    result_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

    total_count = len(result_df)
    fraud_count = len(result_df[result_df["Risk Tier"] == "HIGH"])
    review_count = len(result_df[result_df["Risk Tier"] == "MEDIUM"])
    approve_count = len(result_df[result_df["Risk Tier"] == "LOW"])
    
    total_amount = float(result_df["amount"].sum())
    fraud_amount = float(result_df[result_df["Risk Tier"] == "HIGH"]["amount"].sum())

    summary = {
        "total_transactions": total_count,
        "fraud_detected": fraud_count,
        "under_review": review_count,
        "approved": approve_count,
        "fraud_rate": round((fraud_count / total_count * 100), 2) if total_count > 0 else 0,
        "total_volume": total_amount,
        "fraud_loss_prevented": fraud_amount
    }

    return result_df, summary
