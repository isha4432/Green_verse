import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post(path, data):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=== STARTING FULL LOCATION -> FARM -> PLOT VERIFICATION ===")

# TEST A: Kurnool
print("\n[TEST A] Kurnool (Lat: 15.8289, Lon: 78.0360)")
kurnool_farms = get("/api/farms?lat=15.8289&lon=78.0360&city=Kurnool")
print(f"Farms found for Kurnool: {len(kurnool_farms)}")
assert len(kurnool_farms) >= 1, "Expected at least 1 farm for Kurnool"
k_farm = kurnool_farms[0]
print(f"Farm Name: {k_farm.get('name')}")
print(f"Plot Count: {len(k_farm.get('plots', []))}")
k_plots = get(f"/api/farms/{k_farm['id']}/plots")
k_area = sum(p.get('area', 0) for p in k_plots)
print(f"Plot Details: {[(p['name'], p['crop'], p['area']) for p in k_plots]}")
print(f"Total Cultivated Area calculated: {k_area} m²")
assert k_farm.get('name') == "Kurnool Sun Farm"
assert len(k_plots) == 3
assert k_area == 752.0

# TEST B: Vijayawada (before farm creation)
print("\n[TEST B] Vijayawada (Lat: 16.5062, Lon: 80.6480)")
vja_farms = get("/api/farms?lat=16.5062&lon=80.6480&city=Vijayawada")
print(f"Farms found for Vijayawada (initial): {len(vja_farms)}")
# Kurnool farm must NOT appear
assert all(f.get('city') != 'Kurnool' for f in vja_farms), "Kurnool farm leaked into Vijayawada query!"

# TEST C: Create Farm in Vijayawada with 2 plots (300 m² + 200 m² = 500 m²)
print("\n[TEST C] Creating 'Farm Vijayawada A' in Vijayawada with 2 plots...")
new_farm_payload = {
    "name": "Farm Vijayawada A",
    "farm_name": "Farm Vijayawada A",
    "farmer_id": "F-VJA-1",
    "country": "India",
    "state": "Andhra Pradesh",
    "district": "Krishna",
    "city": "Vijayawada",
    "latitude": 16.5062,
    "longitude": 80.6480,
    "area_ha": 0.05,
    "plots": [
        {"name": "Krishna River Plot A", "crop": "tomato", "stage": 3, "condition": "good", "moisture": 55.0, "temp": 27.0, "area": 300.0, "w": 20.0, "h": 15.0},
        {"name": "Krishna River Plot B", "crop": "wheat", "stage": 2, "condition": "good", "moisture": 48.0, "temp": 27.0, "area": 200.0, "w": 20.0, "h": 10.0}
    ]
}
created_farm = post("/api/farms", new_farm_payload)
print(f"Created Farm ID: {created_farm.get('id')}, Area: {created_farm.get('area')} m²")
assert created_farm.get('area') == 500.0

# Fetch Vijayawada farms again
vja_farms_after = get("/api/farms?lat=16.5062&lon=80.6480&city=Vijayawada")
print(f"Farms found for Vijayawada after creation: {len(vja_farms_after)}")
assert len(vja_farms_after) >= 1
v_farm = vja_farms_after[0]
v_plots = get(f"/api/farms/{v_farm['id']}/plots")
v_area = sum(p.get('area', 0) for p in v_plots)
print(f"Vijayawada Farm Name: {v_farm.get('name')}")
print(f"Vijayawada Plot Count: {len(v_plots)}")
print(f"Vijayawada Total Area: {v_area} m²")
assert len(v_plots) == 2
assert v_area == 500.0

# TEST D: Switch back to Kurnool
print("\n[TEST D] Switching back to Kurnool (Lat: 15.8289, Lon: 78.0360)")
kurnool_farms_back = get("/api/farms?lat=15.8289&lon=78.0360&city=Kurnool")
print(f"Farms found for Kurnool: {len(kurnool_farms_back)}")
assert len(kurnool_farms_back) >= 1
k_farm_back = kurnool_farms_back[0]
assert k_farm_back.get('name') == "Kurnool Sun Farm"
assert len(k_farm_back.get('plots', [])) == 3
assert sum(p.get('area', 0) for p in k_farm_back.get('plots', [])) == 752.0

print("\n=== ALL TEST WORKFLOW SCENARIOS PASSED WITH 100% TRUTHFUL DATA! ===")
