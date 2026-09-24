from pathlib import Path

import pandas as pd
import joblib

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"

DATA_FILE = DATA_DIR / "train_data.csv"
MODEL_FILE = MODEL_DIR / "delay_model.pkl"


# Create model folder automatically
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("Loading training data...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset loaded: {len(df)} rows")


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

features = [
    "current_delay",
    "trains_ahead",
    "track_congestion",
    "signal_wait_time",
    "platform_occupancy",
    "current_speed",
    "distance_to_station",
    "scheduled_travel_time",
    "time_of_day"
]

X = df[features]

y = df["additional_delay"]


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# --------------------------------------------------
# XGBOOST MODEL
# --------------------------------------------------

model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42
)


# --------------------------------------------------
# TRAIN
# --------------------------------------------------

print("\nTraining AI model...")

model.fit(X_train, y_train)

print("Training completed!")


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)

rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5

r2 = r2_score(
    y_test,
    predictions
)


print("\nModel Performance")
print("-------------------------")

print(f"MAE  : {mae:.2f} minutes")
print(f"RMSE : {rmse:.2f} minutes")
print(f"R²   : {r2:.3f}")


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

joblib.dump(
    model,
    MODEL_FILE
)

print("\nAI model saved successfully!")

print(f"Location:")
print(MODEL_FILE)