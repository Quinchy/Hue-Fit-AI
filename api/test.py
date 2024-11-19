from supabase import create_client, Client
import os
from dotenv import load_dotenv
import random

load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the categories and tags
categories = {
    "UPPERWEAR": "Henley Shirt",
    "LOWERWEAR": "Trousers",
    "FOOTWEAR": "Sneakers",
}

# Fetch all type IDs for the categories
def fetch_type_ids():
    type_ids = {}
    for category in categories.keys():
        response = supabase.table("Type").select("*").eq("name", category).execute()
        if not response.data or len(response.data) == 0:
            raise RuntimeError(f"No type IDs found for category '{category}' in the database.")
        # Collect all IDs for the category
        type_ids[category] = [row["id"] for row in response.data]
    return type_ids

# Fetch products filtered by multiple type IDs and tags
def fetch_products_by_type_and_tag(type_ids):
    selected_products = []
    for category, tag in categories.items():
        ids = type_ids[category]  # List of type IDs for the category
        response = supabase.table("Products").select("productNo, name").in_("typeId", ids).eq("tags", tag).execute()
        if response.data and len(response.data) > 0:
            selected_products.append({
                "category": category,
                "productNo": response.data[0]["productNo"],
                "name": response.data[0]["name"]
            })
        else:
            raise RuntimeError(f"No products found for category '{category}' with tag '{tag}'.")
    return selected_products

# Fetch product variants and colors
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

# Apply color theory to select the best combinations
def apply_color_theory(upper_colors, lower_colors, footwear_colors):
    # Simple color theory: Choose analogous, complementary, or triadic combinations
    all_combinations = []
    for upper in upper_colors:
        for lower in lower_colors:
            for footwear in footwear_colors:
                # Add the combination to the list
                all_combinations.append({
                    "upper": upper,
                    "lower": lower,
                    "footwear": footwear
                })

    # Shuffle and select one random combination
    random.shuffle(all_combinations)
    return all_combinations[0]

# Main logic
try:
    # Step 1: Fetch type IDs
    type_ids = fetch_type_ids()
    print("Type IDs:", type_ids)

    # Step 2: Fetch selected products
    selected_products = fetch_products_by_type_and_tag(type_ids)
    print("Selected Products:", selected_products)

    # Step 3: Fetch variants and colors for each product
    all_variants = {}
    for product in selected_products:
        variants = fetch_variants_and_colors(product["productNo"])
        all_variants[product["category"]] = {
            "productName": product["name"],
            "variants": variants
        }

    print("All Variants and Colors:")
    for category, data in all_variants.items():
        print(f"Category: {category}")
        print(f"Product: {data['productName']}")
        for variant in data["variants"]:
            print(variant)

    # Step 4: Apply color theory to find the best combination
    upper_colors = all_variants["UPPERWEAR"]["variants"]
    lower_colors = all_variants["LOWERWEAR"]["variants"]
    footwear_colors = all_variants["FOOTWEAR"]["variants"]

    best_combination = apply_color_theory(upper_colors, lower_colors, footwear_colors)

    # Step 5: Prepare the final output
    final_outfit = {
        "upper_wear": {
            "productVariantNo": best_combination["upper"]["productVariantNo"],
            "name": f"{best_combination['upper']['colorName']} {all_variants['UPPERWEAR']['productName']}",
            "price": best_combination["upper"]["price"]
        },
        "lower_wear": {
            "productVariantNo": best_combination["lower"]["productVariantNo"],
            "name": f"{best_combination['lower']['colorName']} {all_variants['LOWERWEAR']['productName']}",
            "price": best_combination["lower"]["price"]
        },
        "footwear": {
            "productVariantNo": best_combination["footwear"]["productVariantNo"],
            "name": f"{best_combination['footwear']['colorName']} {all_variants['FOOTWEAR']['productName']}",
            "price": best_combination["footwear"]["price"]
        }
    }

    print("Final Outfit:")
    print(final_outfit)

except Exception as e:
    print("An error occurred:", e)
