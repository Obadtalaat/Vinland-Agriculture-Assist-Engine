import requests
import pandas as pd
import streamlit as st

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
    "Cactus Pear": {"min_moisture": 8.0, "max_moisture": 45.0, "min_temp": 5.0, "max_temp": 45.0}
}

st.title("Vinland")

choice = st.selectbox("Pick a crop to plant:", list(crops.keys()))
lat = st.number_input("Latitude:", value=30.9667, format="%.4f")
lon = st.number_input("Longitude:", value=31.1667, format="%.4f")

selected_crop = crops[choice]

if st.button("Check Field"):
    query_params = {
        "parameters": "T2M,T2M_MIN,GWETROOT",
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": "20250302",
        "end": "20250307",
        "format": "JSON"   
    }

    st.write(f"Processing query for {choice} please hold...")

    response = requests.get(url, params=query_params)
    raw_data = response.json()
    weather_dic = raw_data["properties"]["parameter"]

    farm_sheet = pd.DataFrame(weather_dic)
    farm_sheet["Moisture_Pct"] = farm_sheet["GWETROOT"] * 100

    st.dataframe(farm_sheet)

    avg_temp = farm_sheet["T2M"].mean()
    coldest_night = farm_sheet["T2M_MIN"].min()
    avg_moisture = farm_sheet["Moisture_Pct"].mean()

    st.write(f"Average Temp: {avg_temp:.1f} C | Coldest Night: {coldest_night:.1f} C | Average Moisture: {avg_moisture:.1f}%")

    if coldest_night < 0.0 or avg_temp < selected_crop["min_temp"]:
        st.error(f"Decision: Too cold for {choice}. Risk of frost or seed rot.")
    elif avg_moisture > selected_crop["max_moisture"]:
        st.warning(f"Decision: Soil is too waterlogged for {choice}. Risk of root rot.")
    elif avg_moisture < selected_crop["min_moisture"] and avg_temp > selected_crop["max_temp"]:
        st.error(f"Decision: Too hot and dry for {choice}. Irrigate immediately.")
    elif avg_moisture < selected_crop["min_moisture"]:
        st.warning(f"Decision: Soil is too dry for {choice}. Needs water.")
    elif avg_temp > selected_crop["max_temp"]:
        st.warning(f"Decision: Moisture is fine, but temperatures are too hot for {choice}.")
    else:
        st.success(f"Decision: Conditions look good for {choice}!")

    suitable_crops = []
    for name, rules in crops.items():
        if name != choice:
            temp_ok = coldest_night >= 0.0 and rules["min_temp"] <= avg_temp <= rules["max_temp"]
            moisture_ok = rules["min_moisture"] <= avg_moisture <= rules["max_moisture"]
            if temp_ok and moisture_ok:
                suitable_crops.append(name)

    if suitable_crops:
        st.info(f"Other crops that fit these exact conditions: {', '.join(suitable_crops)}")
    else:
        st.info("No other crops in the catalog match these exact conditions without irrigation or protection.")