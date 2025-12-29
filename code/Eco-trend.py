import ee
import geemap.foliumap as geemap
import os
import webbrowser

# Authenticate and initialize Earth Engine
try:
    ee.Initialize(project="ee-ferrenoe")
except ee.EEException: 
    ee.Authenticate()
    ee.Initialize(project="ee-ferrenoe")

# Create map
m = geemap.Map(center=[10, 0], zoom=2)

# ------------------------------------------------------------------
# 1. BASE NDVI (MODIS mean)
# ------------------------------------------------------------------
ndvi_collection = ee.ImageCollection('MODIS/061/MOD13A2').select('NDVI')
ndvi_mean = ndvi_collection.mean()
m.addLayer(
    ndvi_mean,
    {'min': 0, 'max': 9000, 'palette': ['white', 'green']},
    'Mean NDVI'
)

# ------------------------------------------------------------------
# 2. NDVI SEASONALITY (monthly average)
# ------------------------------------------------------------------
months = ee.List.sequence(1, 12)
def monthly_ndvi(mo):
    mo = ee.Number(mo)
    img = ndvi_collection.filter(ee.Filter.calendarRange(mo, mo, 'month')).mean()
    return img.set('month', mo)

ndvi_monthly = ee.ImageCollection(months.map(monthly_ndvi))

# Example: Add January NDVI layer
january_ndvi = ndvi_monthly.filter(ee.Filter.eq('month', 1)).first()
m.addLayer(
    january_ndvi,
    {'min': 0, 'max': 9000, 'palette': ['brown', 'yellow', 'green']},
    'NDVI January (Seasonality Example)'
)

# ------------------------------------------------------------------
# 3. LAND COVER CHANGE (ESA WorldCover 2020 → 2021)
# ------------------------------------------------------------------
esa2020 = ee.Image('ESA/WorldCover/v100/2020')
esa2021 = ee.Image('ESA/WorldCover/v200/2021')

landcover_change = esa2021.subtract(esa2020).neq(0)
m.addLayer(
    esa2020,
    {'min': 10, 'max': 100, 'palette': ['#006400', '#FFFF00', '#8B4513', '#00BFFF']},
    'ESA WorldCover 2020'
)
m.addLayer(
    esa2021,
    {'min': 10, 'max': 100, 'palette': ['#006400', '#FFFF00', '#8B4513', '#00BFFF']},
    'ESA WorldCover 2021'
)
m.addLayer(
    landcover_change.selfMask(),
    {'palette': ['#FF0000']},
    'Land Cover Change (2020-2021)'
)

# ------------------------------------------------------------------
# 4. HUMAN PRESSURE (VIIRS NIGHTLIGHTS)
# ------------------------------------------------------------------
nightlights = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG') \
    .select('avg_rad').mean()
m.addLayer(
    nightlights,
    {'min': 0, 'max': 60, 'palette': ['black', 'purple', 'orange', 'white']},
    'Human Pressure (Nightlights)'
)

# ------------------------------------------------------------------
# Save & open map
# ------------------------------------------------------------------
map_file = "eco_trend_map.html"
m.to_html(map_file, notebook_display=False)
print(f"Map saved as {map_file}")

# Open automatically in browser
full_path = os.path.abspath(map_file)
webbrowser.open(f"file://{full_path}")


