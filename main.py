from fastapi import FastAPI
from api.generate_outfit import router as generate_outfit_router

app = FastAPI()
# To run: uvicorn main:app --reload
# Include the router from generate_outfit.py
app.include_router(generate_outfit_router)
