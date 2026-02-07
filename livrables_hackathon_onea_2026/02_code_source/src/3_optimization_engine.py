import pandas as pd
import numpy as np
from pulp import *
import json
import joblib

class PumpingOptimizer:
    def __init__(self, stations_config):
        self.stations = stations_config
        self.config = {
            "algorithm": "Linear_Programming",
            "solver": "CBC",
            "objective": "minimize_electricity_cost",
            "horizon": "24h"
        }
    
    def optimize_24h(self, forecasts, tariffs):
        """
        forecasts: dict {station: [demandes 24h]}
        tariffs: list de 24 tarifs
        """
        hours = range(24)
        stations = list(self.stations.keys())
        
        prob = LpProblem("ONEA_Optimization", LpMinimize)
        
        # Variables: pompage par station/heure
        pump = LpVariable.dicts("pump", 
                               ((s, h) for s in stations for h in hours),
                               lowBound=0)
        
        # Variables: niveau réservoir
        level = LpVariable.dicts("level",
                                ((s, h) for s in stations for h in hours),
                                lowBound=0)
        
        # OBJECTIF: Minimiser coût
        prob += lpSum([
            pump[s, h] * self.stations[s]['power_per_m3'] * tariffs[h]
            for s in stations for h in hours
        ])
        
        # CONTRAINTES
        for s in stations:
            cfg = self.stations[s]
            for h in hours:
                # Équation réservoir
                if h == 0:
                    prev_level = cfg['reservoir_initial']
                else:
                    prev_level = level[s, h-1]
                
                prob += (level[s, h] == prev_level + 
                        pump[s, h] - forecasts[s][h])
                
                # Limites réservoir
                prob += level[s, h] >= cfg['reservoir_capacity'] * 0.2
                prob += level[s, h] <= cfg['reservoir_capacity'] * 0.95
                
                # Limite pompage
                prob += pump[s, h] <= cfg['max_pump_capacity']
        
        # RÉSOLUTION
        solver = PULP_CBC_CMD(msg=0)
        prob.solve(solver)
        
        # RÉSULTATS
        schedule = {}
        costs = {}
        for s in stations:
            schedule[s] = [value(pump[s, h]) for h in hours]
            costs[s] = sum([value(pump[s, h]) * 
                           self.stations[s]['power_per_m3'] * 
                           tariffs[h] for h in hours])
        
        total_cost = value(prob.objective)
        
        # Calcul coût baseline (pomper selon demande)
        baseline_cost = sum([
            forecasts[s][h] * self.stations[s]['power_per_m3'] * tariffs[h]
            for s in stations for h in hours
        ])
        
        savings = baseline_cost - total_cost
        
        return {
            'schedule': schedule,
            'cost_optimized': total_cost,
            'cost_baseline': baseline_cost,
            'savings': savings,
            'savings_pct': (savings/baseline_cost)*100,
            'costs_by_station': costs
        }
    
    def save_config(self, path):
        with open(f"{path}/optimization_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

# TEST
if __name__ == "__main__":
    # Config stations
    stations_config = {
        'Ouaga_A': {
            'power_per_m3': 0.3,  # kWh/m3
            'reservoir_capacity': 3000,
            'reservoir_initial': 1800,
            'max_pump_capacity': 250
        },
        'Ouaga_B': {
            'power_per_m3': 0.35,
            'reservoir_capacity': 2000,
            'reservoir_initial': 1200,
            'max_pump_capacity': 180
        }
    }
    
    # Prévisions (simulées)
    forecasts = {
        'Ouaga_A': [120]*6 + [180]*6 + [150]*6 + [180]*6,
        'Ouaga_B': [80]*6 + [120]*6 + [100]*6 + [120]*6
    }
    
    # Tarifs (heures creuses/pleines/pointe)
    tariffs = [65]*6 + [80]*12 + [95]*4 + [65]*2
    
    # Optimisation
    optimizer = PumpingOptimizer(stations_config)
    results = optimizer.optimize_24h(forecasts, tariffs)
    
    print(f"\n💰 Coût optimisé: {results['cost_optimized']:,.0f} FCFA")
    print(f"💰 Coût baseline: {results['cost_baseline']:,.0f} FCFA")
    print(f"📉 Économies: {results['savings']:,.0f} FCFA ({results['savings_pct']:.1f}%)")
    
    print("\n📅 Planning optimisé (m³/h par heure):")
    for station, schedule in results['schedule'].items():
        print(f"{station}: {[round(x,1) for x in schedule[:12]]}")
    
    optimizer.save_config('models/optimization')