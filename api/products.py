from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

@router.get("/products", tags=["Products"])
async def get_all_products():
    try:
        # Query the 'Products' table
        response = supabase.table('Products').select('*').execute()

        # Handle response properly
        if response.data is None:
            raise HTTPException(
                status_code=500,
                detail="Supabase error: No data returned from the database."
            )
        return {"products": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
