# amsterdam_tomorrow_forecast_minmax.py

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import date

# -------------------------------------------
# 1. Fetch Historical Data (up to today)
# -------------------------------------------

latitude = 52.37
longitude = 4.89
today = date.today()
start_date = "2015-01-01"
end_date = today.isoformat()

url = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={latitude}&longitude={longitude}"
    f"&start_date={start_date}&end_date={end_date}"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    "&timezone=Europe%2FAmsterdam"
)

print(f"📡 Fetching data from {start_date} to {end_date} ...")
response = requests.get(url)
data = response.json()

df = pd.DataFrame({
    "date": data["daily"]["time"],
    "temp_max": data["daily"]["temperature_2m_max"],
    "temp_min": data["daily"]["temperature_2m_min"],
    "precipitation": data["daily"]["precipitation_sum"]
})

df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()

print(f"✅ Data downloaded successfully: {len(df)} days")
print(df.tail())

# -------------------------------------------
# 2. Feature Engineering
# -------------------------------------------

for lag in range(1, 8):
    df[f"temp_max_lag{lag}"] = df["temp_max"].shift(lag)
    df[f"temp_min_lag{lag}"] = df["temp_min"].shift(lag)
    df[f"precip_lag{lag}"] = df["precipitation"].shift(lag)

df["temp_max_rolling7"] = df["temp_max"].rolling(window=7).mean()
df["temp_min_rolling7"] = df["temp_min"].rolling(window=7).mean()
df["dayofyear"] = df.index.dayofyear
df["month"] = df.index.month
df = df.dropna()

# -------------------------------------------
# 3. Train/Test Split (80/20 time-based)
# -------------------------------------------

train_end = df.index[-int(len(df)*0.2)]
train = df[df.index < train_end]
test = df[df.index >= train_end]

# Common features for both models
feature_cols = [c for c in df.columns if c not in ["temp_max", "temp_min"]]
X_train = train[feature_cols]
X_test = test[feature_cols]

# -------------------------------------------
# 4. Train Random Forest Models (Max & Min)
# -------------------------------------------

def train_and_evaluate(y_train, y_test, label):
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"✅ {label} model trained — MAE: {mae:.2f} °C | RMSE: {rmse:.2f} °C")
    return model, preds

model_max, y_pred_max = train_and_evaluate(train["temp_max"], test["temp_max"], "Max temp")
model_min, y_pred_min = train_and_evaluate(train["temp_min"], test["temp_min"], "Min temp")

# -------------------------------------------
# 5. Predict Tomorrow’s Max & Min Temperatures
# -------------------------------------------

latest_row = df.iloc[-1:].copy()
X_latest = latest_row[feature_cols]
next_day_max = model_max.predict(X_latest)[0]
next_day_min = model_min.predict(X_latest)[0]

tomorrow = df.index[-1] + pd.Timedelta(days=1)

print(f"\n🌤️ Predicted temperatures for {tomorrow.date()} in Amsterdam:")
print(f"   Max: {next_day_max:.2f} °C")
print(f"   Min: {next_day_min:.2f} °C")

# -------------------------------------------
# 6. Optional: Plot Actual vs Predicted (Last 100 Days)
# -------------------------------------------

plt.figure(figsize=(10,5))
plt.plot(test.index[-100:], test["temp_max"][-100:], label="Actual Max", color="red")
plt.plot(test.index[-100:], y_pred_max[-100:], label="Predicted Max", color="orange", alpha=0.7)
plt.plot(test.index[-100:], test["temp_min"][-100:], label="Actual Min", color="blue")
plt.plot(test.index[-100:], y_pred_min[-100:], label="Predicted Min", color="cyan", alpha=0.7)
plt.title("Amsterdam Daily Max & Min Temperature Predictions (Random Forest)")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.tight_layout()
plt.show()
