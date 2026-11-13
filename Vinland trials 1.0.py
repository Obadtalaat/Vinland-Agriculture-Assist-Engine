import requests
import pandas as pd
import streamlit as st

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

crops = {
    "Wheat": {"min_moisture": 25.0, "max_moisture": 70.0, "min_temp": 4.0, "max_temp": 31.0},
    "Corn": {"min_moisture": 35.0, "max_moisture": 65.0, "min_temp": 10.0, "max_temp": 34.0},
    "Fava Bean": {"min_moisture": 30.0, "max_moisture": 70.0, "min_temp": 4.0, "max_temp": 29.0},
    "Olive": {"min_moisture": 15.0, "max_moisture": 55.0, "min_temp": 2.0, "max_temp": 38.0}
}

st.title("Vinland")

choice = st.selectbox("Pick a crop to plant:", list(crops.keys()))
selected_crop = crops[choice]

if st.button("Check Field"):
    query_params = {
        "parameters": "T2M,T2M_MIN,GWETROOT",
        "community": "AG",
        "latitude": "30.9667",
        "longitude": "31.1667",  #long and lat for sadat city :|
        "start" : "20250302",
        "end" : "20250307",
        "format" :"JSON"   
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