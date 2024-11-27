import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import pickle

# Load the dataset
data = pd.read_csv("data/training_data.csv")

# Rename columns for consistent usage
data.rename(
    columns={
        "Height": "height",
        "Weight": "weight",
        "Age": "age",
        "Skin Tone": "skintone",
        "Body Shape": "bodyshape",
        "Category": "category",
        "Outerwear": "outerwear",
        "Upperwear": "upperwear",
        "Lowerwear": "lowerwear",
        "Footwear": "footwear",
    },
    inplace=True,
)

# Fill 'None' values in outerwear with a placeholder (e.g., "No Outerwear")
data["outerwear"] = data["outerwear"].fillna("No Outerwear")

# Define valid combinations explicitly
valid_combinations = {
    "Casual": {
        "outerwear": ["No Outerwear"],
        "upperwear": ["T-Shirts", "Henley Shirt"],
        "lowerwear": ["Jeans", "Shorts"],
        "footwear": ["Sneakers", "Sandals"]
    },
    "Smart Casual": {
        "outerwear": ["No Outerwear"],
        "upperwear": ["Polo Shirt", "Short Sleeves"],
        "lowerwear": ["Chinos", "Trousers", "Jeans"],
        "footwear": ["Sneakers", "Boots"]
    },
    "Formal": {
        "outerwear": ["Blazer", "Coats"],
        "upperwear": ["Long Sleeves", "Turtle Neck Long Sleeves"],
        "lowerwear": ["Slacks"],
        "footwear": ["Oxford", "Loafers"]
    }
}

# Filter data to include only valid combinations
filtered_data = []
for _, row in data.iterrows():
    category = row["category"]
    if (
        row["outerwear"] in valid_combinations[category]["outerwear"]
        and row["upperwear"] in valid_combinations[category]["upperwear"]
        and row["lowerwear"] in valid_combinations[category]["lowerwear"]
        and row["footwear"] in valid_combinations[category]["footwear"]
    ):
        filtered_data.append(row)

data = pd.DataFrame(filtered_data)

# Encode categorical columns
label_encoders = {}
for col in ["skintone", "bodyshape", "category", "outerwear", "upperwear", "lowerwear", "footwear"]:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Save the label encoders for decoding predictions
with open("models/label_encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)

# Define input features and target labels
X = data[["height", "weight", "age", "skintone", "bodyshape", "category"]]
y = data[["outerwear", "upperwear", "lowerwear", "footwear"]]

# Verify label consistency
for col in y.columns:
    assert len(label_encoders[col].classes_) == y[col].nunique(), f"Mismatch in labels for {col}"

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model with MultiOutputClassifier
base_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    n_jobs=-1,
    random_state=42
)
model = MultiOutputClassifier(base_model)
model.fit(X_train, y_train)

# Evaluate the model
accuracy = model.score(X_test, y_test)
scores = cross_val_score(model, X, y, cv=5)
print(f"Cross-validated accuracy: {scores.mean():.2f}")
print(f"Model trained successfully with accuracy: {accuracy:.2f}")

# Save the trained model to a file
with open("models/outfit_model.pkl", "wb") as f:
    pickle.dump(model, f)
