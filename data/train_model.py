import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
# To run: python data/train_model.py
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
        "Upper Wear": "upper_wear",
        "Lower Wear": "lower_wear",
        "Footwear": "footwear",
    },
    inplace=True,
)

# Encode categorical columns
label_encoders = {}
for col in ["skintone", "bodyshape", "upper_wear", "lower_wear", "footwear"]:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Save the label encoders for decoding predictions
with open("models/label_encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)

# Define input features and target labels
X = data[["height", "weight", "age", "skintone", "bodyshape"]]
y = data[["upper_wear", "lower_wear", "footwear"]]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model with MultiOutputClassifier
base_model = RandomForestClassifier(
    n_estimators=100,  # Number of trees in the forest
    max_depth=None,    # Let the tree grow until all leaves are pure or contain less than min_samples_split
    random_state=42    # Ensure reproducibility
)
model = MultiOutputClassifier(base_model)
model.fit(X_train, y_train)

# Evaluate the model (optional, for debugging purposes)
accuracy = model.score(X_test, y_test)
print(f"Model trained successfully with accuracy: {accuracy:.2f}")

# Save the trained model to a file
with open("models/outfit_model.pkl", "wb") as f:
    pickle.dump(model, f)
