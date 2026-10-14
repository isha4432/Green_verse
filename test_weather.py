import urllib.request
import json

locations = [
    ("Kurnool", 15.8289, 78.0360),
    ("Vijayawada", 16.5062, 80.6480),
    ("Hyderabad", 17.3850, 78.4867)
]

print("TESTING FASTAPI REAL LIVE WEATHER ENDPOINTS:")
for name, lat, lon in locations:
    url = f"http://127.0.0.1:8000/api/weather/current?lat={lat}&lon={lon}&name={name}&refresh=true"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"\n--- {name} ---")
        print(f"Status Code: {resp.status}")
        print(f"Latitude: {data.get('latitude')}, Longitude: {data.get('longitude')}")
        print(f"Temperature: {data.get('temperature')} °C")
        print(f"Humidity: {data.get('humidity')} %")
        print(f"Precipitation: {data.get('precipitation')} mm")
        print(f"Wind Speed: {data.get('wind_speed')} km/h")
        print(f"Condition: {data.get('weather_condition')}")
        print(f"Source: {data.get('source')}")
        print(f"Cached: {data.get('cached')}")
        print(f"Timestamp: {data.get('timestamp')}")
