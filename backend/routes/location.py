from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
from services.location_service import LocationService

router = APIRouter(prefix="/api", tags=["Location & Live Weather"])

@router.get("/location/search")
async def search_locations(q: Optional[str] = Query("", description="Place name, district, or state")):
    try:
        results = LocationService.search_locations(q or "")
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Geocoding service unavailable: {str(e)}")

@router.get("/location/reverse")
async def reverse_geocode_location(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        res = LocationService.reverse_geocode(lat=lat, lon=lon)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Reverse geocoding service unavailable: {str(e)}")

@router.get("/location/data")
async def get_location_data(
    lat: float = Query(15.8289, description="Latitude"),
    lon: float = Query(78.0360, description="Longitude"),
    name: str = Query("Kurnool", description="Location name"),
    state: str = Query("Andhra Pradesh", description="State name"),
    country: str = Query("India", description="Country name"),
    refresh: bool = Query(False, description="Force fresh fetch bypassing cache")
):
    return LocationService.get_weather_for_location(
        lat=lat,
        lon=lon,
        location_name=name,
        state_name=state,
        country_name=country,
        force_refresh=refresh
    )

@router.get("/location/{location_id}/data")
async def get_location_by_id_data(
    location_id: str,
    lat: Optional[float] = Query(15.8289),
    lon: Optional[float] = Query(78.0360),
    name: Optional[str] = Query("Kurnool"),
    refresh: bool = Query(False)
):
    return LocationService.get_weather_for_location(
        lat=lat or 15.8289,
        lon=lon or 78.0360,
        location_name=name or location_id,
        force_refresh=refresh
    )

@router.get("/weather/current")
async def get_current_weather(
    lat: float = Query(15.8289, description="Latitude"),
    lon: float = Query(78.0360, description="Longitude"),
    name: Optional[str] = Query("Selected Location"),
    state: Optional[str] = Query(""),
    country: Optional[str] = Query("India"),
    refresh: bool = Query(False)
):
    return LocationService.get_weather_for_location(
        lat=lat,
        lon=lon,
        location_name=name or "Selected Location",
        state_name=state or "",
        country_name=country or "India",
        force_refresh=refresh
    )
