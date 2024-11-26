from models import load_model, load_label_encoders
import pandas as pd
import numpy as np
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

model = load_model()
label_encoders = load_label_encoders()

# Load the training data to validate predictions
training_data = pd.read_csv("data/training_data.csv")
valid_combinations = training_data[["Outerwear", "Upperwear", "Lowerwear", "Footwear", "Category"]].drop_duplicates()

# Define valid footwear for each category
valid_footwear = {
    "Casual": ["Sneakers", "Sandals"],
    "Smart Casual": ["Sneakers", "Boots"],
    "Formal": ["Oxford", "Loafers"]
}

logging.info(f"Total valid combinations: {len(valid_combinations)}")

def predict_outfit(user_features, top_n=3):
    """
    Predict multiple outfit combinations for a given user input.
    Ensures predictions strictly follow the valid combinations in the training dataset.
    """
    # Encode categorical fields
    encoded_skintone = label_encoders["skintone"].transform([user_features.skintone])[0]
    encoded_bodyshape = label_encoders["bodyshape"].transform([user_features.bodyshape])[0]

    # Handle "All Random" in category
    if user_features.category == "All Random":
        random_category = random.choice(["Smart Casual", "Casual", "Formal"])
        encoded_category = label_encoders["category"].transform([random_category])[0]
        user_category = random_category
    else:
        encoded_category = label_encoders["category"].transform([user_features.category])[0]
        user_category = user_features.category

    # Prepare the input features
    input_features = pd.DataFrame([[
        user_features.height,
        user_features.weight,
        user_features.age,
        encoded_skintone,
        encoded_bodyshape,
        encoded_category,
    ]], columns=["height", "weight", "age", "skintone", "bodyshape", "category"])

    # Generate probabilities for each target variable
    probs = {
        col: estimator.predict_proba(input_features) for col, estimator in zip(
            ["outerwear", "upperwear", "lowerwear", "footwear"], model.estimators_
        )
    }

    # Extract top N predictions for each target
    top_predictions = {
        col: np.argsort(-probs[col][0])[:top_n] for col in probs
    }

    # Generate combinations from top predictions
    outfit_combinations = []
    for outerwear in top_predictions["outerwear"]:
        for upperwear in top_predictions["upperwear"]:
            for lowerwear in top_predictions["lowerwear"]:
                for footwear in top_predictions["footwear"]:
                    decoded_combination = {
                        "outerwear": label_encoders["outerwear"].inverse_transform([outerwear])[0],
                        "upperwear": label_encoders["upperwear"].inverse_transform([upperwear])[0],
                        "lowerwear": label_encoders["lowerwear"].inverse_transform([lowerwear])[0],
                        "footwear": label_encoders["footwear"].inverse_transform([footwear])[0],
                    }
                    outfit_combinations.append(decoded_combination)

    logging.info(f"Generated combinations: {len(outfit_combinations)}")

    # Filter combinations based on valid combinations in training data
    filtered_combinations = [
        outfit for outfit in outfit_combinations
        if (
            outfit["outerwear"],
            outfit["upperwear"],
            outfit["lowerwear"],
            outfit["footwear"],
            user_category
        ) in valid_combinations.itertuples(index=False, name=None)
    ]

    # Enforce footwear validation by category
    valid_footwear = {
        "Casual": ["Sneakers", "Sandals"],
        "Smart Casual": ["Sneakers", "Boots"],
        "Formal": ["Oxford", "Loafers"]
    }
    filtered_combinations = [
        outfit for outfit in filtered_combinations
        if outfit["footwear"] in valid_footwear[user_category]
    ]

    logging.info(f"Filtered combinations: {len(filtered_combinations)}")

    # Fallback logic: Allow predictions if filtering returns no results
    if not filtered_combinations:
        logging.warning("No matching combinations found. Returning unfiltered results.")
        filtered_combinations = outfit_combinations[:top_n]

    # Randomize and return top N combinations
    random.shuffle(filtered_combinations)
    return {
        "predictions": filtered_combinations[:top_n],
    }
