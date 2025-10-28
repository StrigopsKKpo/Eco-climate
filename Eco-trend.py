import ee
import geemap.foliumap as geemap
import os, webbrowser

# Initialize Earth Engine
try:
    ee.Initialize(project="ee-ferrenoe")
except ee.EEException:
    ee.Authenticate()
    ee.Initialize(project="ee-ferrenoe")

# Define time range
start_date = '2000-01-01'
end_date = '2023-12-31'

# Load MODIS NDVI collection
ndvi_collection = ee.ImageCollection('MODIS/061/MOD13A2') \
    .select('NDVI') \
    .filterDate(start_date, end_date)

# Add a time band for trend analysis
def add_time_band(image):
    year = ee.Date(image.get('system:time_start')).difference(ee.Date(start_date), 'year')
    return image.addBands(ee.Image.constant(year).rename('t')).float()

ndvi_with_time = ndvi_collection.map(add_time_band)

# Linear regression: NDVI ~ time
trend = ndvi_with_time.select(['t', 'NDVI']).reduce(ee.Reducer.linearFit())

# Extract slope (trend) and intercept
slope = trend.select('scale')  # slope represents trend per year
intercept = trend.select('offset')

# Define visualization parameters
trend_vis = {
    'min': -50,
    'max': 50,
    'palette': ['brown', 'white', 'green']
}

mean_ndvi = ndvi_collection.mean()
mean_vis = {
    'min': 0,
    'max': 8000,
    'palette': ['white', 'lightgreen', 'darkgreen']
}

# Create map
m = geemap.Map(center=[0, 0], zoom=2)
m.addLayer(mean_ndvi, mean_vis, 'Mean NDVI (2000–2023)')
m.addLayer(slope, trend_vis, 'NDVI Trend (Slope)')

# Export HTML map
output_file = "maps/eco_trends_map.html"
m.to_html(output_file, notebook_display=False)
print(f"Map saved to {output_file}")

# Open automatically
full_path = os.path.abspath(output_file)
webbrowser.open(f"file://{full_path}")
