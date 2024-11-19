from math import sqrt
import random
from models.database import fetch_variant_thumbnail  # Import the function to fetch thumbnails

def color_difference(hex1, hex2):
    rgb1 = [int(hex1[i:i+2], 16) for i in (1, 3, 5)]
    rgb2 = [int(hex2[i:i+2], 16) for i in (1, 3, 5)]
    return sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def select_best_combination(products_and_variants):
    upper_colors = products_and_variants["UPPERWEAR"]["variants"]
    lower_colors = products_and_variants["LOWERWEAR"]["variants"]
    footwear_colors = products_and_variants["FOOTWEAR"]["variants"]

    good_combinations = []

    for upper in upper_colors:
        for lower in lower_colors:
            for footwear in footwear_colors:
                upper_lower_diff = color_difference(upper["hexcode"], lower["hexcode"])
                lower_footwear_diff = color_difference(lower["hexcode"], footwear["hexcode"])

                if 50 <= upper_lower_diff <= 150 and 50 <= lower_footwear_diff <= 150:
                    good_combinations.append({
                        "upper": upper,
                        "lower": lower,
                        "footwear": footwear
                    })

    if not good_combinations:
        for upper in upper_colors:
            for lower in lower_colors:
                for footwear in footwear_colors:
                    good_combinations.append({
                        "upper": upper,
                        "lower": lower,
                        "footwear": footwear
                    })

    random.shuffle(good_combinations)
    best_combination = good_combinations[0]

    # Fetch thumbnails for each category
    upper_thumbnail = fetch_variant_thumbnail(best_combination["upper"]["productVariantNo"])
    lower_thumbnail = fetch_variant_thumbnail(best_combination["lower"]["productVariantNo"])
    footwear_thumbnail = fetch_variant_thumbnail(best_combination["footwear"]["productVariantNo"])

    return {
        "upper_wear": {
            "productVariantNo": best_combination["upper"]["productVariantNo"],
            "name": f"{best_combination['upper']['colorName']} {products_and_variants['UPPERWEAR']['productName']}",
            "price": best_combination["upper"]["price"],
            "thumbnail": upper_thumbnail
        },
        "lower_wear": {
            "productVariantNo": best_combination["lower"]["productVariantNo"],
            "name": f"{best_combination['lower']['colorName']} {products_and_variants['LOWERWEAR']['productName']}",
            "price": best_combination["lower"]["price"],
            "thumbnail": lower_thumbnail
        },
        "footwear": {
            "productVariantNo": best_combination["footwear"]["productVariantNo"],
            "name": f"{best_combination['footwear']['colorName']} {products_and_variants['FOOTWEAR']['productName']}",
            "price": best_combination["footwear"]["price"],
            "thumbnail": footwear_thumbnail
        }
    }
