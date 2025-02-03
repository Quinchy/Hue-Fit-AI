# models/database.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

# Initialize logger for this module
logger = logging.getLogger("database")

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.critical("Supabase URL or Key not found in environment variables.")
    raise RuntimeError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logger.info("Supabase client initialized successfully.")

def fetch_tag_ids(tag_name):
    """Fetch all tag IDs based on the tag name across all shops."""
    try:
        response = supabase.table("Tag").select("id").eq("name", tag_name).execute()
        tag_ids = [row["id"] for row in response.data]
        if tag_ids:
            logger.info(f"Tag IDs for '{tag_name}' fetched successfully.")
        else:
            logger.warning(f"No tag IDs found for tag '{tag_name}'.")
        return tag_ids
    except Exception as e:
        logger.error(f"Error fetching tag IDs for '{tag_name}': {e}")
        raise

def fetch_products_by_tags(tag_ids):
    """Fetch products by multiple tag IDs."""
    try:
        products = []
        for tag_id in tag_ids:
            response = supabase.table("Product").select("productNo, name, typeId, tagId").eq("tagId", tag_id).execute()
            if response.data:
                products.extend(response.data)
        if products:
            logger.info(f"Products fetched successfully for tag IDs: {tag_ids}.")
        else:
            logger.warning(f"No products found for tag IDs: {tag_ids}.")
        return products
    except Exception as e:
        logger.error(f"Error fetching products for tag IDs {tag_ids}: {e}")
        raise

def fetch_variants_and_colors(productNo):
    """Fetch product variants and their colors."""
    try:
        product_response = supabase.table("Product").select("id").eq("productNo", productNo).single().execute()
        if not product_response.data:
            logger.warning(f"No product found with productNo '{productNo}'.")
            return []
        product_id = product_response.data["id"]

        response = supabase.table("ProductVariant").select("id, productVariantNo, colorId, price").eq("productId", product_id).execute()
        if not response.data:
            logger.warning(f"No variants found for product '{productNo}'.")
            return []

        variants = []
        for variant in response.data:
            color_response = supabase.table("Color").select("name, hexcode").eq("id", variant["colorId"]).single().execute()
            if not color_response.data:
                logger.warning(f"No color found for colorId '{variant['colorId']}'.")
                continue
            color = color_response.data
            image_url = fetch_variant_thumbnail(variant["id"])
            variants.append({
                "productVariantNo": variant["productVariantNo"],
                "colorName": color["name"],
                "hexcode": color["hexcode"],
                "price": float(variant["price"]),
                "imageUrl": image_url
            })
        if variants:
            logger.info(f"Variants and colors fetched successfully for productNo: {productNo}.")
        else:
            logger.warning(f"No variants and colors found for productNo: {productNo}.")
        return variants
    except Exception as e:
        logger.error(f"Error fetching variants and colors for productNo '{productNo}': {e}")
        raise

def get_products_with_variants(predicted_outfit):
    """Get products and their variants for the predicted outfit."""
    try:
        categories = {
            "outerwear": predicted_outfit.get("outerwear"),
            "upperwear": predicted_outfit.get("upperwear"),
            "lowerwear": predicted_outfit.get("lowerwear"),
            "footwear": predicted_outfit.get("footwear"),
        }

        all_variants = {}
        for type_name, tag_name in categories.items():
            if not tag_name:
                logger.info(f"No tag provided for '{type_name}', skipping.")
                continue

            tag_ids = fetch_tag_ids(tag_name.upper())
            if not tag_ids:
                continue

            products = fetch_products_by_tags(tag_ids)
            if not products:
                continue

            variants = []
            for product in products:
                product_variants = fetch_variants_and_colors(product["productNo"])
                if product_variants:
                    variants.append({
                        "productName": product["name"],
                        "variants": product_variants
                    })
            if variants:
                all_variants[type_name.upper()] = variants
        logger.info("Products and variants fetched successfully.")
        return all_variants
    except Exception as e:
        logger.error(f"Error fetching products and variants: {e}")
        raise

def fetch_variant_thumbnail(productVariantId):
    """Fetch the first thumbnail for a product variant."""
    try:
        response = supabase.table("ProductVariantImage").select("imageURL").eq("productVariantId", productVariantId).limit(1).execute()
        if response.data:
            return response.data[0]["imageURL"]
        return None
    except Exception as e:
        logger.error(f"Error fetching thumbnail for productVariantId '{productVariantId}': {e}")
        return None
