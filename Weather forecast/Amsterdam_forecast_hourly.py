# amsterdam_hourly_forecast_sine.py

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import date, timedelta

# -------------------------------------------
# 1. Fetch Hourly Data
# -------------------------------------------
latitude = 52.37
longitude = 4.89
today = date.today()
start_date = "2025-01-01"
end_date = today.isoformat()

url = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={latitude}&longitude={longitude}"
    f"&start_date={start_date}&end_date={end_date}"
    "&hourly=temperature_2m,relative_humidity_2m,precipitation,cloud_cover"
    "&timezone=Europe%2FAmsterdam"
)

print(f"📡 Fetching hourly data from {start_date} to {end_date} ...")
response = requests.get(url)
data = response.json()

df = pd.DataFrame(data["hourly"])
df["time"] = pd.to_datetime(df["time"])
df = df.set_index("time").sort_index()
df.rename(columns={"temperature_2m": "temp"}, inplace=True)

print(f"✅ Data downloaded: {len(df)} hourly observations (~{len(df)/24:.1f} days)")

# -------------------------------------------
# 2. Feature Engineering
# -------------------------------------------
lags = range(1, 25)

lag_features = {
    f"temp_lag{lag}": df["temp"].shift(lag) for lag in lags
} | {
    f"humidity_lag{lag}": df["relative_humidity_2m"].shift(lag) for lag in lags
} | {
    f"cloud_lag{lag}": df["cloud_cover"].shift(lag) for lag in lags
} | {
    f"precip_lag{lag}": df["precipitation"].shift(lag) for lag in lags
}

lag_df = pd.concat(lag_features, axis=1)
df = pd.concat([df, lag_df], axis=1)

# Rolling averages
df["temp_roll6"] = df["temp"].rolling(6).mean()
df["temp_roll24"] = df["temp"].rolling(24).mean()

# Time features
df["hour"] = df.index.hour
df["dayofyear"] = df.index.dayofyear
df["month"] = df.index.month

# **Sine and Cosine encoding for hour**
df["hour_sin"] = np.sin(2 * np.pi * df.index.hour / 24)
df["hour_cos"] = np.cos(2 * np.pi * df.index.hour / 24)

df = df.dropna()

# -------------------------------------------
# 3. Train/Test Split
# -------------------------------------------
train_end = df.index[-int(len(df)*0.2)]
train = df[df.index < train_end]
test = df[df.index >= train_end]

features = [c for c in df.columns if c != "temp"]
X_train, y_train = train[features], train["temp"]
X_test, y_test = test[features], test["temp"]

print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

# -------------------------------------------
# 4. Train Model
# -------------------------------------------
model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# -------------------------------------------
# 5. Evaluate
# -------------------------------------------
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"✅ Model trained — MAE: {mae:.2f} °C | RMSE: {rmse:.2f} °C")

# -------------------------------------------
# 6. Forecast Next 24 Hours
# -------------------------------------------
last_time = df.index[-1]
forecast_start = (last_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
forecast_hours = pd.date_range(forecast_start, periods=24, freq="h")

preds = []
current_df = df.copy()

for hour in forecast_hours:
    X_latest = current_df.iloc[-1:][features]
    next_temp = model.predict(X_latest)[0]
    preds.append(next_temp)

    # Update next row with new hour and sine/cos encoding
    next_row = X_latest.copy()
    next_row.index = [hour]
    next_row["temp"] = next_temp
    next_row["hour"] = hour.hour
    next_row["hour_sin"] = np.sin(2 * np.pi * hour.hour / 24)
    next_row["hour_cos"] = np.cos(2 * np.pi * hour.hour / 24)
    next_row["dayofyear"] = hour.dayofyear
    next_row["month"] = hour.month

    current_df = pd.concat([current_df, next_row])

forecast_df = pd.DataFrame({"time": forecast_hours, "pred_temp": preds}).set_index("time")

# -------------------------------------------
# 7. Display Results
# -------------------------------------------
print("\n🌤️ Predicted hourly temperatures for tomorrow in Amsterdam:")
print(forecast_df.round(2))

plt.figure(figsize=(10,5))
plt.plot(forecast_df.index, forecast_df["pred_temp"], marker="o", color="orange")
plt.title("Amsterdam Hourly Temperature Forecast for Tomorrow (Random Forest with Hour Encoding)")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.grid(True)
plt.tight_layout()
plt.show()
