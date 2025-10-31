# amsterdam_weather_daily_full.py

import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, roc_auc_score, mean_absolute_error, mean_squared_error
from datetime import date, timedelta

# -------------------------------------------
# 1. Fetch Daily Weather Data
# -------------------------------------------
latitude = 52.37
longitude = 4.89
today = date.today()
start_date = "2020-01-01"
end_date = today.isoformat()

url = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={latitude}&longitude={longitude}"
    f"&start_date={start_date}&end_date={end_date}"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
    "rain_sum,cloudcover_mean,relative_humidity_2m_mean,windspeed_10m_max"
    "&timezone=Europe%2FAmsterdam"
)

print(f"📡 Fetching daily weather data from {start_date} to {end_date} ...")
response = requests.get(url)
data = response.json()

df = pd.DataFrame({
    "date": data["daily"]["time"],
    "temp_max": data["daily"]["temperature_2m_max"],
    "temp_min": data["daily"]["temperature_2m_min"],
    "precip_sum": data["daily"]["precipitation_sum"],
    "rain_sum": data["daily"]["rain_sum"],
    "cloudcover": data["daily"]["cloudcover_mean"],
    "humidity": data["daily"]["relative_humidity_2m_mean"],
    "wind_max": data["daily"]["windspeed_10m_max"],
})

df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()

print(f"✅ Data downloaded: {len(df)} days")
print(df.head())

# -------------------------------------------
# 2. Feature Engineering
# -------------------------------------------
# Binary target: did it rain or not?
df["rain_flag"] = (df["precip_sum"] > 0.1).astype(int)

# Lag features (last few days)
for lag in range(1, 8):
    for col in ["precip_sum", "rain_flag", "temp_max", "temp_min", "cloudcover", "humidity", "wind_max"]:
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

# Rolling features
df["precip_roll3"] = df["precip_sum"].rolling(3).mean()
df["precip_roll7"] = df["precip_sum"].rolling(7).mean()
df["temp_mean"] = (df["temp_max"] + df["temp_min"]) / 2
df["temp_roll7"] = df["temp_mean"].rolling(7).mean()
df["wind_roll3"] = df["wind_max"].rolling(3).mean()
df["cloud_roll3"] = df["cloudcover"].rolling(3).mean()

# Time-based features
df["month"] = df.index.month
df["dayofyear"] = df.index.day_of_year

df = df.dropna()

# -------------------------------------------
# 3. Train/Test Split
# -------------------------------------------
train_end = df.index[-int(len(df)*0.2)]
train = df[df.index < train_end]
test = df[df.index >= train_end]

feature_cols = [c for c in df.columns if c not in [
    "precip_sum", "rain_sum", "rain_flag", "cloudcover", "wind_max"
]]

# -------------------------------------------
# 4. Model 1: Rain Probability (Classifier)
# -------------------------------------------
clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
clf.fit(train[feature_cols], train["rain_flag"])

y_pred_cls = clf.predict(test[feature_cols])
y_proba_cls = clf.predict_proba(test[feature_cols])[:, 1]

acc = accuracy_score(test["rain_flag"], y_pred_cls)
auc = roc_auc_score(test["rain_flag"], y_proba_cls)
print(f"🌧️ Rain classifier — Accuracy: {acc:.2f}, AUC: {auc:.2f}")

# -------------------------------------------
# 5. Model 2: Rain Amount (Regressor)
# -------------------------------------------
rainy_days = df[df["precip_sum"] > 0.1]
reg_rain = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
reg_rain.fit(rainy_days[feature_cols], rainy_days["precip_sum"])

rainy_test = test[test["precip_sum"] > 0.1]
if len(rainy_test) > 0:
    y_pred_reg = reg_rain.predict(rainy_test[feature_cols])
    mae = mean_absolute_error(rainy_test["precip_sum"], y_pred_reg)
    rmse = np.sqrt(mean_squared_error(rainy_test["precip_sum"], y_pred_reg))
    print(f"💧 Rain amount model — MAE: {mae:.2f} mm, RMSE: {rmse:.2f} mm")

# -------------------------------------------
# 6. Model 3: Wind Speed (Regressor)
# -------------------------------------------
reg_wind = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
reg_wind.fit(train[feature_cols], train["wind_max"])
print("🌬️ Wind speed model trained.")

# -------------------------------------------
# 7. Model 4: Cloud Cover (Regressor)
# -------------------------------------------
reg_cloud = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
reg_cloud.fit(train[feature_cols], train["cloudcover"])
print("☁️ Cloud cover model trained.")

# -------------------------------------------
# 8. Predict Tomorrow
# -------------------------------------------
tomorrow = df.index[-1] + timedelta(days=1)
X_latest = df.iloc[-1:][feature_cols]

rain_chance = clf.predict_proba(X_latest)[0, 1] * 100
rain_mm_raw = reg_rain.predict(X_latest)[0]
rain_mm = rain_mm_raw * (rain_chance / 100)  # expected value
wind_pred = reg_wind.predict(X_latest)[0]
cloud_pred = np.clip(reg_cloud.predict(X_latest)[0], 0, 100)

# -------------------------------------------
# 9. Print Forecast
# -------------------------------------------
print(f"\n📅 Forecast for {tomorrow.date()}")
print(f"🌧️ Chance of rain: {rain_chance:.1f}%")
print(f"💦 Expected total precipitation: {rain_mm:.2f} mm (raw model {rain_mm_raw:.2f} mm)")
print(f"🌬️ Predicted max wind speed: {wind_pred:.1f} m/s")
print(f"☁️ Predicted average cloud cover: {cloud_pred:.1f}%")

# -------------------------------------------
# 10. Last week + tomorrow
# -------------------------------------------
print("\nRecent daily summary:")
print(df[["temp_max", "temp_min", "precip_sum", "cloudcover", "wind_max"]].tail(7))
