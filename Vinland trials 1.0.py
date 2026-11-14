import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

crops = {
    "Wheat": {"min_moisture": 25.0, "max_moisture": 70.0, "min_temp": 4.0, "max_temp": 31.0},
    "Corn": {"min_moisture": 35.0, "max_moisture": 65.0, "min_temp": 10.0, "max_temp": 34.0},
    "Fava Bean": {"min_moisture": 30.0, "max_moisture": 70.0, "min_temp": 4.0, "max_temp": 29.0},
    "Olive": {"min_moisture": 15.0, "max_moisture": 55.0, "min_temp": 2.0, "max_temp": 38.0},
    "Egyptian Cotton": {"min_moisture": 30.0, "max_moisture": 65.0, "min_temp": 14.0, "max_temp": 37.0},
    "Rice": {"min_moisture": 55.0, "max_moisture": 95.0, "min_temp": 13.0, "max_temp": 36.0},
    "Sugarcane": {"min_moisture": 45.0, "max_moisture": 80.0, "min_temp": 16.0, "max_temp": 38.0},
    "Tomato": {"min_moisture": 30.0, "max_moisture": 70.0, "min_temp": 10.0, "max_temp": 34.0},
    "Potato": {"min_moisture": 35.0, "max_moisture": 75.0, "min_temp": 6.0, "max_temp": 28.0},
    "Banana": {"min_moisture": 40.0, "max_moisture": 75.0, "min_temp": 15.0, "max_temp": 37.0},
    "Grapes": {"min_moisture": 20.0, "max_moisture": 65.0, "min_temp": 5.0, "max_temp": 36.0},
    "Mango": {"min_moisture": 25.0, "max_moisture": 65.0, "min_temp": 12.0, "max_temp": 40.0},
    "Strawberry": {"min_moisture": 35.0, "max_moisture": 80.0, "min_temp": 3.0, "max_temp": 28.0},
    "Cabbage": {"min_moisture": 35.0, "max_moisture": 85.0, "min_temp": 1.0, "max_temp": 26.0},
    "Sugar Beet": {"min_moisture": 30.0, "max_moisture": 80.0, "min_temp": 3.0, "max_temp": 30.0},
    "Date Palm": {"min_moisture": 10.0, "max_moisture": 50.0, "min_temp": 10.0, "max_temp": 45.0},
    "Cactus Pear": {"min_moisture": 8.0, "max_moisture": 45.0, "min_temp": 5.0, "max_temp": 45.0},
    "Sorghum": {"min_moisture": 15.0, "max_moisture": 60.0, "min_temp": 15.0, "max_temp": 38.0},
    "Chickpea": {"min_moisture": 20.0, "max_moisture": 55.0, "min_temp": 10.0, "max_temp": 30.0},
    "Clover (Berseem)": {"min_moisture": 30.0, "max_moisture": 80.0, "min_temp": 5.0, "max_temp": 28.0},
    "Cowpea": {"min_moisture": 25.0, "max_moisture": 70.0, "min_temp": 16.0, "max_temp": 35.0}
}

st.set_page_config(page_title="Vinland", layout="wide")
st.title("Vinland: Field Shift")
st.markdown("Turning satellite observations into practical crop-rotation choices to adapt to changing weather and water.")

col_left, col_right = st.columns([1, 2])

with col_right:
    m = folium.Map(location=[30.9667, 31.1667], zoom_start=6)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=360, use_container_width=True, returned_objects=["last_clicked"])

lat = 30.9667
lon = 31.1667

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

with col_left:
    with st.container(border=True):
        choice = st.selectbox("Select primary cash crop:", list(crops.keys()))
        selected_crop = crops[choice]
        
        st.caption(
            f"**{choice} Target Range:** {selected_crop['min_temp']}°C to {selected_crop['max_temp']}°C | "
            f"{selected_crop['min_moisture']}% to {selected_crop['max_moisture']}% moisture"
        )
        
        st.markdown("#### Selected Coordinates")
        c_lat, c_lon = st.columns(2)
        c_lat.metric("Latitude", f"{lat:.4f}")
        c_lon.metric("Longitude", f"{lon:.4f}")
        st.caption("Click anywhere on the map to move your pin.")
        
        run_analysis = st.button("Run Field Analysis", type="primary", use_container_width=True)

if run_analysis:
    end_date = datetime.now() - timedelta(days=4)
    start_date = end_date - timedelta(days=14)
    
    query_params = {
        "parameters": "T2M,T2M_MIN,T2M_MAX,GWETROOT,PRECTOTCORR,RH2M,WS2M",
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON"   
    }

    with st.spinner("Fetching NASA Earth observations..."):
        response = requests.get(url, params=query_params)
        
    if response.status_code == 200:
        raw_data = response.json()
        weather_dic = raw_data["properties"]["parameter"]

        farm_sheet = pd.DataFrame(weather_dic)
        farm_sheet = farm_sheet[farm_sheet["GWETROOT"] != -999.0]
        farm_sheet["Moisture_Pct"] = farm_sheet["GWETROOT"] * 100
        
        st.session_state["farm_sheet"] = farm_sheet
    else:
        st.error("Failed to connect to the NASA POWER API. Please try again later.")

if "farm_sheet" in st.session_state:
    farm_sheet = st.session_state["farm_sheet"]
    st.divider()

    avg_temp = farm_sheet["T2M"].mean()
    coldest_night = farm_sheet["T2M_MIN"].min()
    max_temp = farm_sheet["T2M_MAX"].max()
    avg_moisture = farm_sheet["Moisture_Pct"].mean()
    total_rain = farm_sheet["PRECTOTCORR"].sum()

    st.subheader("Current Field Conditions (14-Day Satellite Window)")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Average Temp", f"{avg_temp:.1f} °C", border=True)
    m2.metric("Coldest Night", f"{coldest_night:.1f} °C", border=True)
    m3.metric("Peak Heat", f"{max_temp:.1f} °C", border=True)
    m4.metric("Root Moisture", f"{avg_moisture:.1f}%", border=True)
    m5.metric("Total Rain", f"{total_rain:.1f} mm", border=True)

    if coldest_night < 0.0 or avg_temp < selected_crop["min_temp"]:
        st.error(f"**Warning:** Too cold for {choice}. Risk of frost damage or seed rot.")
    elif avg_moisture > selected_crop["max_moisture"]:
        st.warning(f"**Warning:** Soil is too waterlogged for {choice}. Risk of root rot.")
    elif avg_moisture < selected_crop["min_moisture"] and max_temp > selected_crop["max_temp"]:
        st.error(f"**Critical:** High heat and dry soil detected. {choice} will face severe drought stress.")
    elif avg_moisture < selected_crop["min_moisture"]:
        st.warning(f"**Warning:** Root-zone moisture is too low for {choice}. Irrigation required.")
    elif max_temp > selected_crop["max_temp"]:
        st.warning(f"**Warning:** Moisture is adequate, but peak temperatures exceed optimal range for {choice}.")
    else:
        st.success(f"**Clear:** Environmental conditions are currently optimal for {choice}.")

    suitable_crops = []
    for name, rules in crops.items():
        if name != choice:
            temp_ok = coldest_night >= 0.0 and rules["min_temp"] <= avg_temp <= rules["max_temp"]
            moisture_ok = rules["min_moisture"] <= avg_moisture <= rules["max_moisture"]
            if temp_ok and moisture_ok:
                suitable_crops.append(name)

    if suitable_crops:
        st.info(f"**Alternative Crops Fitting Current Conditions:** {', '.join(suitable_crops)}")

    st.divider()
    st.subheader("12-24 Month Crop Rotation Plans")
    st.caption("Comparing options to cut fertilizer costs, save water, and protect topsoil.")
    
    r1, r2, r3 = st.columns(3)
    
    with r1:
        with st.container(border=True):
            st.markdown("#### Plan A: Current Routine")
            st.write(f"**Schedule:** {choice} → Bare Field")
            st.write("**Impact:** Field sits empty during off-months.")
            st.write("**Risks:** High vulnerability to wind and rain erosion. Drains soil nutrients requiring more chemical fertilizer.")
        
    with r2:
        with st.container(border=True):
            st.markdown("#### Plan B: Water-Saving Shift")
            st.write(f"**Schedule:** Sorghum/Millet → Winter Chickpea → {choice}")
            st.write("**Impact:** Handles dry spells and uses roughly 30% less water.")
            st.write("**Benefits:** Chickpeas add natural nitrogen. Best when satellite data shows dropping groundwater trends.")

    with r3:
        with st.container(border=True):
            st.markdown("#### Plan C: Soil-Building Shift")
            st.write(f"**Schedule:** {choice} → Winter Clover/Cowpea")
            st.write("**Impact:** Keeps living roots in the soil year-round.")
            st.write("**Benefits:** Rebuilds natural nitrogen to cut fertilizer costs, prevents topsoil loss, and provides livestock forage.")

    st.divider()
    st.subheader("Local Ground Check Required")
    st.markdown("""
    * **Markets:** Check if local merchants are buying alternative crops (like sorghum or chickpeas) at a fair price this season.
    * **Soil Health:** Satellites cannot see underground compaction or root pests; consult a local agronomist for salinity checks.
    """)

    with st.expander("View Raw NASA Satellite Table"):
        st.dataframe(farm_sheet, use_container_width=True)