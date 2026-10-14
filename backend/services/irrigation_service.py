from typing import List, Dict, Any
from schemas.irrigation import IrrigationOptimizeRequest, IrrigationOptimizeResponse, PlotAllocation

class IrrigationService:
    @staticmethod
    def optimize_allocation(req: IrrigationOptimizeRequest) -> IrrigationOptimizeResponse:
        plots = req.plots
        if not plots:
            # Default 6 plots
            plots = [
                {"id": "P-1", "name": "North Field", "crop": "tomato", "moisture": 62.0, "priority": 2, "base_demand": 12.0},
                {"id": "P-2", "name": "East Terrace", "crop": "wheat", "moisture": 48.0, "priority": 1, "base_demand": 8.0},
                {"id": "P-3", "name": "South Orchard", "crop": "maize", "moisture": 55.0, "priority": 2, "base_demand": 10.0},
                {"id": "P-4", "name": "West Plots", "crop": "chickpea", "moisture": 42.0, "priority": 1, "base_demand": 6.0},
                {"id": "P-5", "name": "Greenhouse Bed A", "crop": "lettuce", "moisture": 70.0, "priority": 3, "base_demand": 5.0},
                {"id": "P-6", "name": "Greenhouse Bed B", "crop": "sunflower", "moisture": 52.0, "priority": 1, "base_demand": 7.0}
            ]

        total_demand = sum(float(p.base_demand if hasattr(p, 'base_demand') else p.get('base_demand', 8.0)) for p in plots)
        budget = float(req.water_budget)

        allocations: List[PlotAllocation] = []
        allocated_so_far = 0.0

        # Sort plots by urgency / priority (higher priority and lower moisture first)
        def score_plot(p):
            priority = int(getattr(p, 'priority', 1) if hasattr(p, 'priority') else p.get('priority', 1))
            moist = float(getattr(p, 'moisture', 50.0) if hasattr(p, 'moisture') else p.get('moisture', 50.0))
            return priority * 100.0 - moist

        sorted_plots = sorted(plots, key=score_plot, reverse=True)

        if budget >= total_demand:
            # Full satisfaction
            for p in sorted_plots:
                pid = str(getattr(p, 'id', p.get('id', 'P-?')))
                name = str(getattr(p, 'name', p.get('name', 'Plot')))
                crop = str(getattr(p, 'crop', p.get('crop', 'Crop')))
                demand = float(getattr(p, 'base_demand', p.get('base_demand', 8.0)))
                
                allocations.append(PlotAllocation(
                    plot_id=pid,
                    name=name,
                    crop=crop,
                    demand_kL=demand,
                    allocated_kL=demand,
                    deficit_kL=0.0,
                    coverage_pct=100.0,
                    stress_after=15.0
                ))
            allocated_so_far = total_demand
        else:
            # Water deficit: distribute based on priority & proportional allocation
            remaining_budget = budget
            # First pass: give priority 3 (critical) full or up to 90%
            pass1 = {}
            for p in sorted_plots:
                pid = str(getattr(p, 'id', p.get('id', 'P-?')))
                priority = int(getattr(p, 'priority', 1) if hasattr(p, 'priority') else p.get('priority', 1))
                demand = float(getattr(p, 'base_demand', p.get('base_demand', 8.0)))
                weight = 1.0 if priority == 3 else (0.75 if priority == 2 else 0.5)
                target = min(demand, demand * weight)
                pass1[pid] = target

            pass1_tot = sum(pass1.values())
            scale = remaining_budget / pass1_tot if pass1_tot > 0 else 0

            for p in sorted_plots:
                pid = str(getattr(p, 'id', p.get('id', 'P-?')))
                name = str(getattr(p, 'name', p.get('name', 'Plot')))
                crop = str(getattr(p, 'crop', p.get('crop', 'Crop')))
                demand = float(getattr(p, 'base_demand', p.get('base_demand', 8.0)))
                
                alloc = round(min(demand, pass1[pid] * scale), 1)
                deficit = round(max(0.0, demand - alloc), 1)
                cov = round((alloc / demand * 100.0) if demand > 0 else 100.0, 1)
                stress_after = round(max(10.0, 75.0 - (cov * 0.65)), 1)

                allocations.append(PlotAllocation(
                    plot_id=pid,
                    name=name,
                    crop=crop,
                    demand_kL=demand,
                    allocated_kL=alloc,
                    deficit_kL=deficit,
                    coverage_pct=cov,
                    stress_after=stress_after
                ))
                allocated_so_far += alloc

        unmet = round(max(0.0, total_demand - allocated_so_far), 1)
        feasible = (allocated_so_far <= budget + 0.1)
        efficiency = round(min(100.0, (allocated_so_far / total_demand) * 100.0) if total_demand > 0 else 100.0, 1)

        summary = f"Allocated {allocated_so_far:.1f} kL of {budget:.1f} kL budget across {len(plots)} plots. Demand coverage: {efficiency}%."

        return IrrigationOptimizeResponse(
            allocations=allocations,
            total_water=round(allocated_so_far, 1),
            total_demand=round(total_demand, 1),
            unmet_demand=unmet,
            feasible=feasible,
            efficiency_score=efficiency,
            summary=summary
        )
