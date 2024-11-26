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

def fetch_tag_ids(tag_name):
    """Fetch all tag IDs based on the tag name across all shops."""
    response = supabase.table("Tags").select("id").eq("name", tag_name).execute()
    if not response.data or len(response.data) == 0:
        raise RuntimeError(f"No tag IDs found for tag name '{tag_name}'.")
    return [row["id"] for row in response.data]

def fetch_products_by_tags(tag_ids):
    """Fetch products by multiple tag IDs."""
    products = []
    for tag_id in tag_ids:
        response = supabase.table("Products").select("productNo, name, typeId, tagId").eq("tagId", tag_id).execute()
        if response.data:
            products.extend(response.data)  # Add all matching products for the current tagId

    if not products:
        raise RuntimeError(f"No products found for tag IDs '{tag_ids}'.")
    return products

def fetch_variants_and_colors(productNo):
    """Fetch product variants and their colors."""
    response = supabase.table("ProductVariants").select("productVariantNo, colorId, price").eq("productNo", productNo).execute()
    if not response.data or len(response.data) == 0:
        raise RuntimeError(f"No variants found for product '{productNo}'.")

    variants = []
    for variant in response.data:
        color_response = supabase.table("Colors").select("name, hexcode").eq("id", variant["colorId"]).execute()
        if not color_response.data or len(color_response.data) == 0:
            raise RuntimeError(f"No color found for colorId '{variant['colorId']}'.")
        color = color_response.data[0]

        # Fetch the first image URL for the variant
        image_url = fetch_variant_thumbnail(variant["productVariantNo"])

        variants.append({
            "productVariantNo": variant["productVariantNo"],
            "colorName": color["name"],
            "hexcode": color["hexcode"],
            "price": variant["price"],
            "imageUrl": image_url  # Include the image URL in the response
        })
    return variants

def get_products_with_variants(predicted_outfit):
    """Get products and their variants for the predicted outfit."""
    try:
        # Extract type names and their corresponding tags from the predicted outfit
        categories = {
            "outerwear": predicted_outfit.get("outerwear"),
            "upperwear": predicted_outfit.get("upperwear"),
            "lowerwear": predicted_outfit.get("lowerwear"),
            "footwear": predicted_outfit.get("footwear"),
        }

        all_products = {}
        for type_name, tag_name in categories.items():
            if not tag_name:  # Skip if no tag is provided
                continue

            # Fetch all tag IDs for the given tag name
            tag_ids = fetch_tag_ids(tag_name.upper())
            # Fetch all products matching any of the tag IDs
            products = fetch_products_by_tags(tag_ids)

            # Add products if any exist
            if products:
                all_products[type_name.upper()] = [
                    {
                        "productNo": product["productNo"],
                        "name": product["name"],
                    }
                    for product in products
                ]

        # Fetch variants for each product
        all_variants = {}
        for category, products in all_products.items():
            variants = []
            for product in products:
                product_variants = fetch_variants_and_colors(product["productNo"])
                variants.append({
                    "productName": product["name"],
                    "variants": product_variants
                })
            all_variants[category] = variants

        return all_variants

    except Exception as e:
        raise RuntimeError(f"An error occurred while fetching products and variants: {str(e)}")

def fetch_variant_thumbnail(productVariantNo):
    """Fetch the first thumbnail for a product variant."""
    response = supabase.table("ProductVariantImages").select("imageUrl").eq("productVariantNo", productVariantNo).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["imageUrl"]  # Return the first image URL
    return None  # Return None if no image is found
