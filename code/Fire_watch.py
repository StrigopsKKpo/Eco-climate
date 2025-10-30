# fire_watch_simple.py
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

# Create map
m = geemap.Map(center=[0, 0], zoom=2)

# Define time range
start = '2015-01-01'
end = '2023-12-31'  # Avoid using future 2024 data

# ---------------------------------------------------
# 1️⃣ Fire Frequency (MODIS Burned Area)
# ---------------------------------------------------
fires = ee.ImageCollection('MODIS/061/MCD64A1') \
    .filterDate(start, end) \
    .select('BurnDate')

fire_freq = fires.map(lambda img: img.gt(0)).sum()
fire_vis = {'min': 0, 'max': 100, 'palette': ['white', 'orange', 'red']}
m.addLayer(fire_freq, fire_vis, 'Fire Frequency (2015–2023)')

# ---------------------------------------------------
# 2️⃣ Burned Area Extent (MODIS MCD64A1)
# ---------------------------------------------------
burned_area = fires.count()
burned_vis = {'min': 0, 'max': 120, 'palette': ['white', 'yellow', 'brown']}
m.addLayer(burned_area, burned_vis, 'Cumulative Burned Area (2015–2023)')

# ---------------------------------------------------
# 3️⃣ Vegetation Impact (NDVI mean)
# ---------------------------------------------------
ndvi = ee.ImageCollection('MODIS/061/MOD13A2') \
    .filterDate(start, end) \
    .select('NDVI')

ndvi_mean = ndvi.mean()
ndvi_vis = {'min': 0, 'max': 9000, 'palette': ['white', 'green']}
m.addLayer(ndvi_mean, ndvi_vis, 'Mean NDVI (2015–2023)')

# ---------------------------------------------------
# Export to HTML
# --------------------------------------------------
map_file = "fire_watch_map.html"
m.to_html(map_file, notebook_display=False)
print(f"Map saved as {map_file}")

# Open automatically in browser
full_path = os.path.abspath(map_file)
webbrowser.open(f"file://{full_path}")
