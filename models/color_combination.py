from math import sqrt
import random
from models.database import fetch_variant_thumbnail  # Import the function to fetch thumbnails

def color_difference(hex1, hex2):
    """Calculate the color difference between two hex codes."""
    rgb1 = [int(hex1[i:i+2], 16) for i in (1, 3, 5)]
    rgb2 = [int(hex2[i:i+2], 16) for i in (1, 3, 5)]
    return sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def select_best_combination(products_and_variants, user_skintone):
    """Select the best color combination for an outfit based on skin tone and color theory."""
    
    def is_skin_tone_complementary(color_hex, skintone_hex):
        """Check if the color complements the skin tone."""
        difference = color_difference(color_hex, skintone_hex)
        return 100 <= difference <= 200  # Example range for complementarity

    # Skin tone hex mapping
    skintone_hex = {
        "fair": "#FFDFC4",
        "medium": "#D4A67D",
        "olive": "#8E562E",
        "dark": "#4A2C2A"
    }.get(user_skintone.lower(), "#FFFFFF")  # Default to white if skintone is unknown

    # Ensure that we handle products_and_variants correctly
    def extract_variants(category_name):
        """Extract variants from a given category in products_and_variants."""
        if category_name in products_and_variants and products_and_variants[category_name]:
            return products_and_variants[category_name][0]["variants"]
        return []

    # Extract variants for each category
    upper_colors = extract_variants("UPPERWEAR")
    lower_colors = extract_variants("LOWERWEAR")
    footwear_colors = extract_variants("FOOTWEAR")
    outerwear_colors = extract_variants("OUTERWEAR")

    good_combinations = []

    # Iterate through all possible combinations
    for upper in upper_colors:
        for lower in lower_colors:
            for footwear in footwear_colors:
                for outerwear in outerwear_colors if outerwear_colors else [{}]:
                    upper_lower_diff = color_difference(upper["hexcode"], lower["hexcode"])
                    lower_footwear_diff = color_difference(lower["hexcode"], footwear["hexcode"])
                    complements_skintone = all([
                        is_skin_tone_complementary(upper["hexcode"], skintone_hex),
                        is_skin_tone_complementary(lower["hexcode"], skintone_hex),
                        is_skin_tone_complementary(footwear["hexcode"], skintone_hex)
                    ])

                    # If outerwear exists, include its color check
                    if outerwear and outerwear.get("hexcode"):
                        complements_skintone &= is_skin_tone_complementary(outerwear["hexcode"], skintone_hex)

                    # Select combinations that fit both skin tone and color theory
                    if 50 <= upper_lower_diff <= 150 and 50 <= lower_footwear_diff <= 150 and complements_skintone:
                        good_combinations.append({
                            "upper": upper,
                            "lower": lower,
                            "footwear": footwear,
                            "outerwear": outerwear if outerwear_colors else None
                        })

    # If no good combinations are found, fallback to any available combination
    if not good_combinations:
        for upper in upper_colors:
            for lower in lower_colors:
                for footwear in footwear_colors:
                    for outerwear in outerwear_colors if outerwear_colors else [{}]:
                        good_combinations.append({
                            "upper": upper,
                            "lower": lower,
                            "footwear": footwear,
                            "outerwear": outerwear if outerwear_colors else None
                        })

    # Randomly select a combination
    random.shuffle(good_combinations)
    best_combination = good_combinations[0]

    # Fetch thumbnails for each category
    def get_thumbnail(variant):
        return variant.get("imageUrl", None)

    # Build the response
    return {
        "upper_wear": {
            "productVariantNo": best_combination["upper"]["productVariantNo"],
            "name": f"{best_combination['upper']['colorName']} {products_and_variants['UPPERWEAR'][0]['productName']}",
            "price": best_combination["upper"]["price"],
            "thumbnail": get_thumbnail(best_combination["upper"])
        },
        "lower_wear": {
            "productVariantNo": best_combination["lower"]["productVariantNo"],
            "name": f"{best_combination['lower']['colorName']} {products_and_variants['LOWERWEAR'][0]['productName']}",
            "price": best_combination["lower"]["price"],
            "thumbnail": get_thumbnail(best_combination["lower"])
        },
        "footwear": {
            "productVariantNo": best_combination["footwear"]["productVariantNo"],
            "name": f"{best_combination['footwear']['colorName']} {products_and_variants['FOOTWEAR'][0]['productName']}",
            "price": best_combination["footwear"]["price"],
            "thumbnail": get_thumbnail(best_combination["footwear"])
        },
        "outerwear": {
            "productVariantNo": best_combination["outerwear"]["productVariantNo"] if best_combination["outerwear"] else None,
            "name": f"{best_combination['outerwear']['colorName']} {products_and_variants['OUTERWEAR'][0]['productName']}" if outerwear_colors else None,
            "price": best_combination["outerwear"]["price"] if best_combination["outerwear"] else None,
            "thumbnail": get_thumbnail(best_combination["outerwear"]) if best_combination["outerwear"] else None
        } if outerwear_colors else None
    }
