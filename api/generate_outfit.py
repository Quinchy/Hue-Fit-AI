# Outfit API endpoint (e.g., routes/outfit.py)
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from models import ai_model, database, color_combination
import hashlib

router = APIRouter()
last_request_hash = None

class UserFeatures(BaseModel):
    height: float
    weight: float
    age: int
    skintone: str
    bodyshape: str
    category: str
    outfit_name: str

def compute_request_hash(user_features: UserFeatures):
    input_string = f"{user_features.height}-{user_features.weight}-{user_features.age}-{user_features.skintone}-{user_features.bodyshape}-{user_features.category}"
    return hashlib.sha256(input_string.encode()).hexdigest()

@router.post("/generate-outfit", tags=["Outfit"])
async def generate_outfit(user_features: UserFeatures, request: Request):
    global last_request_hash
    try:
        current_hash = compute_request_hash(user_features)
        prediction_response = ai_model.predict_outfit(user_features)
        prediction_queue = prediction_response.get("predictions", [])
        if not prediction_queue:
            raise HTTPException(status_code=404, detail="No predictions available.")
        current_prediction = prediction_queue[0]
        current_prediction = {
            key: (value.upper() if isinstance(value, str) else value)
            for key, value in current_prediction.items()
        }
        if current_prediction.get("outerwear") == "NO OUTERWEAR":
            current_prediction.pop("outerwear", None)
        products_and_variants = database.get_products_with_variants(current_prediction)
        best_combination = color_combination.select_best_combination(products_and_variants, user_features.skintone)
        last_request_hash = current_hash
        response = {
            "outfit_name": user_features.outfit_name,
            "best_combination": best_combination
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
