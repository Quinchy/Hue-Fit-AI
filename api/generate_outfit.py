from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from models import ai_model, database, color_combination
import hashlib
import logging

# Initialize logger for this module
logger = logging.getLogger("outfit_api")

router = APIRouter()

# To track changes in the input request
last_request_hash = None

# Input model
class UserFeatures(BaseModel):
    height: float
    weight: float
    age: int
    skintone: str
    bodyshape: str
    category: str
    outfit_name: str

def compute_request_hash(user_features: UserFeatures):
    """Compute a hash for the input features."""
    input_string = f"{user_features.height}-{user_features.weight}-{user_features.age}-{user_features.skintone}-{user_features.bodyshape}-{user_features.category}"
    return hashlib.sha256(input_string.encode()).hexdigest()

@router.post("/generate-outfit", tags=["Outfit"])
async def generate_outfit(user_features: UserFeatures, request: Request):
    global last_request_hash
    logger.info(f"API accessed from IP: {request.client.host} at {request.client.port}")
    try:
        # Compute the hash of the current input
        current_hash = compute_request_hash(user_features)

        # Step 1: Predict outfit components
        prediction_response = ai_model.predict_outfit(user_features)
        prediction_queue = prediction_response.get("predictions", [])
        if not prediction_queue:
            raise HTTPException(status_code=404, detail="No predictions available.")

        # Always get the first prediction
        current_prediction = prediction_queue[0]

        # Convert all values in current_prediction to uppercase
        current_prediction = {
            key: (value.upper() if isinstance(value, str) else value)
            for key, value in current_prediction.items()
        }

        # Remove "No Outerwear" if present
        if current_prediction.get("outerwear") == "NO OUTERWEAR":
            current_prediction.pop("outerwear", None)

        # Step 2: Fetch products and their variants
        products_and_variants = database.get_products_with_variants(current_prediction)

        # Step 3: Select the best combination
        best_combination = color_combination.select_best_combination(products_and_variants, user_features.skintone)

        # Update the hash to track the last processed request
        last_request_hash = current_hash

        # Step 4: Return the response
        response = {
            "outfit_name": user_features.outfit_name,
            "best_combination": best_combination
        }

        logger.info(f"Successful response for request hash: {current_hash}")
        return response

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
