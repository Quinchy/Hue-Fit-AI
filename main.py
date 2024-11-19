from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.generate_outfit import router as generate_outfit_router
from api.products import router as products_router  # Import the products router

app = FastAPI()
# To run: uvicorn main:app --reload

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific allowed origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the router from generate_outfit.py
app.include_router(generate_outfit_router)
app.include_router(products_router)
