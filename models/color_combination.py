from math import sqrt
import random
import logging

logger = logging.getLogger(__name__)

def color_difference(hex1, hex2):
    rgb1 = [int(hex1[i:i+2], 16) for i in (1, 3, 5)]
    rgb2 = [int(hex2[i:i+2], 16) for i in (1, 3, 5)]
    return sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def select_best_combination(products_and_variants, user_skintone):
    def is_skin_tone_complementary(color_hex, skintone_hex):
        difference = color_difference(color_hex, skintone_hex)
        return 100 <= difference <= 200

    # Corrected skintone hex values for provided skin tones.
    skintone_hex = {
        "fair": "#FFDFC4",
        "light": "#F0D5BE",
        "medium": "#D1A17B",
        "dark": "#8E583E",
        "deep": "#4A2C2A"
    }.get(user_skintone.lower(), "#FFFFFF")

    def extract_variants(category_name):
        if category_name in products_and_variants and products_and_variants[category_name]:
            variants = []
            for product in products_and_variants[category_name]:
                for variant in product.get("variants", []):
                    if "hexcode" in variant:
                        variant["parentProductId"] = product["productId"]
                        variant["productName"] = product["productName"]
                        variants.append(variant)
            return variants
        return []

    upper_colors = extract_variants("UPPERWEAR")
    lower_colors = extract_variants("LOWERWEAR")
    footwear_colors = extract_variants("FOOTWEAR")
    outerwear_colors = extract_variants("OUTERWEAR")

    good_combinations = []
    for upper in upper_colors:
        for lower in lower_colors:
            for footwear in footwear_colors:
                for outerwear in outerwear_colors if outerwear_colors else [{}]:
                    items = [upper, lower, footwear]
                    if outerwear.get("hexcode"):
                        items.append(outerwear)
                    if not all("hexcode" in item for item in items):
                        continue
                    upper_lower_diff = color_difference(upper["hexcode"], lower["hexcode"])
                    lower_footwear_diff = color_difference(lower["hexcode"], footwear["hexcode"])
                    complements_skintone = all(is_skin_tone_complementary(item["hexcode"], skintone_hex) for item in items)

                    if 50 <= upper_lower_diff <= 150 and 50 <= lower_footwear_diff <= 150 and complements_skintone:
                        good_combinations.append({
                            "upper": upper,
                            "lower": lower,
                            "footwear": footwear,
                            "outerwear": outerwear if outerwear_colors else None
                        })

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

    random.shuffle(good_combinations)
    best_combination = good_combinations[0]

    def get_thumbnail(variant):
        return variant.get("imageUrl", None)

    result = {
        "upper_wear": {
            "productId": best_combination["upper"]["parentProductId"],
            "productVariantId": best_combination["upper"]["id"],
            "name": f"{best_combination['upper']['colorName']} {best_combination['upper']['productName']}",
            "price": best_combination["upper"]["price"],
            "thumbnail": get_thumbnail(best_combination["upper"]),
            "hexcode": best_combination["upper"]["hexcode"],
            "pngClotheURL": best_combination["upper"].get("pngClotheURL")
        },
        "lower_wear": {
            "productId": best_combination["lower"]["parentProductId"],
            "productVariantId": best_combination["lower"]["id"],
            "name": f"{best_combination['lower']['colorName']} {best_combination['lower']['productName']}",
            "price": best_combination["lower"]["price"],
            "thumbnail": get_thumbnail(best_combination["lower"]),
            "hexcode": best_combination["lower"]["hexcode"],
            "pngClotheURL": best_combination["lower"].get("pngClotheURL")
        },
        "footwear": {
            "productId": best_combination["footwear"]["parentProductId"],
            "productVariantId": best_combination["footwear"]["id"],
            "name": f"{best_combination['footwear']['colorName']} {best_combination['footwear']['productName']}",
            "price": best_combination["footwear"]["price"],
            "thumbnail": get_thumbnail(best_combination["footwear"]),
            "hexcode": best_combination["footwear"]["hexcode"],
            "pngClotheURL": best_combination["footwear"].get("pngClotheURL")
        },
        "outerwear": {
            "productId": best_combination["outerwear"]["parentProductId"] if best_combination.get("outerwear") else None,
            "productVariantId": best_combination["outerwear"]["id"] if best_combination.get("outerwear") else None,
            "name": f"{best_combination['outerwear']['colorName']} {best_combination['outerwear']['productName']}" if best_combination.get("outerwear") else None,
            "price": best_combination["outerwear"]["price"] if best_combination.get("outerwear") else None,
            "thumbnail": get_thumbnail(best_combination["outerwear"]) if best_combination.get("outerwear") else None,
            "hexcode": best_combination["outerwear"]["hexcode"] if best_combination.get("outerwear") else None,
            "pngClotheURL": best_combination["outerwear"].get("pngClotheURL") if best_combination.get("outerwear") else None,
        } if outerwear_colors else None
    }

    logger.info(f"Return: {result}")
    return result
