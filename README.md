# 🌧️ RainTrack UAE
### From Cloud to Catchment — Satellite-Based Rainfall Visualisation & AI-Assisted Analysis

**RainTrack UAE** is an interactive rainfall analysis platform designed to visualise and explore satellite-derived precipitation data across the United Arab Emirates.

The project focuses on the UAE's extreme rainfall event between **16 April and 24 April 2024**, using NASA's Global Precipitation Measurement (GPM) IMERG satellite data to explore rainfall patterns and provide accessible, data-driven insights.

Our goal is to make complex rainfall information easier to understand through interactive maps, statistical visualisations and an AI-powered assistant.

---

## 🚀 Live Demo

**Explore the application:** [RainTrack UAE – Live Dashboard](https://raintrack-uae-7ef7me3fs9yvageznmpbcx.streamlit.app/)

Explore the interactive rainfall dashboard, satellite-derived precipitation visualisations, statistical analysis and RainTrack AI assistant.

---

## 1. The Problem

Extreme rainfall events can create significant challenges for urban infrastructure, transportation, drainage systems and emergency response.

However, raw satellite precipitation datasets are often difficult to interpret without technical knowledge or specialised software.

There is a need for an accessible platform that can:

- Visualise rainfall patterns across different regions of the UAE.
- Make satellite precipitation data easier to explore.
- Allow users to investigate rainfall estimates near major cities.
- Present rainfall statistics in an understandable format.
- Help users interpret rainfall data through AI-assisted explanations.

## 2. Our Solution

RainTrack UAE transforms satellite-derived precipitation data into an interactive dashboard.

Users can explore rainfall information through an interactive UAE map, examine statistical summaries, compare locations and ask questions using an integrated AI assistant.

By combining geospatial visualisation, data analytics and artificial intelligence, the platform makes satellite rainfall information more accessible and understandable.

## 3. Key Features

### 🗺️ Interactive Rainfall Map
- Displays rainfall estimates across the UAE.
- Uses an interactive heatmap and geographical markers.
- Allows users to select major UAE cities.
- Identifies the nearest satellite grid point to a selected city.
- Displays estimated precipitation rates and grid-point information.

### 📊 Rainfall Data Analytics
- Calculates mean, maximum, minimum and median precipitation rates.
- Provides rainfall distribution visualisations.
- Supports city comparisons using nearest grid-cell estimates.
- Displays processed rainfall data in a structured table.
- Allows users to download data as a CSV file.

### 🤖 RainTrack AI
- Integrated AI assistant powered by OpenRouter.
- Answers questions about rainfall information displayed in the dashboard.
- Explains rainfall statistics and visualisations in simple language.
- Uses available dashboard data to provide context-aware responses.

### 📁 Flexible Data Input
- Supports NASA GPM IMERG NetCDF datasets.
- Supports CSV uploads containing rainfall measurements.
- Automatically identifies common date, rainfall, latitude and longitude column names in supported CSV files.

## 4. Study Area & Data Source

| Parameter | Details |
|---|---|
| Study area | United Arab Emirates |
| Study period | 16–24 April 2024 |
| Satellite dataset | NASA GPM IMERG Final Run |
| Data formats | NetCDF and CSV |
| Main variable | `GPM_3IMERGHH_07_precipitation` |
| Precipitation unit | mm/hr |

**Data source:** [NASA Global Precipitation Measurement (GPM)](https://gpm.nasa.gov/)

The application processes satellite precipitation estimates within a geographical bounding box covering the UAE.

For the current NetCDF workflow, the application visualises a time-averaged precipitation map for the selected dataset period rather than a live or daily rainfall feed.

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas | Data processing and analysis |
| NumPy | Numerical computations |
| Xarray | NetCDF and multidimensional satellite data processing |
| Folium | Interactive geographical mapping |
| Plotly | Interactive charts and visualisations |
| Streamlit-Folium | Map integration with Streamlit |
| OpenRouter API | AI assistant integration |
| Requests | API communication |

## 6. Current Limitations

RainTrack UAE is currently a prototype for satellite-based rainfall exploration and AI-assisted interpretation.

The current implementation:

- Does not provide live rainfall monitoring.
- Does not generate weather forecasts.
- Does not predict floods or issue operational flood warnings.
- Does not integrate ground-based weather station observations.
- Does not calculate groundwater recharge or simulate surface runoff.
- Uses satellite-derived estimates, which may differ from ground-based measurements.

**Important:** The nearest grid-cell rainfall estimate is not equivalent to a city-wide rainfall average.

## 7. Future Development

We aim to expand RainTrack UAE into a more comprehensive environmental monitoring and analysis platform.

Planned improvements include:

- **Automated Data Integration:** Regular ingestion of updated satellite precipitation datasets.
- **Ground Station Integration:** Combining satellite estimates with ground-based rainfall measurements.
- **Rainfall Forecasting:** Exploring machine learning models for rainfall prediction.
- **Flood Risk Modelling:** Incorporating elevation, drainage networks and runoff analysis.
- **Advanced Analytics:** Improving geographical comparisons and rainfall trend analysis.
- **Early Warning Research:** Exploring how rainfall analysis could support future disaster preparedness systems.

---

**RainTrack UAE — From Cloud to Catchment.**

*Developed as a prototype project focused on the UAE's April 2024 extreme rainfall event.*
