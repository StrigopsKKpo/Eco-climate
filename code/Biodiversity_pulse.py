# biodiversity_pulse_working.py
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

# -----------------------------
# 1️⃣ NDVI (Vegetation Health)
# -----------------------------
ndvi = ee.ImageCollection('MODIS/061/MOD13A2').select('NDVI').mean()
ndvi_vis = {'min': 0, 'max': 9000, 'palette': ['white', 'green']}
m.addLayer(ndvi, ndvi_vis, 'NDVI (Mean)')

# -----------------------------
# 2️⃣ Land Surface Temperature
# -----------------------------
lst = ee.ImageCollection('MODIS/061/MOD11A2').select('LST_Day_1km').mean().multiply(0.02)
lst_vis = {'min': 200, 'max': 320, 'palette': ['blue', 'white', 'red']}
m.addLayer(lst, lst_vis, 'Temperature (LST)')

# -----------------------------
# 3️⃣ Global Protected Areas
# -----------------------------
protected = ee.FeatureCollection('WCMC/WDPA/current/polygons')
m.addLayer(protected, {'color': 'blue'}, 'Protected Areas')

# -----------------------------
# 4️⃣ Global Land Cover
# -----------------------------
landcover = ee.Image('ESA/WorldCover/v100/2020')
lc_vis = {'min': 10, 'max': 100, 'palette': ['forestgreen', 'yellow', 'brown', 'blue']}
m.addLayer(landcover, lc_vis, 'ESA WorldCover 2020')

# -----------------------------
# Export map to HTML
# -----------------------------
map_file = "maps/biodiversity_pulse_map.html"
m.to_html(map_file, notebook_display=False)
print(f"Map saved as {map_file}")

# Open automatically in browser
full_path = os.path.abspath(map_file)
webbrowser.open(f"file://{full_path}")
