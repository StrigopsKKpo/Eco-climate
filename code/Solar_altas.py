# solar_atlas_simple.py
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

# -------------------------
# 1️⃣ Global Solar Radiation Proxy (MODIS)
# -------------------------
solar_proxy = ee.ImageCollection('MODIS/006/MOD09GA') \
    .select('sur_refl_b01') \
    .filterDate('2023-01-01', '2023-12-31') \
    .mean()

solar_vis = {'min': 0, 'max': 2000, 'palette': ['blue', 'yellow', 'red']}
m.addLayer(solar_proxy, solar_vis, 'Solar Radiation Proxy (MODIS B01)')

# -------------------------
# 2️⃣ Suitable Land for Solar Farms
# -------------------------
landcover = ee.Image('ESA/WorldCover/v100/2020')
suitable_land = landcover.updateMask(
    landcover.neq(10)  # remove forests
).updateMask(
    landcover.neq(80)  # remove water
)
m.addLayer(suitable_land, {'palette': ['lightgreen']}, 'Suitable Land (simplified)')

# -------------------------
# 3️⃣ Optional: Solar Potential / Population (simplified)
# -------------------------
population = ee.ImageCollection('CIESIN/GPWv4/population-count') \
    .first()
solar_per_capita = solar_proxy.divide(population.add(1))
pop_vis = {'min': 0, 'max': 500, 'palette': ['white', 'yellow', 'red']}
m.addLayer(solar_per_capita, pop_vis, 'Solar Radiation per Capita')

# -------------------------
# Export to HTML
# -------------------------
map_file = "solar_atlas_map.html"
m.to_html(map_file, notebook_display=False)
print(f"Map saved as {map_file}")

# Open automatically in browser
full_path = os.path.abspath(map_file)
webbrowser.open(f"file://{full_path}")
