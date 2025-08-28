import os

import requests
import streamlit as st

# --- Configuration ---
st.set_page_config(
    page_title="Churn Decision Platform",
    page_icon="🤖",
    layout="centered"
)

# This should point to your running FastAPI application
# Use an environment variable for the API URL in production
API_URL = os.getenv("API_URL", "http://localhost:8000/decide/churn")

# --- UI Components ---
st.title("🤖 Customer Churn Decision Platform")
st.markdown(
    """
    This UI demonstrates the **Automated Decision Engine**. 
    Adjust the customer features below and click 'Get Decision' to see the recommended action.
    """
)

st.header("Customer Features")

# Create a form for a cleaner UI
with st.form("customer_features_form"):
    customer_id = st.text_input("Customer ID", value="cust_12345")
    
    col1, col2 = st.columns(2)
    with col1:
        monthly_charges = st.slider("Monthly Charges ($)", min_value=10.0, max_value=200.0, value=105.50, step=0.5)
        tenure_months = st.slider("Tenure (Months)", min_value=1, max_value=72, value=6)
    with col2:
        support_tickets = st.slider("Support Tickets (Last 30 Days)", min_value=0, max_value=10, value=3)
        failed_payments = st.slider("Failed Payments (Last 90 Days)", min_value=0, max_value=5, value=1)

    # The submit button for the form
    submitted = st.form_submit_button("Get Decision")


# --- API Call and Response Handling ---
if submitted:
    # Construct the payload based on the FeaturePayload model in the API
    payload = {
        "customer_id": customer_id,
        "features": {
            "monthly_charges": monthly_charges,
            "tenure_months": tenure_months,
            "support_tickets_last_30d": support_tickets,
            "failed_payments_last_90d": failed_payments
        }
    }

    st.subheader("API Request Payload")
    st.json(payload)

    try:
        with st.spinner("Calling Decision Engine..."):
            response = requests.post(API_URL, json=payload, timeout=5)
            response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
            
            data = response.json()

            st.subheader("API Response")
            st.json(data)

            # Display the results in a more user-friendly way
            st.subheader("Result")
            action = data.get("recommended_action", "N/A")
            probability = data.get("churn_probability", 0)
            confidence = data.get("confidence_level", "N/A")

            if "Proactive_Retention" in action:
                st.error(f"**Action:** {action.replace('_', ' ')}", icon="🚨")
            elif "Monitor_Account" in action:
                st.warning(f"**Action:** {action.replace('_', ' ')}", icon="⚠️")
            else:
                st.success(f"**Action:** {action.replace('_', ' ')}", icon="✅")

            st.metric(label="Predicted Churn Probability", value=f"{probability:.2%}")

    except requests.exceptions.RequestException as e:
        st.error(f"API Call Failed: {e}", icon="🔥")
        st.info("Please ensure the FastAPI server is running. You can start it with: `uvicorn main:app --host 0.0.0.0 --port 8000`")