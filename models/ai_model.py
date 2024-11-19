from models import load_model, load_label_encoders
import pandas as pd

model = load_model()
label_encoders = load_label_encoders()

def predict_outfit(user_features):
    input_features = pd.DataFrame([[
        user_features.height,
        user_features.weight,
        user_features.age,
        label_encoders["skintone"].transform([user_features.skin_tone])[0],
        label_encoders["bodyshape"].transform([user_features.body_shape])[0],
    ]], columns=["height", "weight", "age", "skintone", "bodyshape"])

    predictions = model.predict(input_features)
    return [
        {
            "upper_wear": label_encoders["upper_wear"].inverse_transform([pred[0]])[0],
            "lower_wear": label_encoders["lower_wear"].inverse_transform([pred[1]])[0],
            "footwear": label_encoders["footwear"].inverse_transform([pred[2]])[0],
        }
        for pred in predictions
    ]
