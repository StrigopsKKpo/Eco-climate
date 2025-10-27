import ee
import geemap.foliumap as geemap
import webbrowser
import os

# Authenticate and initialize Earth Engine (if needed)
try:
    ee.Initialize(project="ee-ferrenoe")
except ee.EEException:
    ee.Authenticate()
    ee.Initialize()

# Create a map centered at some coordinates
m = geemap.Map(center=[20, 0], zoom=2)

# Add an Earth Engine dataset (SRTM elevation)
srtm = ee.Image('CGIAR/SRTM90_V4')
m.addLayer(
    srtm,
    {'min': 0, 'max': 3000, 'palette': ['blue', 'green', 'brown']},
    'SRTM Elevation'
)

# Export map to HTML
map_file = "demo_map.html"
m.to_html(map_file, notebook_display=False)
print(f"Map saved as {map_file}")

# Open map in default web browser
full_path = os.path.abspath(map_file)
webbrowser.open(f"file://{full_path}")
