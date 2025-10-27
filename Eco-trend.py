
# # Eco-Trends Map
# 
# This notebook displays MODIS NDVI and ESA WorldCover datasets using Google Earth Engine and geemap.

# %%
import ee
import geemap.foliumap as geemap

# Authenticate and initialize Earth Engine
try:
    ee.Initialize(project="ee-ferrenoe")
except ee.EEException:
    ee.Authenticate()
    ee.Initialize(project="ee-ferrenoe")

# %%
# Create a map centered on your area of interest
m = geemap.Map(center=[20, 0], zoom=2)

# %%
# ===============================
# ADD ECO-TRENDS DATASETS HERE
# ===============================

# MODIS NDVI (Vegetation Index)
ndvi_collection = ee.ImageCollection('MODIS/061/MOD13A2').select('NDVI').mean()
m.addLayer(
    ndvi_collection,
    {'min': 0, 'max': 9000, 'palette': ['white', 'green']},
    'MODIS NDVI'
)

# Global Land Cover (ESA)
landcover = ee.Image('ESA/WorldCover/v100/2020')
m.addLayer(
    landcover,
    {'min': 10, 'max': 100, 'palette': ['forestgreen', 'yellow', 'brown', 'blue']},
    'ESA WorldCover 2020'
)

# Display the map in the notebook
m

# Export the interactive map to an HTML file
m.to_html("eco_trend_map.html", notebook_display=False)
print("Map saved as eco_trend_map.html")
