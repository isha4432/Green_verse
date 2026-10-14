import urllib.request
import urllib.parse
import json

locations = [
    ("Kurnool", 15.8289, 78.0360),
    ("Vijayawada", 16.5062, 80.6480),
    ("Hyderabad", 17.3850, 78.4867),
    ("New South Wales", -31.8402, 145.6128)
]

print("==================================================")
print("GREEN VERSE — LOCATION-AWARE LIVE DATA INTEGRITY TEST")
print("==================================================")

for name, lat, lon in locations:
    url = f"http://127.0.0.1:8000/api/weather/current?lat={lat}&lon={lon}&name={urllib.parse.quote(name)}&refresh=true"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"\n=============================")
        print(f"LOCATION: {name}")
        print(f"REQUEST URL: {url}")
        print(f"RESPONSE LATITUDE: {data.get('latitude')}")
        print(f"RESPONSE LONGITUDE: {data.get('longitude')}")
        print(f"CURRENT TEMPERATURE: {data.get('temperature')} °C")
        print(f"CURRENT HUMIDITY: {data.get('humidity')} %")
        print(f"CURRENT PRECIPITATION: {data.get('precipitation')} mm")
        print(f"CURRENT WIND: {data.get('wind_speed')} km/h ({data.get('wind_direction')}°)")
        print(f"PRESSURE: {data.get('pressure')} hPa")
        print(f"WEATHER CONDITION: {data.get('weather_condition')}")
        print(f"SOURCE: {data.get('source')}")
        print(f"IS LIVE: {data.get('is_live')}")
        print(f"CACHED: {data.get('cached')}")
        print(f"TIMESTAMP: {data.get('timestamp')}")
        
        df = data.get('daily_forecast', {})
        print(f"7-DAY FORECAST DATES: {df.get('time', [])}")
        print(f"7-DAY PRECIPITATION (mm): {df.get('precipitation_sum_mm', [])}")
        print(f"7-DAY MAX TEMP (°C): {df.get('temperature_2m_max', [])}")
