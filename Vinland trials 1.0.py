import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta, date

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

crops = {
    "Wheat": {"min_moisture": 25.0, "max_moisture": 90.0, "min_temp": 1.0, "max_temp": 32.0, "frost_temp": -10.0},
    "Potato": {"min_moisture": 35.0, "max_moisture": 88.0, "min_temp": 2.0, "max_temp": 28.0, "frost_temp": -4.0},
    "Olive": {"min_moisture": 15.0, "max_moisture": 70.0, "min_temp": 3.0, "max_temp": 38.0, "frost_temp": -5.0},
    "Mango": {"min_moisture": 25.0, "max_moisture": 75.0, "min_temp": 14.0, "max_temp": 40.0, "frost_temp": 2.0},
    "Date Palm": {"min_moisture": 8.0, "max_moisture": 55.0, "min_temp": 10.0, "max_temp": 46.0, "frost_temp": -2.0},
    "Cactus Pear": {"min_moisture": 6.0, "max_moisture": 45.0, "min_temp": 5.0, "max_temp": 45.0, "frost_temp": -2.0},
    "Arabica Coffee": {"min_moisture": 45.0, "max_moisture": 85.0, "min_temp": 14.0, "max_temp": 28.0, "frost_temp": 2.0},
    "Cocoa (Cacao)": {"min_moisture": 55.0, "max_moisture": 92.0, "min_temp": 18.0, "max_temp": 34.0, "frost_temp": 8.0},
    "Tea (Camellia)": {"min_moisture": 50.0, "max_moisture": 90.0, "min_temp": 10.0, "max_temp": 30.0, "frost_temp": -2.0},
    "Rice (Paddy)": {"min_moisture": 55.0, "max_moisture": 98.0, "min_temp": 14.0, "max_temp": 36.0, "frost_temp": 3.0},
    "Corn (Maize)": {"min_moisture": 35.0, "max_moisture": 78.0, "min_temp": 10.0, "max_temp": 34.0, "frost_temp": 0.0},
    "Soybean": {"min_moisture": 35.0, "max_moisture": 82.0, "min_temp": 12.0, "max_temp": 33.0, "frost_temp": 0.0},
    "Egyptian Cotton": {"min_moisture": 30.0, "max_moisture": 72.0, "min_temp": 14.0, "max_temp": 37.0, "frost_temp": 2.0},
    "Sugarcane": {"min_moisture": 45.0, "max_moisture": 85.0, "min_temp": 16.0, "max_temp": 38.0, "frost_temp": 2.0},
    "Wine Grapes": {"min_moisture": 20.0, "max_moisture": 78.0, "min_temp": 4.0, "max_temp": 35.0, "frost_temp": -4.0},
    "Avocado": {"min_moisture": 35.0, "max_moisture": 78.0, "min_temp": 12.0, "max_temp": 32.0, "frost_temp": 0.0},
    "Banana": {"min_moisture": 45.0, "max_moisture": 88.0, "min_temp": 15.0, "max_temp": 37.0, "frost_temp": 3.0},
    "Oats": {"min_moisture": 35.0, "max_moisture": 90.0, "min_temp": 1.0, "max_temp": 26.0, "frost_temp": -8.0},
    "Sugar Beet": {"min_moisture": 30.0, "max_moisture": 88.0, "min_temp": 2.0, "max_temp": 30.0, "frost_temp": -6.0},
    "Quinoa": {"min_moisture": 15.0, "max_moisture": 65.0, "min_temp": 4.0, "max_temp": 28.0, "frost_temp": -5.0},
    "Sorghum": {"min_moisture": 12.0, "max_moisture": 65.0, "min_temp": 15.0, "max_temp": 40.0, "frost_temp": 1.0}
}

st.set_page_config(page_title="Vinland | Field Shift", layout="wide")

st.markdown("""
<style>
    .top-header {
        background: linear-gradient(135deg, #122a1d 0%, #1b4332 60%, #2d6a4f 100%);
        padding: 26px 32px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 24px;
        border-left: 6px solid #52b788;
    }
    .header-tag {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #74c69d;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-sub {
        font-size: 0.98rem;
        color: #d8f3dc;
        margin-top: 6px;
        margin-bottom: 0;
        opacity: 0.9;
    }
    div.stButton > button[kind="primary"] {
        background-color: #2d6a4f;
        color: white;
        border: 1px solid #40916c;
        padding: 0.65rem 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        letter-spacing: 0.3px;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #1b4332;
        border-color: #52b788;
    }
    .spec-panel {
        background: rgba(45, 106, 79, 0.1);
        border: 1px solid rgba(82, 183, 136, 0.3);
        border-left: 4px solid #40916c;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0 14px 0;
    }
    .spec-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #74c69d;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .spec-value {
        font-size: 0.88rem;
        margin: 2px 0;
    }
    .alt-tag {
        display: inline-block;
        background: rgba(45, 106, 79, 0.15);
        border: 1px solid #40916c;
        color: #95d5b2;
        padding: 5px 14px;
        border-radius: 6px;
        margin: 4px 8px 4px 0;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .rotation-card {
        border-radius: 10px;
        padding: 22px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(128, 128, 128, 0.22);
        height: 100%;
    }
    .card-baseline { border-top: 4px solid #e07a5f; }
    .card-water { border-top: 4px solid #457b9d; }
    .card-soil { border-top: 4px solid #40916c; }
    .strategy-tag {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 6px;
    }
    .tag-baseline { color: #e07a5f; }
    .tag-water { color: #64b5f6; }
    .tag-soil { color: #74c69d; }
    .sequence-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(0, 0, 0, 0.22);
        padding: 10px 14px;
        border-radius: 6px;
        margin: 16px 0;
        border: 1px solid rgba(128, 128, 128, 0.2);
        font-size: 0.85rem;
        font-weight: 600;
    }
    .seq-arrow {
        color: #74c69d;
        font-weight: 700;
        padding: 0 6px;
    }
    .metric-row {
        margin-top: 12px;
    }
    .metric-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        margin-bottom: 4px;
    }
    .bar-bg {
        width: 100%;
        height: 6px;
        background: rgba(128, 128, 128, 0.2);
        border-radius: 3px;
        overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        border-radius: 3px;
    }
</style>

<div class="top-header">
    <div class="header-tag">NASA POWER Agroclimatology System</div>
    <p class="header-title">Vinland: Field Shift</p>
    <p class="header-sub">Satellite-driven crop suitability analysis and multi-season rotation planning.</p>
</div>
""", unsafe_allow_html=True)

latest_safe_date = datetime.now().date() - timedelta(days=4)

def get_season_dates(month, day):
    year = latest_safe_date.year
    candidate_end = date(year, month, day) + timedelta(days=14)
    if candidate_end > latest_safe_date:
        year -= 1
    s_date = date(year, month, day)
    e_date = s_date + timedelta(days=14)
    return s_date, e_date

season_presets = {
    "Live Telemetry (Last 14 Days)": (latest_safe_date - timedelta(days=14), latest_safe_date),
    "Spring Planting (May)": get_season_dates(5, 5),
    "Summer Peak (July)": get_season_dates(7, 10),
    "Autumn Harvest (October)": get_season_dates(10, 5),
    "Winter Window (January)": get_season_dates(1, 10)
}

col_left, col_right = st.columns([1.05, 2.25], gap="large")

with col_right:
    m = folium.Map(location=[30.9667, 31.1667], zoom_start=5, tiles="OpenStreetMap", control_scale=True)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Satellite (Labeled)",
        overlay=False,
        control=True,
        show=False
    ).add_to(m)
    folium.LayerControl(position="topright").add_to(m)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=580, use_container_width=True, returned_objects=["last_clicked"])

lat = 30.9667
lon = 31.1667

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

with col_left:
    with st.container(border=True):
        st.markdown("#### Field Parameters")
        choice = st.selectbox("Primary Cash Crop", list(crops.keys()))
        selected_crop = crops[choice]

        st.markdown(f"""
        <div class="spec-panel">
            <div class="spec-label">{choice} Agronomic Thresholds</div>
            <div class="spec-value"><b>Mean Temp Range:</b> {selected_crop['min_temp']}°C to {selected_crop['max_temp']}°C</div>
            <div class="spec-value"><b>Night Frost Limit:</b> {selected_crop['frost_temp']}°C</div>
            <div class="spec-value"><b>Root-Zone Moisture:</b> {selected_crop['min_moisture']}% to {selected_crop['max_moisture']}%</div>
        </div>
        """, unsafe_allow_html=True)

        season_choice = st.selectbox("Seasonal Analysis Window", list(season_presets.keys()))
        default_start, default_end = season_presets[season_choice]

        d_col1, d_col2 = st.columns(2)
        start_date = d_col1.date_input("Start Date", value=default_start, max_value=latest_safe_date)
        end_date = d_col2.date_input("End Date", value=default_end, max_value=latest_safe_date)

        st.markdown("#### Target Coordinates")
        c_lat, c_lon = st.columns(2)
        c_lat.metric("Latitude", f"{lat:.4f}°", border=True)
        c_lon.metric("Longitude", f"{lon:.4f}°", border=True)

        run_analysis = st.button("Run Field Analysis", type="primary", use_container_width=True)

if run_analysis:
    if start_date > end_date:
        st.error("Start Date must be earlier than End Date.")
    else:
        query_params = {
            "parameters": "T2M,T2M_MIN,T2M_MAX,GWETROOT,PRECTOTCORR,RH2M,WS2M",
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d"),
            "format": "JSON"   
        }

        with st.spinner("Retrieving NASA POWER satellite telemetry..."):
            response = requests.get(url, params=query_params)
            
        if response.status_code == 200:
            raw_data = response.json()
            weather_dic = raw_data["properties"]["parameter"]

            farm_sheet = pd.DataFrame(weather_dic)
            farm_sheet = farm_sheet[farm_sheet["GWETROOT"] != -999.0]
            farm_sheet["Moisture_Pct"] = farm_sheet["GWETROOT"] * 100
            
            st.session_state["farm_sheet"] = farm_sheet
            st.session_state["window_label"] = f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"
        else:
            st.error("Failed to connect to the NASA POWER API. Please try again later.")

if "farm_sheet" in st.session_state:
    farm_sheet = st.session_state["farm_sheet"]
    window_label = st.session_state.get("window_label", "14-Day Window")
    st.divider()

    avg_temp = farm_sheet["T2M"].mean()
    coldest_night = farm_sheet["T2M_MIN"].min()
    max_temp = farm_sheet["T2M_MAX"].max()
    avg_moisture = farm_sheet["Moisture_Pct"].mean()
    total_rain = farm_sheet["PRECTOTCORR"].sum()

    st.subheader(f"Field Telemetry ({window_label})")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Mean Temperature", f"{avg_temp:.1f} °C", f"Min: {selected_crop['min_temp']}°C", delta_color="off", border=True)
    m2.metric("Minimum Night Temp", f"{coldest_night:.1f} °C", f"Frost Limit: {selected_crop['frost_temp']}°C", delta_color="off", border=True)
    m3.metric("Peak Daytime Heat", f"{max_temp:.1f} °C", f"Max: {selected_crop['max_temp']}°C", delta_color="off", border=True)
    m4.metric("Root-Zone Moisture", f"{avg_moisture:.1f}%", f"Target: {selected_crop['min_moisture']}–{selected_crop['max_moisture']}%", delta_color="off", border=True)
    m5.metric("Cumulative Rainfall", f"{total_rain:.1f} mm", "Period Total", delta_color="off", border=True)

    if coldest_night < selected_crop["frost_temp"] or avg_temp < selected_crop["min_temp"]:
        st.error(f"**Cold / Frost Risk:** Field temperatures ({avg_temp:.1f}°C mean, {coldest_night:.1f}°C night minimum) fall below the thermal threshold for **{choice}** (min {selected_crop['min_temp']}°C, frost limit {selected_crop['frost_temp']}°C).")
    elif avg_moisture > selected_crop["max_moisture"]:
        st.warning(f"**Excess Moisture Risk:** Root-zone moisture ({avg_moisture:.1f}%) exceeds the {selected_crop['max_moisture']}% upper limit for **{choice}**. Risk of root saturation and fungal rot.")
    elif avg_moisture < selected_crop["min_moisture"] and max_temp > selected_crop["max_temp"]:
        st.error(f"**Compound Drought & Heat Stress:** Peak temperature ({max_temp:.1f}°C) and low root moisture ({avg_moisture:.1f}%) exceed safe limits for **{choice}**. Immediate irrigation required.")
    elif avg_moisture < selected_crop["min_moisture"]:
        st.warning(f"**Moisture Deficit:** Root-zone moisture ({avg_moisture:.1f}%) is below the {selected_crop['min_moisture']}% threshold for **{choice}**. Supplemental irrigation is advised.")
    elif max_temp > selected_crop["max_temp"]:
        st.warning(f"**Thermal Stress:** Root moisture is adequate, but peak daytime heat ({max_temp:.1f}°C) exceeds the {selected_crop['max_temp']}°C threshold for **{choice}**.")
    else:
        st.success(f"**Optimal Conditions:** Current temperature and root-zone moisture metrics are within the target operating window for **{choice}**.")

    suitable_crops = []
    for name, rules in crops.items():
        if name != choice:
            temp_ok = coldest_night >= rules["frost_temp"] and rules["min_temp"] <= avg_temp <= rules["max_temp"]
            moisture_ok = rules["min_moisture"] <= avg_moisture <= rules["max_moisture"]
            if temp_ok and moisture_ok:
                suitable_crops.append(f"<span class='alt-tag'>{name}</span>")

    if suitable_crops:
        st.markdown("##### Viable Alternative Crops for Selected Period")
        st.markdown("".join(suitable_crops), unsafe_allow_html=True)
    else:
        st.info("No other catalog crops match these exact conditions without irrigation or thermal protection.")

    st.divider()
    st.subheader("12–24 Month Crop Rotation Strategies")
    st.caption("Comparative multi-season schedules designed to reduce synthetic input costs, conserve groundwater, and maintain soil structure.")
    
    r1, r2, r3 = st.columns(3, gap="medium")
    
    with r1:
        st.markdown(f"""
        <div class="rotation-card card-baseline">
            <div class="strategy-tag tag-baseline">Plan 01 // Standard Baseline</div>
            <h4 style="margin: 0 0 8px 0;">Continuous Monoculture</h4>
            <p style="font-size: 0.88rem; opacity: 0.8; margin-bottom: 12px;">Single cash-crop cycle leaving topsoil exposed during off-season fallow periods.</p>
            <div class="sequence-bar">
                <span>{choice}</span><span class="seq-arrow">→</span><span>Bare Fallow</span><span class="seq-arrow">→</span><span>{choice}</span>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Water Consumption</span><b>100% (Baseline)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 95%; background: #e07a5f;"></div></div>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Nitrogen Retention</span><b>Low (Requires Synthetic NPK)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 25%; background: #e07a5f;"></div></div>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Erosion Protection</span><b>Minimal (Exposed Topsoil)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 20%; background: #e07a5f;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with r2:
        st.markdown(f"""
        <div class="rotation-card card-water">
            <div class="strategy-tag tag-water">Plan 02 // Water Conservation</div>
            <h4 style="margin: 0 0 8px 0;">Drought-Buffered Rotation</h4>
            <p style="font-size: 0.88rem; opacity: 0.8; margin-bottom: 12px;">Alternates low-transpiration grains with winter legumes to lower irrigation demand.</p>
            <div class="sequence-bar">
                <span>Sorghum</span><span class="seq-arrow">→</span><span>Winter Chickpea</span><span class="seq-arrow">→</span><span>{choice}</span>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Water Consumption</span><b>~70% (-30% Demand)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 65%; background: #64b5f6;"></div></div>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Nitrogen Retention</span><b>Moderate (Pulse Fixation)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 65%; background: #64b5f6;"></div></div>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Erosion Protection</span><b>High (Deep Root Matrix)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 75%; background: #64b5f6;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div class="rotation-card card-soil">
            <div class="strategy-tag tag-soil">Plan 03 // Soil Regeneration</div>
            <h4 style="margin: 0 0 8px 0;">Nitrogen & Forage Integration</h4>
            <p style="font-size: 0.88rem; opacity: 0.8; margin-bottom: 12px;">Maintains continuous root cover using nitrogen-fixing forage crops between cash harvests.</p>
            <div class="sequence-bar">
                <span>{choice}</span><span class="seq-arrow">→</span><span>Clover / Cowpea</span><span class="seq-arrow">→</span><span>{choice}</span>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Water Consumption</span><b>80% (Canopy Moisture Lock)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 75%; background: #52b788;"></div></div>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Nitrogen Retention</span><b>High (Natural Bio-Fixation)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 92%; background: #52b788;"></div></div>
            </div>
            <div class="metric-row">
                <div class="metric-header"><span>Erosion Protection</span><b>Maximum (Year-Round Cover)</b></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 95%; background: #52b788;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    col_check, col_chart = st.columns([1, 1.6], gap="large")

    with col_check:
        with st.container(border=True):
            st.markdown("#### Field Verification Protocol")
            st.markdown("""
            * **Offtake & Market Liquidity:** Verify local cooperative or merchant demand for secondary rotation crops (*Sorghum, Chickpea, Berseem*) prior to planting.
            * **Root-Zone Salinity (EC):** Satellite wetness (`GWETROOT`) does not measure dissolved salts. Conduct a physical soil conductivity check in arid zones.
            * **Subsurface Compaction:** Inspect plow-pan depth before introducing deep-rooting rotation crops.
            """)

    with col_chart:
        with st.container(border=True):
            st.markdown(f"#### Telemetry Trend ({window_label})")
            chart_df = farm_sheet[["T2M_MAX", "T2M", "T2M_MIN", "Moisture_Pct"]].copy()
            chart_df.columns = ["Peak Heat (°C)", "Mean Temp (°C)", "Night Low (°C)", "Root Moisture (%)"]
            st.line_chart(chart_df, height=220)

    with st.expander("View Raw NASA POWER Telemetry Table"):
        st.dataframe(farm_sheet, use_container_width=True)