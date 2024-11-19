import pickle

# Load AI model
def load_model():
    with open("models/outfit_model.pkl", "rb") as f:
        return pickle.load(f)

# Load label encoders
def load_label_encoders():
    with open("models/label_encoders.pkl", "rb") as f:
        return pickle.load(f)
