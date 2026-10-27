import os
import streamlit as st
import numpy as np
import joblib
import requests as re

st.set_page_config(
    page_title="Credit Card Fraud Detection",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Credit Card Fraud Detection Web App")

if os.path.exists("image.png"):
    st.image("image.png")

st.write("""
## About
Credit card fraud is an inclusive term for fraud committed using a payment card, such as a credit card or debit card.
This application utilizes a trained Machine Learning model to detect whether a financial transaction is fraudulent or legitimate based on key transaction parameters.
""")

@st.cache_resource
def get_model():
    model_path = os.path.join(os.path.dirname(__file__), "credit_fraud.pkl")
    return joblib.load(model_path)

st.sidebar.header("Input Features of The Transaction")

sender_name = st.sidebar.text_input("Sender ID / Name", value="Customer_A")
receiver_name = st.sidebar.text_input("Receiver ID / Name", value="Merchant_B")
step = st.sidebar.slider("Transaction Duration (Hours):", min_value=0, max_value=744, value=1)

types_dict = {
    0: "Cash In",
    1: "Cash Out",
    2: "Debit",
    3: "Payment",
    4: "Transfer"
}

types = st.sidebar.selectbox(
    "Type of Transfer Made:",
    options=list(types_dict.keys()),
    format_func=lambda val: f"{val} - {types_dict[val]}"
)
x = types_dict[types]

amount = st.sidebar.number_input("Amount in $", min_value=0.0, max_value=1000000.0, value=9839.64, step=100.0)
oldbalanceorg = st.sidebar.number_input("Sender Balance Before Transaction", min_value=0.0, max_value=10000000.0, value=170136.0, step=500.0)
newbalanceorg = st.sidebar.number_input("Sender Balance After Transaction", min_value=0.0, max_value=10000000.0, value=160296.36, step=500.0)
oldbalancedest = st.sidebar.number_input("Recipient Balance Before Transaction", min_value=0.0, max_value=10000000.0, value=0.0, step=500.0)
newbalancedest = st.sidebar.number_input("Recipient Balance After Transaction", min_value=0.0, max_value=10000000.0, value=0.0, step=500.0)

isflaggedfraud = 1 if amount >= 200000 else 0

st.subheader("Transaction Summary")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Sender ID:** {sender_name}")
    st.write(f"**Receiver ID:** {receiver_name}")
    st.write(f"**Transaction Type:** {x}")
    st.write(f"**Amount Sent:** ${amount:,.2f}")
with col2:
    st.write(f"**Sender Balance Before:** ${oldbalanceorg:,.2f}")
    st.write(f"**Sender Balance After:** ${newbalanceorg:,.2f}")
    st.write(f"**Recipient Balance Before:** ${oldbalancedest:,.2f}")
    st.write(f"**Recipient Balance After:** ${newbalancedest:,.2f}")
    st.write(f"**System High-Value Flag (> $200k):** {'Yes' if isflaggedfraud == 1 else 'No'}")

if st.button("Run Fraud Detection", type="primary"):
    values = {
        "step": int(step),
        "types": int(types),
        "amount": float(amount),
        "oldbalanceorig": float(oldbalanceorg),
        "newbalanceorig": float(newbalanceorg),
        "oldbalancedest": float(oldbalancedest),
        "newbalancedest": float(newbalancedest),
        "isflaggedfraud": float(isflaggedfraud)
    }

    prediction = None
    engine = ""

    # Attempt 1: Call API if running (Microservice Mode)
    api_url = os.environ.get("API_URL", "http://127.0.0.1:8000/predict")
    try:
        res = re.post(api_url, json=values, timeout=1.5)
        if res.status_code == 200:
            resp = res.json()
            prediction = resp[0] if isinstance(resp, list) else str(resp)
            engine = "FastAPI Backend Service"
    except Exception:
        pass

    # Attempt 2: Embedded Direct Model Inference (Cloud Standalone Mode)
    if prediction is None:
        try:
            model = get_model()
            features = np.array([[values["step"], values["types"], values["amount"], 
                                  values["oldbalanceorig"], values["newbalanceorig"], 
                                  values["oldbalancedest"], values["newbalancedest"], 
                                  values["isflaggedfraud"]]])
            pred = model.predict(features)
            prediction = "fraudulent" if pred[0] == 1 else "not fraudulent"
            engine = "Embedded Random Forest Engine"
        except Exception as e:
            st.error(f"Inference error: {e}")

    if prediction:
        st.divider()
        if not sender_name or not receiver_name:
            st.warning("Please provide valid Sender and Receiver IDs.")
        elif prediction.lower() == "fraudulent":
            st.error(f"### 🚨 ALERT: Fraudulent Transaction Detected!\nThe '{x}' transaction of **${amount:,.2f}** from **{sender_name}** to **{receiver_name}** was flagged as **FRAUDULENT**.")
        else:
            st.success(f"### ✅ Transaction Verified: Legitimate\nThe '{x}' transaction of **${amount:,.2f}** from **{sender_name}** to **{receiver_name}** is **NOT FRAUDULENT**.")
        st.caption(f"Inference Engine: {engine}")
