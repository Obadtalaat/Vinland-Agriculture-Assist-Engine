import requests
import pandas as pd

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

query_params = {
    "parameters": "T2M,GWETTOP",
    "community": "AG",
    "latitude": "31.1287",
    "longitude": "33.7971",  #العريش :|
    "start" : "20250302",
    "end" : "20250307",
    "format" :"JSON"   
    }
print("Processing query please hold...")

response = requests.get(url, params=query_params)

raw_data = response.json()

weather_dic = raw_data["properties"]["parameter"]

farm_sheet = pd.DataFrame(weather_dic)

print(farm_sheet)