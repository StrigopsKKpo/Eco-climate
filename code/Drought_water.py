# drought_water.py
import ee
import geemap.foliumap as geemap
import webbrowser
import os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Authenticate and initialize Earth Engine
try:
    ee.Initialize(project="ee-ferrenoe")
except ee.EEException:
    ee.Authenticate()
    ee.Initialize(project="ee-ferrenoe")

# Create base map
m = geemap.Map(center=[10, 0], zoom=2)

# 1️⃣ Surface Water Occurrence (JRC)
water_occurrence = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence')
m.addLayer(
    water_occurrence,
    {'min': 0, 'max': 100, 'palette': ['white', 'blue']},
    'Surface Water Occurrence'
)

# 2️⃣ NDVI Anomaly (MODIS)
ndvi = ee.ImageCollection('MODIS/061/MOD13A2').select('NDVI')
baseline = ndvi.filterDate('2001-01-01', '2010-12-31').mean()
recent = ndvi.filterDate('2021-01-01', '2024-12-31').mean()
ndvi_anomaly = recent.subtract(baseline)
m.addLayer(
    ndvi_anomaly,
    {'min': -1000, 'max': 1000, 'palette': ['brown', 'white', 'green']},
    'NDVI Anomaly (Recent - Baseline)'
)

# 3️⃣ Land Surface Temperature (MODIS)
lst = ee.ImageCollection('MODIS/061/MOD11A2').select('LST_Day_1km').mean().multiply(0.02).subtract(273.15)
m.addLayer(
    lst,
    {'min': 10, 'max': 45, 'palette': ['blue', 'yellow', 'red']},
    'Land Surface Temperature (°C)'
)

# 4️⃣ Evapotranspiration (MODIS/061)
et = ee.ImageCollection('MODIS/061/MOD16A2GF').select('ET').mean().multiply(0.1)
m.addLayer(
    et,
    {'min': 0, 'max': 2000, 'palette': ['white', 'lightblue', 'darkblue']},
    'Evapotranspiration (MODIS/061)'
)

# 5️⃣ Precipitation Mean (CHIRPS)
precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
    .filterDate('2020-01-01', '2024-12-31') \
    .select('precipitation').mean()
m.addLayer(
    precip,
    {'min': 0, 'max': 10, 'palette': ['white', 'lightblue', 'blue']},
    'Mean Precipitation (CHIRPS)'
)

# Export to HTML and open in browser
output_html = "maps/drought_water_map.html"
m.to_html(output_html, notebook_display=False)
print(f"✅ Map saved as {output_html}")

full_path = os.path.abspath(output_html)
webbrowser.open(f"file://{full_path}")
