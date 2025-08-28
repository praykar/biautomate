import logging
import os
import sys
from enum import Enum

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# --- Enums for Robustness and Clarity ---
class RecommendedAction(str, Enum):
    PROACTIVE_RETENTION = "Proactive_Retention_Offer"
    MONITOR_ACCOUNT = "Monitor_Account"
    NO_ACTION = "No_Action_Needed"

class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# --- Pydantic Models for Data Validation ---
class FeaturePayload(BaseModel):
    """The raw features the platform expects from a client application."""
    customer_id: str
    features: dict = Field(
        ...,
        example={"monthly_charges": 105.50, "tenure_months": 6, "support_tickets_last_30d": 3}
    )


class DecisionResponse(BaseModel):
    """The final, actionable response returned to the client."""
    customer_id: str
    churn_probability: float
    recommended_action: RecommendedAction
    confidence_level: ConfidenceLevel


# --- Setup Structured Logging ---
# In a real-world scenario, this would be JSON formatted for easier parsing.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Service Configuration ---
# In a real deployment, this would come from environment variables for security and flexibility.
MODEL_SERVING_URL = os.getenv("MODEL_SERVING_URL", "http://localhost:8001/predict/churn")


# --- Initialize FastAPI App ---
app = FastAPI(
    title="Decision Engine",
    description="Translates model scores into actionable business decisions.",
    version="1.0.0"
)

# --- Centralized Business Logic Configuration ---
CHURN_DECISION_THRESHOLDS = {
    "high_risk": {"threshold": 0.75, "action": RecommendedAction.PROACTIVE_RETENTION, "confidence": ConfidenceLevel.HIGH},
    "medium_risk": {"threshold": 0.50, "action": RecommendedAction.MONITOR_ACCOUNT, "confidence": ConfidenceLevel.MEDIUM},
}


# --- Simulated Model Serving Client ---
async def get_churn_prediction_from_model_server(customer_id: str, features: dict) -> float:
    """
    Simulates calling a separate, dedicated Model Serving API.
    This decouples the business logic from the ML model execution.
    """
    # In a real system, this would be an async HTTP call, e.g., using httpx
    # payload = {"customer_id": customer_id, "features": features}
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(MODEL_SERVING_URL, json=payload)
    #     response.raise_for_status()
    #     return response.json()["churn_probability"]
    logging.info(f"Simulating call to Model Serving for customer: {customer_id}")
    
    # For now, we'll use a simple heuristic for the simulation.
    # A real model server would return a score from a loaded model file.
    return features.get("support_tickets_last_30d", 0) * 0.2 + features.get("tenure_months", 12) * 0.01

# --- Business Logic for Decisions ---
def make_churn_decision(probability: float) -> tuple[RecommendedAction, ConfidenceLevel]:
    """
    Applies business rules to a churn probability score.
    Returns a tuple of (recommendation, confidence).
    """
    if probability > CHURN_DECISION_THRESHOLDS["high_risk"]["threshold"]:
        rule = CHURN_DECISION_THRESHOLDS["high_risk"]
        return (rule["action"], rule["confidence"])
    elif probability > CHURN_DECISION_THRESHOLDS["medium_risk"]["threshold"]:
        rule = CHURN_DECISION_THRESHOLDS["medium_risk"]
        return (rule["action"], rule["confidence"])
    return (RecommendedAction.NO_ACTION, ConfidenceLevel.LOW)

# --- API Endpoint ---
@app.post("/decide/churn", response_model=DecisionResponse)
async def decide(payload: FeaturePayload):
    """Accepts customer features, gets a prediction, and returns a decision."""
    try:
        # Step 1: Call the model server to get a prediction score.
        # This is the key change to align with the target architecture.
        churn_probability = await get_churn_prediction_from_model_server(
            payload.customer_id, payload.features
        )

        # Step 2: Use the score to make a business decision.
        action, confidence = make_churn_decision(churn_probability)
        
        response = DecisionResponse(
            customer_id=payload.customer_id,
            churn_probability=churn_probability,
            recommended_action=action,
            confidence_level=confidence
        )

        # This is the first step towards the feedback loop.
        # In a later phase, this would write to Kafka or a data lake.
        logging.info(f"Decision made: {response.model_dump_json()}")

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error in decision engine: {e}")