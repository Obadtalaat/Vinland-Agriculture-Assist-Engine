import requests
import pandas as pd

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

crops = {
    "1": {"name": "Wheat", "min_moisture": 28.0, "max_temp": 31.0},
    "2": {"name": "Corn", "min_moisture": 35.0, "max_temp": 34.0},
    "3": {"name": "Fava Bean", "min_moisture": 30.0, "max_temp": 29.0},
    "4": {"name": "Olive", "min_moisture": 18.0, "max_temp": 38.0}
}

print("Pick a crop to plant:")
print("1 - Wheat")
print("2 - Corn")
print("3 - Fava Bean")
print("4 - Olive")

choice = input("Enter a number (1-4): ")
selected_crop = crops[choice]



query_params = {
    "parameters": "T2M,GWETTOP",
    "community": "AG",
    "latitude": "30.9667",
    "longitude": "31.1667",  #long and lat for sadat city :|
    "start" : "20250302",
    "end" : "20250307",
    "format" :"JSON"   
}

print(f"\nProcessing query for {selected_crop['name']} please hold...")

response = requests.get(url, params=query_params)

raw_data = response.json()

weather_dic = raw_data["properties"]["parameter"]

farm_sheet = pd.DataFrame(weather_dic)
farm_sheet["Moisture_Pct"] = farm_sheet["GWETTOP"] * 100

print(farm_sheet)

avg_temp = farm_sheet["T2M"].mean()
avg_moisture = farm_sheet["Moisture_Pct"].mean()

print(f"\nAverage Temp: {avg_temp:.1f} C | Average Moisture: {avg_moisture:.1f}%")

if avg_moisture < selected_crop["min_moisture"] and avg_temp > selected_crop["max_temp"]:
    print(f"Decision: Too hot and dry for {selected_crop['name']}. Irrigate immediately.")
elif avg_moisture < selected_crop["min_moisture"]:
    print(f"Decision: Soil is too dry for {selected_crop['name']}. Needs water.")
elif avg_temp > selected_crop["max_temp"]:
    print(f"Decision: Moisture is fine, but temperatures are too hot for {selected_crop['name']}.")
else:
    print(f"Decision: Conditions look good for {selected_crop['name']}!")