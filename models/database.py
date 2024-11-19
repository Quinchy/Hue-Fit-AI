from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_type_ids(categories):
    type_ids = {}
    for category in categories.keys():
        response = supabase.table("Type").select("*").eq("name", category).execute()
        if not response.data or len(response.data) == 0:
            raise RuntimeError(f"No type IDs found for category '{category}' in the database.")
        type_ids[category] = [row["id"] for row in response.data]
    return type_ids

def fetch_products_by_type_and_tag(type_ids, categories):
    selected_products = {}
    for category, tag in categories.items():
        ids = type_ids[category]
        response = supabase.table("Products").select("productNo, name").in_("typeId", ids).eq("tags", tag).execute()
        if response.data and len(response.data) > 0:
            selected_products[category] = {
                "productNo": response.data[0]["productNo"],
                "name": response.data[0]["name"],
            }
        else:
            raise RuntimeError(f"No products found for category '{category}' with tag '{tag}'.")
    return selected_products

def fetch_variants_and_colors(productNo):
    response = supabase.table("ProductVariants").select("productVariantNo, colorId, price").eq("productNo", productNo).execute()
    if not response.data or len(response.data) == 0:
        raise RuntimeError(f"No variants found for product '{productNo}'.")

    variants = []
    for variant in response.data:
        color_response = supabase.table("Colors").select("name, hexcode").eq("id", variant["colorId"]).execute()
        if not color_response.data or len(color_response.data) == 0:
            raise RuntimeError(f"No color found for colorId '{variant['colorId']}'.")
        color = color_response.data[0]
        variants.append({
            "productVariantNo": variant["productVariantNo"],
            "colorName": color["name"],
            "hexcode": color["hexcode"],
            "price": variant["price"]
        })
    return variants

def get_products_with_variants(predicted_outfit):
    categories = {
        "UPPERWEAR": predicted_outfit[0]["upper_wear"],
        "LOWERWEAR": predicted_outfit[0]["lower_wear"],
        "FOOTWEAR": predicted_outfit[0]["footwear"],
    }
    type_ids = fetch_type_ids(categories)
    products = fetch_products_by_type_and_tag(type_ids, categories)

    all_variants = {}
    for category, product in products.items():
        variants = fetch_variants_and_colors(product["productNo"])
        all_variants[category] = {
            "productName": product["name"],
            "variants": variants
        }
    return all_variants

def fetch_variant_thumbnail(productVariantNo):
    response = supabase.table("ProductVariantImages").select("imageUrl").eq("productVariantNo", productVariantNo).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["imageUrl"]  # Return the first image URL
    return None  # Return None if no image is found