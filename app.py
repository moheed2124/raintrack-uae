
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import xarray as xr
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RainTrack UAE",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# MODERN DESIGN
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, #12334a 0%, transparent 35%),
        linear-gradient(145deg, #071321 0%, #0a1929 55%, #0b202a 100%);
    color: #edf6fa;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1c2d, #102638);
    border-right: 1px solid #244052;
}

[data-testid="stSidebar"] * {
    color: #e6f2f7;
}

.hero {
    background: linear-gradient(115deg, #10394a, #10283f 55%, #125047);
    border: 1px solid #286174;
    border-radius: 24px;
    padding: 30px 32px;
    margin: 4px 0 25px 0;
    box-shadow: 0 12px 40px rgba(0,0,0,.18);
}

.hero h1 {
    font-size: 2.65rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -1.5px;
}

.hero p {
    color: #c1dce5;
    font-size: 1.02rem;
    margin: 8px 0 0 0;
}

.eyebrow {
    color: #75e2cf;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.section-heading {
    color: #f0f8fb;
    font-size: 1.35rem;
    font-weight: 750;
    margin-top: 8px;
    margin-bottom: 12px;
}

.muted {
    color: #a9c1ce;
    font-size: .88rem;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #10283c, #123346);
    border: 1px solid #28516a;
    border-radius: 17px;
    padding: 17px 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,.12);
}

div[data-testid="stMetricLabel"] {
    color: #b9d0dc;
}

div[data-testid="stMetricValue"] {
    color: #f4fbff;
    font-weight: 750;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid #2b6875;
    background: linear-gradient(100deg, #087e82, #159b8a);
    color: white;
    font-weight: 700;
    min-height: 42px;
    transition: .2s ease;
}

.stButton > button:hover {
    border-color: #70e0cf;
    color: white;
    transform: translateY(-1px);
}

.stDownloadButton > button {
    border-radius: 12px;
    background: #123d4c;
    color: #e9fbff;
    border: 1px solid #347081;
    font-weight: 700;
}

div[data-testid="stChatMessage"] {
    background: #10283a;
    border: 1px solid #29485a;
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 10px;
}

div[data-testid="stChatInput"] textarea {
    background: #10283a;
    color: white;
    border-radius: 14px;
}

.stTabs [data-baseweb="tab"] {
    color: #c6dce5;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    color: #6ce0cc !important;
}

hr {
    border-color: #244356;
}

.small-status {
    color: #75d9c5;
    font-size: .82rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# OPENROUTER API SETTINGS
# =========================================================

try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"].strip()
    AI_MODEL = st.secrets.get(
        "OPENROUTER_MODEL",
        "openai/gpt-4o-mini"
    )
except (KeyError, FileNotFoundError):
    API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
    AI_MODEL = os.getenv(
        "OPENROUTER_MODEL",
        "openai/gpt-4o-mini"
    )

AI_READY = bool(
    API_KEY and API_KEY != "YOUR_API_KEY_HERE"
)

if AI_READY:
    try:
        test_response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={
                "Authorization": f"Bearer {API_KEY}"
            },
            timeout=20
        )

        st.write("OpenRouter key test:", test_response.status_code)

        if test_response.status_code == 200:
            st.success("OpenRouter recognises your API key!")
        else:
            st.error("OpenRouter did not accept the API key.")
            st.write(test_response.text[:500])

    except requests.exceptions.RequestException as exc:
        st.error(f"Connection test failed: {exc}")
        
if not AI_READY:
    st.warning(
        "OpenRouter API key is missing. "
        "Please check your .streamlit/secrets.toml file."
    )

# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">FROM CLOUD TO CATCHMENT · UAE</div>
    <h1>🌧️ RainTrack UAE</h1>
    <p>
        Understanding rainfall patterns through satellite data,
        interactive mapping and AI-powered insights.
    </p>
</div>
""", unsafe_allow_html=True)

status_col1, status_col2, status_col3 = st.columns([1, 1, 2])

with status_col1:
    st.markdown(
        '<div class="small-status">● Dashboard active</div>',
        unsafe_allow_html=True
    )

with status_col2:
    st.markdown(
        '<div class="small-status">● NASA data explorer</div>',
        unsafe_allow_html=True
    )

with status_col3:
    if AI_READY:
        st.markdown(
            '<div class="small-status">● AI assistant configured</div>',
            unsafe_allow_html=True
        )
    else:
        st.caption("AI assistant not configured")


# =========================================================
# UAE LOCATIONS
# =========================================================

LOCATIONS = {
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
    "Sharjah": (25.3463, 55.4209),
    "Ajman": (25.4052, 55.5136),
    "Ras Al Khaimah": (25.7895, 55.9432),
    "Fujairah": (25.1288, 56.3265),
    "Umm Al Quwain": (25.5647, 55.5552),
    "Al Ain": (24.1917, 55.7606),
}


# =========================================================
# NASA NETCDF READER
# =========================================================

@st.cache_data
def load_nasa_netcdf(file_bytes):

    with tempfile.NamedTemporaryFile(
        suffix=".nc",
        delete=False
    ) as tmp:
        tmp.write(file_bytes)
        temp_path = tmp.name

    ds = None

    try:
        try:
            ds = xr.open_dataset(
                temp_path,
                engine="h5netcdf"
            )
        except Exception:
            ds = xr.open_dataset(temp_path)

        variable_name = "GPM_3IMERGHH_07_precipitation"

        if variable_name not in ds.data_vars:
            raise ValueError(
                f"Could not find {variable_name}. "
                f"Available variables: {list(ds.data_vars)}"
            )

        rainfall = ds[variable_name]

        uae = rainfall.sel(
            lat=slice(22.55, 26.15),
            lon=slice(51.45, 56.45)
        )

        df = uae.to_dataframe(
            name="rain_rate"
        ).reset_index()

        df = df.dropna(subset=["rain_rate"])

        start_time = ds.attrs.get(
            "start_time",
            "2024-04-16T00:00:00Z"
        )

        end_time = ds.attrs.get(
            "end_time",
            "2024-04-27T00:00:00Z"
        )

    finally:
        if ds is not None:
            ds.close()

        if os.path.exists(temp_path):
            os.remove(temp_path)

    df["date"] = pd.to_datetime(
        start_time,
        utc=True
    )

    df["latitude"] = df["lat"]
    df["longitude"] = df["lon"]

    df["date_label"] = (
        str(start_time)[:10]
        + " to "
        + str(end_time)[:10]
    )

    df["source_type"] = "NASA IMERG time-averaged map"

    return df, str(start_time), str(end_time)


# =========================================================
# CSV READER
# =========================================================

ALIASES = {
    "date": ["date", "datetime", "time", "timestamp"],
    "lat": ["lat", "latitude"],
    "lon": ["lon", "longitude"],
    "rain": [
        "precipitation",
        "precipitation_rate",
        "precip_rate",
        "rainfall",
        "rain_rate",
        "value",
        "mean",
        "precip"
    ],
}


def find_column(df, candidates):

    lower = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for name in candidates:
        if name in lower:
            return lower[name]

    for key, original in lower.items():
        if any(candidate in key for candidate in candidates):
            return original

    return None


def load_nasa_csv(uploaded_file):

    raw = pd.read_csv(uploaded_file)

    date_col = find_column(raw, ALIASES["date"])
    lat_col = find_column(raw, ALIASES["lat"])
    lon_col = find_column(raw, ALIASES["lon"])
    rain_col = find_column(raw, ALIASES["rain"])

    if date_col is None or rain_col is None:
        raise ValueError(
            "CSV needs a date/time column and a rainfall column."
        )

    df = pd.DataFrame()

    df["date"] = pd.to_datetime(
        raw[date_col],
        errors="coerce",
        utc=True
    )

    df["rain_rate"] = pd.to_numeric(
        raw[rain_col],
        errors="coerce"
    )

    df["latitude"] = (
        pd.to_numeric(raw[lat_col], errors="coerce")
        if lat_col else np.nan
    )

    df["longitude"] = (
        pd.to_numeric(raw[lon_col], errors="coerce")
        if lon_col else np.nan
    )

    df = df.dropna(
        subset=["date", "rain_rate"]
    )

    df["date_label"] = df["date"].dt.strftime("%Y-%m-%d")
    df["source_type"] = "Uploaded CSV"

    return df


# =========================================================
# SIDEBAR: DATA AND FILTERS
# =========================================================

st.sidebar.markdown("## 🌧️ RainTrack UAE")
st.sidebar.caption("Your rainfall exploration workspace")

uploaded = st.sidebar.file_uploader(
    "Upload rainfall data",
    type=["nc", "csv"],
    help="Upload a NASA NetCDF file or a compatible CSV."
)

st.sidebar.divider()
st.sidebar.markdown("### 📍 Dashboard guide")
st.sidebar.caption(
    "Explore the map, compare UAE locations, "
    "inspect observations and ask the AI assistant."
)


# =========================================================
# SIDEBAR: DATA AND FILTERS
# =========================================================

st.sidebar.markdown("## 🌧️ RainTrack UAE")
st.sidebar.caption("Your rainfall exploration workspace")

uploaded = st.sidebar.file_uploader(
    "Upload rainfall data",
    type=["nc", "csv"],
    help="Upload a NASA NetCDF file or a compatible CSV."
)

st.sidebar.divider()
st.sidebar.markdown("### 📍 Dashboard guide")
st.sidebar.caption(
    "Explore the map, compare UAE locations, "
    "inspect observations and ask the AI assistant."
)

# Find the actual project folder, regardless of where
# Streamlit Cloud runs the application from.
BASE_DIR = Path(__file__).resolve().parent

data = None
is_nasa_period_map = False
period_start = None
period_end = None

try:
    if uploaded is not None:

        if uploaded.name.lower().endswith(".nc"):
            data, period_start, period_end = load_nasa_netcdf(
                uploaded.getvalue()
            )
            is_nasa_period_map = True

        else:
            data = load_nasa_csv(uploaded)

    else:
        # Search both the main project folder and data folder.
        root_nc_files = list(BASE_DIR.glob("*.nc"))

        data_folder = BASE_DIR / "data"

        if data_folder.exists():
            data_nc_files = list(data_folder.glob("*.nc"))
        else:
            data_nc_files = []

        # Combine both lists.
        nc_files = root_nc_files + data_nc_files

        # Remove duplicate paths, if any.
        nc_files = list(dict.fromkeys(nc_files))

        if nc_files:
            selected_file = nc_files[0]

            st.sidebar.success(
                f"NASA file found: {selected_file.name}"
            )

            data, period_start, period_end = load_nasa_netcdf(
                selected_file.read_bytes()
            )

            is_nasa_period_map = True

        else:
            st.sidebar.warning(
                "No .nc file found in the project folder or data folder."
            )

            st.info(
                "No NASA rainfall file was found. "
                "Please upload your .nc or CSV file using the sidebar."
            )

            st.write("Files available in the project folder:")

            try:
                available_files = [
                    str(path.relative_to(BASE_DIR))
                    for path in BASE_DIR.rglob("*")
                    if path.is_file()
                    and ".git" not in path.parts
                ]

                st.write(available_files[:100])

            except Exception:
                st.write("Could not list project files.")

            st.stop()

except Exception as exc:
    st.error(f"Could not load the data: {exc}")
    st.stop()


if data is None or data.empty:
    st.warning(
        "No rainfall data found. Upload a supported file "
        "or check the data folder."
    )
    st.stop()



# =========================================================
# DATA SOURCE INFORMATION
# =========================================================

if is_nasa_period_map:

    st.success("NASA GPM IMERG data successfully loaded.")

    st.info(
        f"Observation period: {period_start} to {period_end}. "
        "This file is a time-averaged precipitation map, "
        "not a live or daily rainfall feed."
    )

else:
    st.success("Your uploaded rainfall observations are loaded.")

st.caption(
    "Source: NASA GPM IMERG Final Run. "
    "Satellite estimates are not direct ground-gauge measurements."
)


# =========================================================
# DATE FILTERS
# =========================================================

st.sidebar.divider()
st.sidebar.markdown("### 📅 Observation filters")

if not is_nasa_period_map:

    min_date = data["date"].min().date()
    max_date = data["date"].max().date()

    date_range = st.sidebar.date_input(
        "Observation date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    filtered = data[
        (data["date"].dt.date >= start_date)
        & (data["date"].dt.date <= end_date)
    ].copy()

else:
    filtered = data.copy()


if filtered.empty:
    st.warning("No data available for this date selection.")
    st.stop()


# =========================================================
# CALCULATE OVERVIEW STATISTICS
# =========================================================

mean_rate = float(filtered["rain_rate"].mean())
max_rate = float(filtered["rain_rate"].max())
min_rate = float(filtered["rain_rate"].min())
median_rate = float(filtered["rain_rate"].median())

highest_row = filtered.loc[
    filtered["rain_rate"].idxmax()
]

location_available = (
    filtered["latitude"].notna().any()
    and filtered["longitude"].notna().any()
)

geo_data = filtered.dropna(
    subset=["latitude", "longitude", "rain_rate"]
).copy()

selected_city = None
city_rate = None
nearest = None
city_lat = None
city_lon = None


# =========================================================
# LOCATION SELECTION
# =========================================================

st.markdown(
    '<div class="section-heading">📍 Explore a UAE location</div>',
    unsafe_allow_html=True
)

if location_available and not geo_data.empty:

    selected_city = st.selectbox(
        "Choose a location to inspect its nearest satellite grid point",
        list(LOCATIONS.keys()),
        index=0
    )

    city_lat, city_lon = LOCATIONS[selected_city]

    geo_data["distance"] = np.sqrt(
        (geo_data["latitude"] - city_lat) ** 2
        + (geo_data["longitude"] - city_lon) ** 2
    )

    nearest = geo_data.loc[
        geo_data["distance"].idxmin()
    ]

    city_rate = float(nearest["rain_rate"])
    distance_km = float(nearest["distance"]) * 111

    c1, c2, c3 = st.columns(3)

    c1.metric(
        f"{selected_city} · estimated rate",
        f"{city_rate:.3f} mm/hr"
    )

    c2.metric(
        "Nearest grid distance",
        f"{distance_km:.1f} km"
    )

    c3.metric(
        "Grid coordinates",
        f"{nearest['latitude']:.2f}, {nearest['longitude']:.2f}"
    )

    st.caption(
        "This value is taken from the nearest available NASA grid cell. "
        "It is not a direct measurement at the city centre."
    )

else:

    st.warning(
        "Location insights need usable latitude and longitude columns."
    )


# =========================================================
# RAINFALL OVERVIEW
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">📊 Rainfall overview</div>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Average rate", f"{mean_rate:.3f} mm/hr")
m2.metric("Highest rate", f"{max_rate:.3f} mm/hr")
m3.metric("Lowest rate", f"{min_rate:.3f} mm/hr")
m4.metric("Grid points / records", f"{len(filtered):,}")


# =========================================================
# PLAIN-LANGUAGE INSIGHTS
# =========================================================

st.markdown(
    '<div class="section-heading">💡 What do the numbers tell us?</div>',
    unsafe_allow_html=True
)

if mean_rate < 0.1:
    overall_description = (
        "The average estimated precipitation rate is very low "
        "across the selected grid cells."
    )
elif mean_rate < 1:
    overall_description = (
        "The average estimated precipitation rate is relatively low, "
        "although some grid cells may have higher values."
    )
else:
    overall_description = (
        "The average estimated precipitation rate is above 1 mm/hr. "
        "Explore the map to see where estimates are higher."
    )

st.info(overall_description)

insight1, insight2 = st.columns(2)

with insight1:
    st.markdown("**Average compared with median**")
    st.write(
        f"The mean is {mean_rate:.3f} mm/hr and the median is "
        f"{median_rate:.3f} mm/hr. The mean is influenced by "
        "higher values, while the median represents the middle "
        "grid-cell value."
    )

with insight2:
    st.markdown("**Highest estimated grid cell**")
    st.write(
        f"The highest value is {max_rate:.3f} mm/hr, at approximately "
        f"{highest_row['latitude']:.2f}° latitude and "
        f"{highest_row['longitude']:.2f}° longitude."
    )


# =========================================================
# MAP AND RAINFALL CHART
# =========================================================

st.divider()

map_tab, chart_tab = st.tabs([
    "🗺️ Interactive rainfall map",
    "📈 Rainfall distribution"
])


with map_tab:

    st.markdown("### Explore rainfall across the UAE")
    st.caption(
        "Click a rainfall point to inspect its nearest grid-cell estimate."
    )

    map_df = geo_data.copy()

    fmap = folium.Map(
        location=[24.2, 54.5],
        zoom_start=7,
        tiles=None
    )

    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Tiles © Esri",
        name="English Street Map",
        overlay=False,
        control=True
    ).add_to(fmap)

    if not map_df.empty:

        max_val = max(
            float(map_df["rain_rate"].max()),
            0.0001
        )

        heat_data = [
            [
                float(row.latitude),
                float(row.longitude),
                float(max(row.rain_rate, 0) / max_val)
            ]
            for row in map_df.itertuples()
        ]

        HeatMap(
            heat_data,
            radius=20,
            blur=16,
            min_opacity=0.25
        ).add_to(fmap)

        for row in map_df.itertuples():

            popup_html = f"""
            <div style="font-family:Arial; width:190px;">
                <h4 style="color:#087f8c;">RainTrack UAE</h4>
                <b>Estimated rainfall rate:</b><br>
                {float(row.rain_rate):.3f} mm/hr
                <br><br>
                <b>Latitude:</b> {float(row.latitude):.3f}
                <br>
                <b>Longitude:</b> {float(row.longitude):.3f}
                <br><br>
                <small>NASA GPM IMERG satellite estimate</small>
            </div>
            """

            folium.CircleMarker(
                location=[
                    float(row.latitude),
                    float(row.longitude)
                ],
                radius=7,
                color="#ffffff",
                weight=1,
                fill=True,
                fill_color="#f59e0b",
                fill_opacity=0.9,
                tooltip=(
                    f"Rainfall: {float(row.rain_rate):.3f} mm/hr"
                ),
                popup=folium.Popup(
                    popup_html,
                    max_width=250
                )
            ).add_to(fmap)

    if location_available and selected_city and nearest is not None:

        folium.Marker(
            [city_lat, city_lon],
            tooltip=f"{selected_city} city centre",
            popup=f"{selected_city} city centre",
            icon=folium.Icon(
                color="blue",
                icon="info-sign"
            )
        ).add_to(fmap)

        folium.CircleMarker(
            [
                float(nearest["latitude"]),
                float(nearest["longitude"])
            ],
            radius=10,
            color="#ffffff",
            weight=3,
            fill=True,
            fill_color="#2563eb",
            fill_opacity=1,
            tooltip=f"{selected_city}: nearest NASA grid point"
        ).add_to(fmap)

    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 9999;
        background: white;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #cccccc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        font-family: Arial;
        color: #222222;
        width: 190px;
    ">
        <b style="font-size:14px;">Rainfall intensity</b>
        <div style="margin-top:10px;">
            <span style="color:#2c7bb6;">●</span>
            Low <span style="float:right;">0–1 mm/hr</span>
        </div>
        <div style="margin-top:7px;">
            <span style="color:#abd9e9;">●</span>
            Light <span style="float:right;">1–2 mm/hr</span>
        </div>
        <div style="margin-top:7px;">
            <span style="color:#ffffbf;">●</span>
            Moderate <span style="float:right;">2–4 mm/hr</span>
        </div>
        <div style="margin-top:7px;">
            <span style="color:#fdae61;">●</span>
            High <span style="float:right;">4–6 mm/hr</span>
        </div>
        <div style="margin-top:7px;">
            <span style="color:#d7191c;">●</span>
            Very high <span style="float:right;">Above 6 mm/hr</span>
        </div>
        <hr style="border:0; border-top:1px solid #ddd;">
        <small>Satellite-estimated rainfall rate</small>
    </div>
    """

    fmap.get_root().html.add_child(
        folium.Element(legend_html)
    )

    folium.LayerControl().add_to(fmap)

    map_result = st_folium(
        fmap,
        use_container_width=True,
        height=530,
        returned_objects=["last_object_clicked"]
    )

    clicked = (
        map_result.get("last_object_clicked")
        if map_result else None
    )

    if clicked and not map_df.empty:

        click_lat = clicked.get("lat")
        click_lon = clicked.get("lng")

        if click_lat is not None and click_lon is not None:

            distances = np.sqrt(
                (map_df["latitude"] - click_lat) ** 2
                + (map_df["longitude"] - click_lon) ** 2
            )

            clicked_point = map_df.loc[
                distances.idxmin()
            ]

            st.markdown("### 📍 Selected rainfall point")

            ca, cb, cc = st.columns(3)

            ca.metric(
                "Estimated rate",
                f"{float(clicked_point['rain_rate']):.3f} mm/hr"
            )

            cb.metric(
                "Latitude",
                f"{float(clicked_point['latitude']):.3f}°"
            )

            cc.metric(
                "Longitude",
                f"{float(clicked_point['longitude']):.3f}°"
            )

            st.caption(
                "The value is the nearest available NASA grid-cell "
                "estimate to your click, not a measurement at the "
                "exact clicked position."
            )

    else:
        st.info("Click a rainfall point on the map to inspect its value.")

    st.caption(
        "The heat layer is a relative visual guide. Its colours are "
        "not a calibrated rainfall-intensity scale."
    )


with chart_tab:

    st.markdown("### How are rainfall estimates distributed?")

    if is_nasa_period_map:

        fig = px.histogram(
            filtered,
            x="rain_rate",
            nbins=20,
            title="Distribution of estimated precipitation rates",
            labels={
                "rain_rate": "Precipitation rate (mm/hr)"
            },
            color_discrete_sequence=["#23b6a5"],
            template="plotly_dark"
        )

    else:

        daily = (
            filtered.groupby(
                filtered["date"].dt.date
            )["rain_rate"]
            .mean()
            .reset_index()
        )

        daily.columns = ["Date", "Average rate"]

        fig = px.line(
            daily,
            x="Date",
            y="Average rate",
            markers=True,
            title="Average rainfall rate over time",
            template="plotly_dark"
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e9f4f8",
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if is_nasa_period_map:
        st.caption(
            "This histogram shows the distribution of grid-cell "
            "values in the time-averaged map. It is not a daily trend."
        )


# =========================================================
# CITY COMPARISON
# =========================================================

if location_available and not geo_data.empty:

    st.divider()

    st.markdown(
        '<div class="section-heading">🏙️ Compare UAE locations</div>',
        unsafe_allow_html=True
    )

    city_results = []

    for city, (lat, lon) in LOCATIONS.items():

        distances = np.sqrt(
            (geo_data["latitude"] - lat) ** 2
            + (geo_data["longitude"] - lon) ** 2
        )

        closest_index = distances.idxmin()
        point = geo_data.loc[closest_index]

        city_results.append({
            "Location": city,
            "Estimated rate (mm/hr)": float(point["rain_rate"]),
            "Grid latitude": float(point["latitude"]),
            "Grid longitude": float(point["longitude"])
        })

    city_df = pd.DataFrame(city_results)

    city_fig = px.bar(
        city_df.sort_values(
            "Estimated rate (mm/hr)",
            ascending=False
        ),
        x="Location",
        y="Estimated rate (mm/hr)",
        color="Estimated rate (mm/hr)",
        color_continuous_scale="Tealgrn",
        template="plotly_dark"
    )

    city_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e9f4f8",
        height=390,
        xaxis_title="UAE location",
        yaxis_title="Nearest grid estimate (mm/hr)"
    )

    st.plotly_chart(
        city_fig,
        use_container_width=True
    )

    st.caption(
        "Each bar represents the nearest available satellite grid cell "
        "to that city's coordinates. These are not city-wide averages."
    )


# =========================================================
# DATA TABLE AND DOWNLOAD
# =========================================================

st.divider()

with st.expander("📋 Explore and download rainfall data"):

    st.write(
        "Inspect the rainfall estimates currently used in the dashboard."
    )

    table_df = filtered.copy()

    numeric_columns = table_df.select_dtypes(
        include=["number"]
    ).columns

    table_df[numeric_columns] = (
        table_df[numeric_columns].round(3)
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = table_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download rainfall data (CSV)",
        data=csv_data,
        file_name="raintrack_uae_rainfall_data.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.caption(
        "The download contains the currently filtered data. "
        "Rainfall values are satellite-estimated rates in mm/hr."
    )


# =========================================================
# AI ASSISTANT
# =========================================================

st.divider()

st.markdown("""
<div class="section-heading">🤖 Meet RainTrack AI</div>
<div class="muted">
Your rainfall data companion. Ask questions, explore patterns
and get simple explanations based on the currently loaded data.
</div>
""", unsafe_allow_html=True)


if "raintrack_messages" not in st.session_state:
    st.session_state.raintrack_messages = []


# Build current dashboard data context.
summary = {
    "number_of_records": int(len(filtered)),
    "average_rate_mm_per_hour": round(mean_rate, 4),
    "maximum_rate_mm_per_hour": round(max_rate, 4),
    "minimum_rate_mm_per_hour": round(min_rate, 4),
    "median_rate_mm_per_hour": round(median_rate, 4),
    "highest_grid_point": {
        "latitude": round(float(highest_row["latitude"]), 4),
        "longitude": round(float(highest_row["longitude"]), 4),
        "rate_mm_per_hour": round(max_rate, 4)
    },
    "selected_location": selected_city,
    "selected_location_nearest_grid_rate_mm_per_hour": (
        round(city_rate, 4)
        if city_rate is not None else None
    ),
    "data_type": (
        "NASA IMERG time-averaged map"
        if is_nasa_period_map
        else "Uploaded CSV observations"
    ),
    "observation_period": (
        f"{period_start} to {period_end}"
        if is_nasa_period_map
        else (
            f"{filtered['date'].min()} to {filtered['date'].max()}"
        )
    )
}


st.markdown("**✨ Try asking:**")

suggestions = [
    "Summarise the rainfall data for me.",
    "Which UAE location has the highest estimate?",
    "What does mm/hr mean?",
    "Explain the difference between mean and median.",
]

suggestion_cols = st.columns(2)

for i, suggestion in enumerate(suggestions):

    with suggestion_cols[i % 2]:

        if st.button(
            suggestion,
            key=f"suggestion_{i}",
            use_container_width=True
        ):
            st.session_state.pending_raintrack_question = suggestion


control_a, control_b = st.columns([1, 4])

with control_a:

    if st.button(
        "🗑️ Clear chat",
        use_container_width=True
    ):
        st.session_state.raintrack_messages = []
        st.rerun()

with control_b:

    if AI_READY:
        st.caption(f"● OpenRouter configured · Model: {AI_MODEL}")
    else:
        st.caption("AI is waiting for an OpenRouter API key.")


# Display existing conversation.
for message in st.session_state.raintrack_messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


pending_question = st.session_state.pop(
    "pending_raintrack_question",
    None
)

typed_question = st.chat_input(
    "Ask RainTrack AI about the rainfall data..."
)

question = pending_question or typed_question


if question:

    st.session_state.raintrack_messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        if not AI_READY:

            answer = (
                "The AI assistant is not connected yet. "
                "Please check your OpenRouter API key in "
                "`.streamlit/secrets.toml`."
            )

            st.warning(answer)

        else:

            answer = ""

            with st.spinner("RainTrack AI is thinking..."):

                try:

                    system_prompt = """
You are RainTrack AI, the friendly assistant inside RainTrack UAE.

Your job is to explain rainfall data in simple, clear language.

IMPORTANT RULES:
1. Use the supplied dashboard data as your factual source.
2. Never invent measurements, locations, dates or statistics.
3. Explain precipitation rate in mm/hr as a rate, not an accumulated total.
4. The NASA IMERG dataset may be a time-averaged map. If so, never call
   it a daily or half-hourly time series.
5. Satellite estimates are not direct ground-gauge measurements.
6. Do not claim to provide live weather, weather forecasts, flood warnings,
   street-level measurements or groundwater recharge predictions.
7. Do not claim that a high rainfall rate automatically means flooding.
8. If the supplied data cannot answer a question, say so honestly.
9. Use friendly, accessible language. Explain technical terms.
10. When useful, use short headings and bullet points.
11. You may explain possible relevance to water security, but clearly
    distinguish interpretation from measured data.

You are helping users understand the data, not making safety decisions.
"""

                    recent_messages = (
                        st.session_state.raintrack_messages[-10:]
                    )

                    api_messages = [
                        {
                            "role": "system",
                            "content": (
                                system_prompt
                                + "\n\nCURRENT DASHBOARD DATA:\n"
                                + str(summary)
                            )
                        }
                    ]

                    api_messages.extend(recent_messages)

                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {API_KEY}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": (
                                "https://raintrack-uae.streamlit.app"
                            ),
                            "X-Title": "RainTrack UAE"
                        },
                        json={
                            "model": AI_MODEL,
                            "messages": api_messages,
                            "temperature": 0.3,
                            "max_tokens": 700
                        },
                        timeout=60
                    )

                    # Raise an exception for HTTP errors.
                    response.raise_for_status()

                    result = response.json()

                    # Safely extract the AI answer.
                    answer = (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )

                    if isinstance(answer, list):
                        answer = "\n".join(
                            str(item.get("text", item))
                            if isinstance(item, dict)
                            else str(item)
                            for item in answer
                        )

                    if not answer or not str(answer).strip():
                        raise ValueError(
                            "The model returned an empty response."
                        )

                    answer = str(answer)
                    st.markdown(answer)

                except requests.exceptions.HTTPError as exc:

                    status_code = (
                        exc.response.status_code
                        if exc.response is not None
                        else "Unknown"
                    )

                    error_details = (
                        "No additional details were provided."
                    )

                    if exc.response is not None:

                        try:
                            error_data = exc.response.json()

                            if isinstance(error_data, dict):
                                error_object = error_data.get(
                                    "error",
                                    error_data
                                )

                                if isinstance(error_object, dict):
                                    error_details = (
                                        error_object.get(
                                            "message",
                                            str(error_object)
                                        )
                                    )
                                else:
                                    error_details = str(error_object)

                            else:
                                error_details = str(error_data)

                        except ValueError:
                            error_details = exc.response.text[:1500]

                    answer = (
                        f"OpenRouter returned HTTP error {status_code}.\n\n"
                        f"Details: {error_details}\n\n"
                        f"Configured model: {AI_MODEL}"
                    )

                    st.error("AI connection failed")
                    st.code(answer)

                except requests.exceptions.Timeout:

                    answer = (
                        "The request to OpenRouter timed out after "
                        "60 seconds. Please try again."
                    )

                    st.error(answer)

                except requests.exceptions.ConnectionError:

                    answer = (
                        "RainTrack could not connect to OpenRouter. "
                        "Please check your internet connection and try again."
                    )

                    st.error(answer)

                except requests.exceptions.RequestException as exc:

                    answer = (
                        f"A network error occurred: {str(exc)[:1000]}"
                    )

                    st.error(answer)

                except (ValueError, KeyError, IndexError) as exc:

                    answer = (
                        "The AI service returned an unexpected response. "
                        f"Details: {str(exc)[:1000]}"
                    )

                    st.error(answer)

                except Exception as exc:

                    answer = (
                        "Something unexpected went wrong: "
                        f"{str(exc)[:1000]}"
                    )

                    st.error(answer)

        # Save both successful answers and error messages.
        st.session_state.raintrack_messages.append({
            "role": "assistant",
            "content": answer
        })


# =========================================================
# ABOUT AND METHODOLOGY
# =========================================================

st.divider()

with st.expander("ℹ️ About RainTrack UAE and its methodology"):

    st.markdown("""
### Our mission

RainTrack UAE explores how satellite rainfall estimates can help
people understand rainfall patterns and think about water security.

### Data source

**NASA GPM IMERG Final Run**

- Satellite-estimated precipitation.
- The current NetCDF file is a time-averaged map covering
  16–26 April 2024.
- Values are precipitation rates in mm/hr, not accumulated
  rainfall totals in mm.
- City insights use the nearest available satellite grid cell.
- Satellite estimates are not direct ground measurements.

### Important limitations

This prototype is not a live weather service, street-level sensor,
weather forecast, flood-warning system or groundwater-recharge model.

The map and charts help explore the supplied observations.
They should not be used alone for emergency or safety decisions.

### Learn more

[NASA IMERG documentation](https://gpm.nasa.gov/data/imerg)

[NASA Giovanni](https://giovanni.gsfc.nasa.gov/giovanni/)

[NASA Worldview](https://worldview.earthdata.nasa.gov/)
    """)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<hr>
<div style="text-align:center; padding:12px 0 22px 0;">
    <div style="color:#76ddcb; font-weight:800; letter-spacing:1px;">
        🌧️ RAINTRACK UAE
    </div>
    <div style="color:#91aebb; font-size:.82rem; margin-top:5px;">
        From Cloud to Catchment · Exploring rainfall for water security
    </div>
    <div style="color:#718b99; font-size:.72rem; margin-top:8px;">
        Built with NASA GPM IMERG · Streamlit · Python
    </div>
</div>
""", unsafe_allow_html=True)
