# 🌍 Eco-Climate

**Eco-Climate** is a collection of open, data-driven environmental analysis projects linking **climate dynamics, ecosystems, and sustainability**.
The goal is to build transparent tools that make satellite and meteorological data accessible for research, education, and ecological insight.

---

## 🔬 Overview

Each module explores a key environmental theme:

| Module                    | Focus                                              | Example Question                                           |
| ------------------------- | -------------------------------------------------- | ---------------------------------------------------------- |
| **🌿 Eco-Trends**         | Vegetation health (NDVI) & temperature trends      | How has vegetation responded to climate change since 2000? |
| **💧 Drought & Water**    | Soil moisture, rainfall, and drought index mapping | Where are long-term drying patterns emerging?              |
| **🔥 Fire Watch**         | Wildfire detection & impact analysis               | How have fire frequencies changed over the last decade?    |
| **☀️ Solar Atlas**        | Renewable energy & solar potential                 | What is the solar energy potential in different regions?   |
| **🦋 Biodiversity Pulse** | Habitat & species richness under climate stress    | Which ecosystems show the greatest biodiversity loss risk? |

---

[![Eco-Trend Map](https://img.shields.io/badge/View-Eco%20Trend%20Map-green)](https://StrigopsKKpo.github.io/Eco-climate/eco_trend_map.html)

[![Drought-Water Map](https://img.shields.io/badge/View-Drought%20Water%20Map-blue)](https://StrigopsKKpo.github.io/Eco-climate/drought_water_map.html)

[![Fire-Watch Map](https://img.shields.io/badge/View-Fire%20Watch%20Map-red)](https://StrigopsKKpo.github.io/Eco-climate/fire_watch_map.html)

[![Solar-Atlas Map](https://img.shields.io/badge/View-Solar%20Atlas%20Map-yellow)](https://StrigopsKKpo.github.io/Eco-climate/solar_atlas_map.html)

[![Biodiversity-Pulse Map](https://img.shields.io/badge/View-Biodiversity%20Pulse%20Map-purple)](https://StrigopsKKpo.github.io/Eco-climate/biodiversity_pulse_map.html)

## 🧭 Objectives

* Combine **Google Earth Engine**, **Python**, and **open data sources** (NASA, Copernicus, NOAA).
* Provide reproducible code and clear visualizations.
* Encourage data-driven ecological awareness.

---

## 🧰 Tech Stack

* **Python 3.10+**
* **Google Earth Engine API**
* **geemap**, **xarray**, **pandas**, **matplotlib**, **plotly**, **folium**
* **Jupyter Notebooks** for research
* **Streamlit** for interactive dashboards

---

## 🗂️ Repository Structure

```
Eco-Climate/
│
├── projects/
│   ├── eco-trends/           # NDVI & temperature analysis
│   ├── drought-water/        # Rainfall & moisture trends
│   ├── fire-watch/           # Wildfire detection
│   ├── solar-atlas/          # Renewable energy mapping
│   └── biodiversity-pulse/   # Habitat & species analysis
│
├── data/                     # Local datasets (if any)
├── notebooks/                # Exploratory Jupyter notebooks
├── scripts/                  # Reusable Python utilities
├── README.md                 # You are here
└── requirements.txt
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/StrigopsKKpo/Eco-climate.git
cd Eco-climate

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate    # (or venv\Scripts\activate on Windows)

# 3. Install dependencies
pip install -r requirements.txt
```

To use **Google Earth Engine**, make sure you are logged in:

```bash
earthengine authenticate
```

---

## 🧪 How to Run a Project

Example for `eco-trends`:

```bash
cd projects/eco-trends
jupyter notebook eco-trends.ipynb
```

Or run the Streamlit app (if available):

```bash
streamlit run app.py
```

---

## 📊 Example Outputs

* Interactive time-series of NDVI change
* Maps of temperature anomalies
* Correlation plots between vegetation health and precipitation
* Renewable energy potential maps
* Biodiversity and habitat loss visualizations

---

## 🤝 Contributing

Contributions and collaborations are welcome!
If you’d like to suggest a dataset, analysis, or visualization idea, please open an **Issue** or submit a **Pull Request**.

---

## 🪶 License

This repository is open source under the **MIT License**.
You are free to use, modify, and share with attribution.

---

## 👤 Author

**Noé Ferré**
🌐 [github.com/StrigopsKKpo](https://github.com/StrigopsKKpo)
💬 Building open-source climate & ecology tools with Python and Earth Engine.
