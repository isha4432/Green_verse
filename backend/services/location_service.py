import time
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Weather Code Mapping (WMO Weather interpretation codes)
WMO_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

# Simple in-memory cache for external weather and geocoding responses (TTL: 10 minutes)
_cache = {}
CACHE_TTL = 600

class LocationService:
    @staticmethod
    def search_locations(query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []

        cache_key = f"geo_{q.lower()}"
        now = time.time()
        if cache_key in _cache and (now - _cache[cache_key]["ts"]) < CACHE_TTL:
            return _cache[cache_key]["data"]

        # 1. Primary real geocoding service: Open-Meteo Geocoding API
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(q)}&count=10&language=en&format=json"
            req = urllib.request.Request(url, headers={"User-Agent": "GreenVerse-Agricultural-Platform/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                results = data.get("results", [])
                formatted = []
                for r in results:
                    place_name = r.get("name") or ""
                    city = r.get("name") or ""
                    district = r.get("admin2") or ""
                    state = r.get("admin1") or ""
                    country = r.get("country") or ""
                    lat = round(float(r.get("latitude", 0.0)), 4)
                    lon = round(float(r.get("longitude", 0.0)), 4)

                    parts = [place_name]
                    if district and district.lower() != place_name.lower():
                        parts.append(district)
                    if state and state.lower() != place_name.lower() and state.lower() != district.lower():
                        parts.append(state)
                    if country:
                        parts.append(country)
                    display_name = ", ".join(parts)

                    item_data = {
                        "id": f"loc_{lat}_{lon}",
                        "location_id": f"loc_{lat}_{lon}",
                        "name": place_name,
                        "place_name": place_name,
                        "city": city,
                        "district": district,
                        "state": state,
                        "country": country,
                        "latitude": lat,
                        "longitude": lon,
                        "display_name": display_name,
                        "source": "Open-Meteo Geocoding",
                        "selected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    formatted.append(item_data)

                _cache[cache_key] = {"data": formatted, "ts": now}
                return formatted
        except Exception as e_om:
            # 2. Secondary real geocoding service: OpenStreetMap Nominatim
            try:
                nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&addressdetails=1&limit=8"
                nom_req = urllib.request.Request(nom_url, headers={"User-Agent": "GreenVerse-AgriApp/1.0 (contact@greenverse.ag)"})
                with urllib.request.urlopen(nom_req, timeout=6) as resp:
                    nom_data = json.loads(resp.read().decode())
                    formatted = []
                    for item in nom_data:
                        addr = item.get("address", {})
                        p_name = item.get("name") or addr.get("city") or addr.get("town") or addr.get("village") or item.get("display_name", "").split(",")[0]
                        c_name = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or p_name
                        d_name = addr.get("state_district") or addr.get("county") or addr.get("district") or ""
                        s_name = addr.get("state") or ""
                        co_name = addr.get("country") or ""
                        lat = round(float(item.get("lat", 0.0)), 4)
                        lon = round(float(item.get("lon", 0.0)), 4)
                        disp_name = item.get("display_name") or f"{p_name}, {s_name}, {co_name}"
                        item_data = {
                            "id": f"loc_{lat}_{lon}",
                            "location_id": f"loc_{lat}_{lon}",
                            "name": p_name,
                            "place_name": p_name,
                            "city": c_name,
                            "district": d_name,
                            "state": s_name,
                            "country": co_name,
                            "latitude": lat,
                            "longitude": lon,
                            "display_name": disp_name,
                            "source": "OpenStreetMap Nominatim",
                            "selected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        formatted.append(item_data)
                    _cache[cache_key] = {"data": formatted, "ts": now}
                    return formatted
            except Exception as e_nom:
                print(f"[GreenVerse LocationService Error]: Open-Meteo ({e_om}), Nominatim ({e_nom})")
                from fastapi import HTTPException
                raise HTTPException(status_code=503, detail="Real geocoding service is unavailable. Please check your network connection.")

    @staticmethod
    def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
        lat = round(lat, 4)
        lon = round(lon, 4)
        cache_key = f"rev_{lat}_{lon}"
        now = time.time()
        if cache_key in _cache and (now - _cache[cache_key]["ts"]) < CACHE_TTL:
            return _cache[cache_key]["data"]

        try:
            nom_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
            nom_req = urllib.request.Request(nom_url, headers={"User-Agent": "GreenVerse-AgriApp/1.0 (contact@greenverse.ag)"})
            with urllib.request.urlopen(nom_req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                addr = data.get("address", {})
                p_name = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("suburb") or addr.get("county") or "Current Location"
                c_name = addr.get("city") or addr.get("town") or addr.get("village") or p_name
                d_name = addr.get("state_district") or addr.get("county") or addr.get("district") or ""
                s_name = addr.get("state") or ""
                co_name = addr.get("country") or "India"
                disp_name = data.get("display_name") or f"{p_name}, {s_name}, {co_name}"

                res = {
                    "id": f"loc_{lat}_{lon}",
                    "location_id": f"loc_{lat}_{lon}",
                    "name": p_name,
                    "place_name": p_name,
                    "city": c_name,
                    "district": d_name,
                    "state": s_name,
                    "country": co_name,
                    "latitude": lat,
                    "longitude": lon,
                    "display_name": disp_name,
                    "source": "Browser Geolocation + OpenStreetMap Reverse Geocoder",
                    "selected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                _cache[cache_key] = {"data": res, "ts": now}
                return res
        except Exception as e:
            print(f"[GreenVerse Reverse Geocoding Fallback]: {e}")
            return {
                "id": f"loc_{lat}_{lon}",
                "location_id": f"loc_{lat}_{lon}",
                "name": f"Coordinates ({lat}, {lon})",
                "place_name": f"Coordinates ({lat}, {lon})",
                "city": f"Coords {lat},{lon}",
                "district": "",
                "state": "",
                "country": "",
                "latitude": lat,
                "longitude": lon,
                "display_name": f"Latitude: {lat}, Longitude: {lon}",
                "source": "Browser Geolocation (Coordinates)",
                "selected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    @staticmethod
    def get_weather_for_location(
        lat: float,
        lon: float,
        location_name: str = "Selected Location",
        state_name: str = "",
        country_name: str = "India",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        lat = round(lat, 4)
        lon = round(lon, 4)
        cache_key = f"wx_{lat}_{lon}"
        now = time.time()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Logging as requested in specification
        safe_loc = str(location_name).encode('ascii', 'replace').decode()
        print(f"\n==========================================")
        print(f"[LOCATION SELECTED]: {safe_loc}")
        print(f"[COORDINATES]: Latitude={lat}, Longitude={lon}")
        print(f"[FETCHING LIVE WEATHER]: Open-Meteo Meteorological Service")
        print(f"[DATA SOURCE]: Open-Meteo Public API")
        print(f"[TIMESTAMP]: {now_str}")
        print(f"==========================================\n")

        if not force_refresh and cache_key in _cache and (now - _cache[cache_key]["ts"]) < CACHE_TTL:
            cached_res = dict(_cache[cache_key]["data"])
            cached_res["location"] = location_name
            cached_res["location_info"] = {
                "name": location_name,
                "state": state_name,
                "country": country_name,
                "latitude": lat,
                "longitude": lon,
                "formatted": f"{location_name}{', ' + state_name if state_name else ''}{', ' + country_name if country_name else ''}"
            }
            cached_res["cached"] = True
            return cached_res

        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m,cloud_cover,surface_pressure"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
                f"&timezone=auto"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "GreenVerse-AgriApp/1.0"})
            raw = None
            last_err = None
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(req, timeout=7) as resp:
                        raw = json.loads(resp.read().decode())
                        break
                except Exception as e:
                    last_err = e
                    time.sleep(0.3)
            
            if not raw:
                raise last_err or Exception("Failed to fetch data from Open-Meteo API")
            
            current = raw.get("current", {})
            daily = raw.get("daily", {})

            w_code = int(current.get("weather_code", 0))
            condition_label = WMO_CODES.get(w_code, "Clear Sky")

            t_max = daily.get("temperature_2m_max", [30.0])[0] if daily.get("temperature_2m_max") else 30.0
            t_min = daily.get("temperature_2m_min", [20.0])[0] if daily.get("temperature_2m_min") else 20.0
            p_sum = daily.get("precipitation_sum", [0.0])[0] if daily.get("precipitation_sum") else 0.0
            w_max = daily.get("wind_speed_10m_max", [10.0])[0] if daily.get("wind_speed_10m_max") else 10.0

            temp_val = round(float(current.get("temperature_2m", 25.0)), 1)
            humid_val = int(current.get("relative_humidity_2m", 50))
            rain_val = round(float(current.get("precipitation", 0.0)), 1)
            wind_val = round(float(current.get("wind_speed_10m", 5.0)), 1)
            wind_dir = int(current.get("wind_direction_10m", 0))
            clouds = int(current.get("cloud_cover", 0))
            pressure = round(float(current.get("surface_pressure", 1013.25)), 1)

            wx_payload = {
                "location": location_name,
                "location_info": {
                    "name": location_name,
                    "state": state_name,
                    "country": country_name,
                    "latitude": lat,
                    "longitude": lon,
                    "formatted": f"{location_name}{', ' + state_name if state_name else ''}{', ' + country_name if country_name else ''}"
                },
                "latitude": lat,
                "longitude": lon,
                "temperature": temp_val,
                "temperature_c": temp_val,
                "humidity": humid_val,
                "humidity_pct": humid_val,
                "rainfall": rain_val,
                "rainfall_mm": rain_val,
                "precipitation": rain_val,
                "wind": wind_val,
                "wind_speed": wind_val,
                "wind_speed_kmh": wind_val,
                "wind_direction": wind_dir,
                "cloud_cover": clouds,
                "pressure": pressure,
                "weather_condition": condition_label,
                "weather_code": w_code,
                "cached": False,
                "is_live": True,
                "forecast_today": {
                    "temp_max": round(float(t_max), 1),
                    "temp_min": round(float(t_min), 1),
                    "precipitation_sum_mm": round(float(p_sum), 1),
                    "max_wind_speed_kmh": round(float(w_max), 1)
                },
                "daily_forecast": {
                    "time": daily.get("time", []),
                    "precipitation_sum_mm": [round(float(v), 1) if v is not None else 0.0 for v in daily.get("precipitation_sum", [])],
                    "temperature_2m_max": [round(float(v), 1) if v is not None else 0.0 for v in daily.get("temperature_2m_max", [])],
                    "temperature_2m_min": [round(float(v), 1) if v is not None else 0.0 for v in daily.get("temperature_2m_min", [])],
                    "wind_speed_10m_max": [round(float(v), 1) if v is not None else 0.0 for v in daily.get("wind_speed_10m_max", [])]
                },
                "current": {
                    "temperature": {"value": temp_val, "unit": "°C", "source": "Open-Meteo", "timestamp": now_str},
                    "humidity": {"value": humid_val, "unit": "%", "source": "Open-Meteo", "timestamp": now_str},
                    "precipitation": {"value": rain_val, "unit": "mm", "source": "Open-Meteo", "timestamp": now_str},
                    "wind_speed": {"value": wind_val, "unit": "km/h", "source": "Open-Meteo", "timestamp": now_str},
                    "wind_direction": {"value": wind_dir, "unit": "°", "source": "Open-Meteo", "timestamp": now_str},
                    "cloud_cover": {"value": clouds, "unit": "%", "source": "Open-Meteo", "timestamp": now_str},
                    "pressure": {"value": pressure, "unit": "hPa", "source": "Open-Meteo", "timestamp": now_str},
                    "weather_condition": condition_label,
                    "weather_code": w_code
                },
                "soil_status": "Unavailable",
                "soil_source": "No live sensor connected · Enter manually",
                "water_status": "Calculated Watershed Model",
                "source": "Open-Meteo Meteorological Service",
                "source_provider": "Open-Meteo Meteorological Service",
                "source_type": "LIVE_API",
                "is_live": True,
                "timestamp": now_str
            }

            _cache[cache_key] = {"data": wx_payload, "ts": now}
            return wx_payload

        except Exception as e:
            print(f"[GreenVerse Weather API Error]: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail=f"Live weather data service temporarily unreachable: {str(e)}")
