from typing import List, Dict, Any
from schemas.climate import ClimateSimulateRequest, ClimateSimulateResponse, SimulatedPlot
from services.ai_service import AIService
from schemas.ai import CropStressRequest

class ClimateService:
    @staticmethod
    def simulate_scenario(req: ClimateSimulateRequest) -> ClimateSimulateResponse:
        default_plots = [
            {"id": "P-1", "name": "North Field", "crop": "tomato", "moisture": 62.0, "temp": 24.0, "w": 28, "h": 16},
            {"id": "P-2", "name": "East Terrace", "crop": "wheat", "moisture": 48.0, "temp": 24.0, "w": 24, "h": 14},
            {"id": "P-3", "name": "South Orchard", "crop": "maize", "moisture": 55.0, "temp": 25.0, "w": 20, "h": 18},
            {"id": "P-4", "name": "West Plots", "crop": "chickpea", "moisture": 42.0, "temp": 24.0, "w": 22, "h": 12},
            {"id": "P-5", "name": "Greenhouse Bed A", "crop": "lettuce", "moisture": 70.0, "temp": 23.0, "w": 18, "h": 10},
            {"id": "P-6", "name": "Greenhouse Bed B", "crop": "sunflower", "moisture": 52.0, "temp": 24.0, "w": 20, "h": 12}
        ]

        plots_input = req.plots if req.plots and len(req.plots) > 0 else default_plots
        simulated_plots: List[SimulatedPlot] = []
        total_risk = 0.0
        total_demand = 0.0

        for p in plots_input:
            base_m = float(p.get("moisture", 50.0))
            base_t = float(p.get("temp", 24.0))
            crop = p.get("crop", "tomato")
            area = float(p.get("w", 20)) * float(p.get("h", 12)) / 100.0 # approximate ha

            # Apply deltas
            sim_t = round(base_t + req.temperature_delta, 1)
            # Moisture drops with soil moisture delta and rainfall decrease
            moist_effect = req.soil_moisture_delta + (req.rainfall_change * 0.15)
            sim_m = max(5.0, min(100.0, round(base_m + moist_effect, 1)))

            # Predict stress
            ai_res = AIService.predict_crop_stress(CropStressRequest(
                crop=crop,
                soil_moisture=sim_m,
                temperature=sim_t,
                rainfall=max(0.0, 15.0 * (1.0 + req.rainfall_change / 100.0)),
                growth_stage=3
            ))

            # Water demand in kL: increases with temperature and moisture deficit
            base_crop_demand = area * 6.5
            temp_demand_mult = 1.0 + max(0.0, req.temperature_delta * 0.08)
            moist_deficit_mult = 1.0 + max(0.0, (60.0 - sim_m) * 0.015)
            plot_demand = round(base_crop_demand * temp_demand_mult * moist_deficit_mult, 1)

            total_risk += ai_res.risk
            total_demand += plot_demand

            simulated_plots.append(SimulatedPlot(
                id=str(p.get("id", "P-?")),
                name=str(p.get("name", "Plot")),
                crop=crop,
                baseline_moisture=base_m,
                simulated_moisture=sim_m,
                baseline_temp=base_t,
                simulated_temp=sim_t,
                stress_risk=ai_res.risk,
                status=ai_res.category,
                water_demand_kL=plot_demand
            ))

        num_plots = max(1, len(simulated_plots))
        mean_risk = round(total_risk / num_plots, 1)

        # Baseline available water 45 kL adjusted by water_change
        baseline_water = 45.0
        water_available = max(0.0, round(baseline_water * (1.0 + req.water_change / 100.0), 1))
        shortage = max(0.0, round(total_demand - water_available, 1))
        resilience_score = max(0.0, min(100.0, round(100.0 - (mean_risk * 0.6) - (min(shortage, 50.0) * 0.8), 1)))

        return ClimateSimulateResponse(
            scenario={
                "temperature_delta": req.temperature_delta,
                "rainfall_change": req.rainfall_change,
                "soil_moisture_delta": req.soil_moisture_delta,
                "water_change": req.water_change
            },
            plots=simulated_plots,
            mean_risk=mean_risk,
            water_demand=round(total_demand, 1),
            water_available=water_available,
            shortage=shortage,
            resilience_score=resilience_score,
            is_demo=True
        )
