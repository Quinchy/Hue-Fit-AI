import os
import psutil
import logging
import hashlib
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from models import ai_model, database, color_combination

logger = logging.getLogger(__name__)
router = APIRouter()
last_request_hash = None

def log_memory_usage(stage: str):
    process = psutil.Process(os.getpid())
    mem_used = process.memory_info().rss  # in bytes
    mem_mb = mem_used / (1024 * 1024)
    logger.info(f"[MEMORY] {stage}: {mem_mb:.2f} MB used")

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
        log_memory_usage("Start generate_outfit")
        current_hash = compute_request_hash(user_features)
        log_memory_usage("After computing request hash")
        
        # Get predictions from the AI model
        prediction_response = ai_model.predict_outfit(user_features)
        log_memory_usage("After AI model prediction")
        
        prediction_queue = prediction_response.get("predictions", [])
        if not prediction_queue:
            raise HTTPException(status_code=404, detail="No predictions available.")
        
        current_prediction = prediction_queue[0]
        # Convert string values to uppercase
        current_prediction = {
            key: (value.upper() if isinstance(value, str) else value)
            for key, value in current_prediction.items()
        }
        if current_prediction.get("outerwear") == "NO OUTERWEAR":
            current_prediction.pop("outerwear", None)
        
        log_memory_usage("Before fetching products with variants")
        products_and_variants = database.get_products_with_variants(current_prediction)
        log_memory_usage("After fetching products with variants")
        
        best_combination = color_combination.select_best_combination(products_and_variants, user_features.skintone)
        log_memory_usage("After selecting best combination")
        
        last_request_hash = current_hash
        response = {
            "outfit_name": user_features.outfit_name,
            "best_combination": best_combination
        }
        log_memory_usage("Before returning response")
        return response
    except Exception as e:
        logger.error("Error in generate_outfit: %s", e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
