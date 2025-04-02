from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_tag_ids(tag_name):
    try:
        response = supabase.table("Tag").select("id").eq("name", tag_name).execute()
        tag_ids = [row["id"] for row in response.data]
        return tag_ids
    except Exception as e:
        raise

def fetch_products_by_tags(tag_ids):
    try:
        products = []
        for tag_id in tag_ids:
            # Filter products that are not archived
            response = supabase.table("Product") \
                .select("id, name, typeId, tagId") \
                .eq("tagId", tag_id) \
                .eq("isArchived", False) \
                .execute()
            if response.data:
                products.extend(response.data)
        return products
    except Exception as e:
        raise

def fetch_variants_and_colors(product_id):
    try:
        # Include pngClotheURL in the select fields and filter non-archived variants
        response = supabase.table("ProductVariant") \
            .select("id, colorId, price, pngClotheURL") \
            .eq("productId", product_id) \
            .eq("isArchived", False) \
            .execute()
        if not response.data:
            return []
        variants = []
        for variant in response.data:
            color_response = supabase.table("Color") \
                .select("id, name, hexcode") \
                .eq("id", variant["colorId"]) \
                .single() \
                .execute()
            if not color_response.data:
                continue
            color = color_response.data
            image_url = fetch_variant_thumbnail(variant["id"])
            variants.append({
                "id": variant["id"],
                "colorName": color["name"],
                "hexcode": color["hexcode"],
                "price": float(variant["price"]),
                "imageUrl": image_url,
                "pngClotheURL": variant.get("pngClotheURL")  # New field to retrieve PNG URL
            })
        return variants
    except Exception as e:
        raise

def get_products_with_variants(predicted_outfit, recommended_color: str = None):
    """
    Retrieves products and their variants based on the predicted outfit.
    If a recommended_color is provided, it will attach a 'default_variant'
    to each product if one of its variants matches the recommended color.
    """
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
                continue
            tag_ids = fetch_tag_ids(tag_name.upper())
            if not tag_ids:
                continue
            products = fetch_products_by_tags(tag_ids)
            if not products:
                continue
            variants = []
            for product in products:
                product_variants = fetch_variants_and_colors(product["id"])
                if product_variants:
                    product_entry = {
                        "productId": product["id"],
                        "productName": product["name"],
                        "variants": product_variants
                    }
                    # If a recommended color is provided, preselect a matching variant.
                    if recommended_color:
                        for variant in product_variants:
                            if variant["colorName"].lower() == recommended_color.lower():
                                product_entry["default_variant"] = variant
                                break
                    variants.append(product_entry)
            if variants:
                all_variants[type_name.upper()] = variants
        return all_variants
    except Exception as e:
        raise

def fetch_variant_thumbnail(productVariantId):
    try:
        response = supabase.table("ProductVariantImage") \
            .select("imageURL") \
            .eq("productVariantId", productVariantId) \
            .limit(1) \
            .execute()
        if response.data:
            return response.data[0]["imageURL"]
        return None
    except Exception as e:
        return None
