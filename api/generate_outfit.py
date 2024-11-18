from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Define the schema for the request body
class UserFeatures(BaseModel):
    height: float  # in cm
    weight: float  # in kg
    age: int       # in years
    skin_tone: str
    body_shape: str

@router.post("/generate-outfit")
async def generate_outfit(user_features: UserFeatures):
    """
    Endpoint to generate an outfit based on user features.
    """
    # Logic to generate outfit
    outfit = {
        "upper_wear": "T-Shirts" if user_features.body_shape == "Athletic" else "Polo Shirt",
        "lower_wear": "Jeans" if user_features.weight < 75 else "Chinos",
        "footwear": "Sneakers" if user_features.height > 170 else "Loafers",
    }

    # Return the generated outfit and user features as a response
    return {
        "outfit": outfit,
        "user_features": user_features.dict()
    }
