from typing import Dict, Any
from schemas.water_soil import (
    WaterCalculateRequest, WaterCalculateResponse,
    SoilAnalyzeRequest, SoilAnalyzeResponse,
    CropRecommendationRequest, CropRecommendationResponse, CropRecommendationItem
)

class WaterService:
    @staticmethod
    def calculate_water_harvesting(req: WaterCalculateRequest) -> WaterCalculateResponse:
        # Rainfall in m = rainfall (mm) / 1000
        rain_m = req.rainfall / 1000.0
        # Gross harvested volume in m³ / kL = Area * rain_m * coefficient
        gross_harvested = req.catchment_area * rain_m * req.runoff_coefficient
        
        # First flush diverter: drops the first 0.5 mm of rain
        first_flush_vol = min(gross_harvested, req.catchment_area * (req.first_flush_mm / 1000.0))
        net_harvested = max(0.0, gross_harvested - first_flush_vol)

        # Storage & overflow calculation
        stored = min(req.storage_capacity, net_harvested)
        overflow = max(0.0, net_harvested - req.storage_capacity)
        recharge_potential = overflow * 0.85 # 85% goes to groundwater recharge pit

        # Irrigation draw
        irr_supplied = min(req.irrigation_demand, stored)
        remaining_stored = max(0.0, stored - irr_supplied)
        utilization = min(100.0, (stored / max(0.1, req.storage_capacity)) * 100.0)

        return WaterCalculateResponse(
            harvested_water=round(gross_harvested, 2),
            first_flush_diverted=round(first_flush_vol, 2),
            net_inflow=round(net_harvested, 2),
            stored_water=round(remaining_stored, 2),
            irrigation_supplied=round(irr_supplied, 2),
            overflow=round(overflow, 2),
            recharge_potential=round(recharge_potential, 2),
            storage_utilization_pct=round(utilization, 1),
            cycles_analyzed=1
        )

    @staticmethod
    def analyze_soil(req: SoilAnalyzeRequest) -> SoilAnalyzeResponse:
        # Evaluate suitability for the given crop
        ph_ok = 6.0 <= req.ph <= 7.5
        moist_ok = 40.0 <= req.moisture <= 75.0
        om_ok = req.organic_matter >= 2.0

        score = 85.0
        if not ph_ok:
            score -= 15.0
        if not moist_ok:
            score -= 20.0
        if not om_ok:
            score -= 10.0
        if req.slope > 8.0:
            score -= 15.0

        score = max(20.0, min(100.0, score))
        fertility = "High" if score >= 80 else ("Moderate" if score >= 60 else "Low / Degraded")

        recs = []
        amends = []

        if req.ph < 6.0:
            recs.append("Soil is slightly acidic; apply agricultural lime (calcium carbonate) at 1.5 t/ha")
            amends.append("Agricultural Lime")
        elif req.ph > 7.8:
            recs.append("Soil is alkaline; apply gypsum or elemental sulfur to lower pH and mobilize phosphorus")
            amends.append("Gypsum / Elemental Sulfur")

        if req.organic_matter < 2.0:
            recs.append("Organic matter is below target; incorporate 5-8 tons/ha well-rotted farmyard manure or vermicompost")
            amends.append("Vermicompost & Green Manure")

        if req.drainage == "Poor":
            recs.append("Drainage is impeded; construct contour bunds and raised beds to prevent root hypoxia")
            amends.append("Raised bed tillage")

        if not recs:
            recs.append("Optimal soil chemistry and physical structure for target crop")
            amends.append("Standard maintenance compost")

        return SoilAnalyzeResponse(
            texture=req.texture,
            ph=req.ph,
            moisture=req.moisture,
            drainage=req.drainage,
            organic_matter=req.organic_matter,
            slope=req.slope,
            crop=req.crop,
            suitability_score=round(score, 1),
            fertility_index=fertility,
            recommendations=recs,
            amendments=amends
        )

    @staticmethod
    def recommend_crops(req: CropRecommendationRequest) -> CropRecommendationResponse:
        candidates = [
            {
                "crop": "Tomato",
                "water_need": "Medium (350-500 mm)",
                "season": "rabi / summer",
                "duration_days": 90,
                "yield": 32.0,
                "match_ph": (6.0, 7.2),
                "opt_temp": (18, 28),
                "income_score": 92,
                "water_saving_score": 65,
                "resilience_score": 75,
                "reasons": ["High market value per hectare", "Well-suited to silt-loam and drip fertigation"]
            },
            {
                "crop": "Durum Wheat",
                "water_need": "Low-Med (250-400 mm)",
                "season": "rabi",
                "duration_days": 110,
                "yield": 4.8,
                "match_ph": (6.2, 7.8),
                "opt_temp": (15, 25),
                "income_score": 78,
                "water_saving_score": 82,
                "resilience_score": 88,
                "reasons": ["Staple crop with guaranteed minimum price support", "Moderate water requirement with good drought tolerance"]
            },
            {
                "crop": "Chickpea",
                "water_need": "Low (180-280 mm)",
                "season": "rabi",
                "duration_days": 95,
                "yield": 2.2,
                "match_ph": (6.0, 8.0),
                "opt_temp": (16, 26),
                "income_score": 82,
                "water_saving_score": 95,
                "resilience_score": 92,
                "reasons": ["Biological nitrogen fixation enhances soil health", "Minimal supplemental irrigation required"]
            },
            {
                "crop": "Maize",
                "water_need": "Medium (400-600 mm)",
                "season": "kharif / spring",
                "duration_days": 105,
                "yield": 6.5,
                "match_ph": (5.8, 7.5),
                "opt_temp": (20, 30),
                "income_score": 75,
                "water_saving_score": 60,
                "resilience_score": 78,
                "reasons": ["High biomass output and robust intercropping partner", "High C4 photosynthetic efficiency"]
            },
            {
                "crop": "Sunflower",
                "water_need": "Low-Med (200-350 mm)",
                "season": "kharif / rabi",
                "duration_days": 85,
                "yield": 2.0,
                "match_ph": (6.0, 7.5),
                "opt_temp": (20, 32),
                "income_score": 80,
                "water_saving_score": 88,
                "resilience_score": 86,
                "reasons": ["Deep taproot extracts subsoil residual moisture", "Drought tolerant oilseed crop"]
            }
        ]

        scored_list = []
        for c in candidates:
            score = 70
            if req.crop_goal == "income":
                score = c["income_score"]
            elif req.crop_goal == "water_saving":
                score = c["water_saving_score"]
            elif req.crop_goal == "resilience":
                score = c["resilience_score"]
            
            # Adjust score for soil pH match
            if c["match_ph"][0] <= req.ph <= c["match_ph"][1]:
                score += 5
            else:
                score -= 10

            # Adjust for temperature
            if c["opt_temp"][0] <= req.temperature <= c["opt_temp"][1]:
                score += 5
            else:
                score -= 8

            score = max(30, min(99, score))
            scored_list.append(CropRecommendationItem(
                crop=c["crop"],
                score=score,
                water_need=c["water_need"],
                season=c["season"],
                duration_days=c["duration_days"],
                expected_yield_tons_ha=c["yield"],
                reasons=c["reasons"]
            ))

        scored_list.sort(key=lambda x: x.score, reverse=True)
        top = scored_list[0].crop

        return CropRecommendationResponse(
            recommendations=scored_list,
            top_recommendation=top,
            explanation=f"{top} is ranked highest for your goal ({req.crop_goal}) given pH {req.ph} and temperature {req.temperature}°C.",
            is_demo=True
        )
