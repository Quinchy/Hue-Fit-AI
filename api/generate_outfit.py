from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
from models import ai_model, database, color_combination

router = APIRouter()

# Input model
class UserFeatures(BaseModel):
    height: float
    weight: float
    skin_tone: str = Field(alias="skintone")
    body_shape: str = Field(alias="bodyshape")
    age: int
    outfit_name: Optional[str] = None  # Include outfit name as optional

@router.post("/generate-outfit", tags=["Outfit"])
async def generate_outfit(request: Request, user_features: UserFeatures):
    try:
        # Step 1: Predict outfit components
        predicted_outfit = ai_model.predict_outfit(user_features)

        # Step 2: Fetch products and their variants
        products_and_variants = database.get_products_with_variants(predicted_outfit)

        # Step 3: Select the best combination using color logic
        final_outfit = color_combination.select_best_combination(products_and_variants)

        # Include the outfit name (if provided) in the response
        response = {
            "outfit": final_outfit,
            "outfit_name": user_features.outfit_name  # Add outfit_name to the response
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
