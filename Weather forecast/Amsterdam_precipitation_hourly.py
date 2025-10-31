# amsterdam_weather_hourly_full.py

import requests
import pandas as pd
import numpy as np
from datetime import date, timedelta
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, roc_auc_score, mean_absolute_error, mean_squared_error

# -------------------------------------------
# 1. Fetch Hourly Data
# -------------------------------------------
latitude = 52.37
longitude = 4.89
today = date.today()
start_date = "2024-01-01"
end_date = today.isoformat()

url = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={latitude}&longitude={longitude}"
    f"&start_date={start_date}&end_date={end_date}"
    "&hourly=temperature_2m,precipitation,cloudcover,relative_humidity_2m,wind_speed_10m"
    "&timezone=Europe%2FAmsterdam"
)

print(f"📡 Fetching hourly data from {start_date} to {end_date} ...")
response = requests.get(url)
data = response.json()

df = pd.DataFrame({
    "time": data["hourly"]["time"],
    "temp": data["hourly"]["temperature_2m"],
    "precip": data["hourly"]["precipitation"],
    "cloud": data["hourly"]["cloudcover"],
    "humidity": data["hourly"]["relative_humidity_2m"],
    "wind": data["hourly"]["wind_speed_10m"],
})

df["time"] = pd.to_datetime(df["time"])
df = df.set_index("time").sort_index()

print(f"✅ Data downloaded: {len(df)} hourly samples (~{len(df)/24:.1f} days)")

# -------------------------------------------
# 2. Feature Engineering
# -------------------------------------------
df["rain_flag"] = (df["precip"] > 0.05).astype(int)

# Lag features
for lag in range(1, 6):
    for col in ["precip", "rain_flag", "temp", "cloud", "humidity", "wind"]:
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

# Rolling features
df["precip_roll6"] = df["precip"].rolling(6).mean()
df["precip_roll12"] = df["precip"].rolling(12).mean()
df["wind_roll6"] = df["wind"].rolling(6).mean()
df["cloud_roll6"] = df["cloud"].rolling(6).mean()

# Time features
df["hour"] = df.index.hour
df["dayofyear"] = df.index.day_of_year

df = df.dropna()

# -------------------------------------------
# 3. Train/Test Split
# -------------------------------------------
train_end = df.index[-int(len(df) * 0.2)]
train = df[df.index < train_end]
test = df[df.index >= train_end]

features = [c for c in df.columns if c not in ["precip", "rain_flag", "wind", "cloud"]]

# Targets
y_train_cls = train["rain_flag"]
y_test_cls = test["rain_flag"]

# -------------------------------------------
# 4. Rain Probability (Classifier)
# -------------------------------------------
clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
clf.fit(train[features], y_train_cls)
y_proba_cls = clf.predict_proba(test[features])[:, 1]
print(f"🌧️ Rain classifier — AUC: {roc_auc_score(y_test_cls, y_proba_cls):.2f}")

# -------------------------------------------
# 5. Rain Amount (Regressor)
# -------------------------------------------
rainy_hours = df[df["precip"] > 0.05]
reg_rain = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
reg_rain.fit(rainy_hours[features], rainy_hours["precip"])
print("💧 Rain amount model trained.")

# -------------------------------------------
# 6. Wind Speed (Regressor)
# -------------------------------------------
reg_wind = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
reg_wind.fit(train[features], train["wind"])
print("🌬️ Wind speed model trained.")

# -------------------------------------------
# 7. Cloud Cover (Regressor)
# -------------------------------------------
reg_cloud = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
reg_cloud.fit(train[features], train["cloud"])
print("☁️ Cloud cover model trained.")

# -------------------------------------------
# 8. Forecast Tomorrow Hourly
# -------------------------------------------
tomorrow_start = (df.index[-1] + timedelta(hours=1)).replace(hour=0, minute=0)
forecast_hours = pd.date_range(tomorrow_start, periods=24, freq="h")

last_known = df.iloc[-1:].copy()
forecast_rows = []

for hour in forecast_hours:
    X_latest = last_known[features].copy()
    X_latest["hour"] = hour.hour
    X_latest["dayofyear"] = hour.day_of_year

    rain_prob = clf.predict_proba(X_latest)[0, 1] * 100
    rain_mm = reg_rain.predict(X_latest)[0] * (rain_prob / 100)
    wind_speed = reg_wind.predict(X_latest)[0]
    cloud_cover = np.clip(reg_cloud.predict(X_latest)[0], 0, 100)

    forecast_rows.append({
        "time": hour,
        "rain_prob_%": rain_prob,
        "rain_mm": rain_mm,
        "wind_speed_mps": wind_speed,
        "cloud_cover_%": cloud_cover
    })

forecast_df = pd.DataFrame(forecast_rows).set_index("time")

# -------------------------------------------
# 9. Display Results
# -------------------------------------------
print("\n📅 Hourly Forecast for Tomorrow:")
print(forecast_df.round(2))

print("\n🌦️ Summary:")
print(f"Average rain probability: {forecast_df['rain_prob_%'].mean():.1f}%")
print(f"Expected total rainfall: {forecast_df['rain_mm'].sum():.2f} mm")
print(f"Average wind speed: {forecast_df['wind_speed_mps'].mean():.1f} m/s")
print(f"Average cloud cover: {forecast_df['cloud_cover_%'].mean():.1f}%")
