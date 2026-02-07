import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_onea_data(station_name, start_date, days=365):
    """
    Génère des données synthétiques réalistes pour une station ONEA
    
    Patterns réalistes:
    - Consommation eau pics: 6h-9h (matin), 18h-21h (soir)
    - Consommation électrique corrélée à pompage
    - Variations saisonnières (saison sèche vs pluies)
    - Jours de marché (hausse demande)
    - Impact température
    """
    
    dates = pd.date_range(start=start_date, periods=days*24, freq='H')
    
    # Paramètres de base
    base_demand = 150  # m3/h moyen
    base_power = 45    # kW moyen
    
    data = []
    
    for i, dt in enumerate(dates):
        hour = dt.hour
        day_of_week = dt.dayofweek
        month = dt.month
        
        # Pattern horaire (pics matin/soir)
        if 6 <= hour <= 9:
            hour_multiplier = 1.4
        elif 18 <= hour <= 21:
            hour_multiplier = 1.3
        elif 0 <= hour <= 5:
            hour_multiplier = 0.6
        else:
            hour_multiplier = 1.0
        
        # Pattern saisonnier (saison sèche: Nov-Mai)
        if month in [11, 12, 1, 2, 3, 4, 5]:
            seasonal_multiplier = 1.2  # Plus de demande
        else:
            seasonal_multiplier = 0.9
        
        # Jours de marché (mercredi, vendredi au Burkina)
        if day_of_week in [2, 4]:  # Mercredi=2, Vendredi=4
            market_multiplier = 1.15
        else:
            market_multiplier = 1.0
        
        # Température simulée (impact demande)
        temp_base = 30 if month in [3, 4, 5] else 25
        temperature = temp_base + np.random.normal(0, 3)
        temp_multiplier = 1 + (temperature - 25) * 0.01
        
        # Calcul demande finale
        demand = base_demand * hour_multiplier * seasonal_multiplier * market_multiplier * temp_multiplier
        demand += np.random.normal(0, 10)  # Bruit
        demand = max(0, demand)
        
        # Calcul consommation électrique
        # Relation: kW ≈ (m3/h * hauteur_manométrique) / rendement_pompe
        # Supposons rendement 65%, HMT 50m
        efficiency = 0.65 + np.random.normal(0, 0.05)
        efficiency = np.clip(efficiency, 0.5, 0.8)
        
        power = (demand * 50 * 9.81) / (3600 * efficiency * 1000)  # kW
        power += np.random.normal(0, 2)
        power = max(0, power)
        
        # Tarif électrique (simplifié BF: heures pleines/creuses)
        if 22 <= hour or hour < 6:
            tariff = 65  # FCFA/kWh heures creuses
        elif 18 <= hour <= 22:
            tariff = 95  # FCFA/kWh heures pointe
        else:
            tariff = 80  # FCFA/kWh heures pleines
        
        # Niveau réservoir (simulation simple)
        reservoir_capacity = 500  # m3
        # Variation basée sur balance demande/production
        reservoir_level = reservoir_capacity * (0.4 + 0.3 * np.sin(i / 24 * 2 * np.pi))
        
        data.append({
            'timestamp': dt,
            'station': station_name,
            'water_demand_m3h': round(demand, 2),
            'power_consumption_kw': round(power, 2),
            'electricity_tariff_fcfa_kwh': tariff,
            'temperature_celsius': round(temperature, 1),
            'reservoir_level_m3': round(reservoir_level, 1),
            'reservoir_capacity_m3': reservoir_capacity,
            'is_market_day': 1 if day_of_week in [2, 4] else 0,
            'efficiency': round(efficiency, 3)
        })
    
    return pd.DataFrame(data)

# Génération pour 3 stations
print("Génération données Station Ouaga A...")
df_ouaga_a = generate_onea_data('Ouaga_Station_A', '2025-01-01', days=365)

print("Génération données Station Ouaga B...")
# Station B: plus petite, plus énergivore (pompes vieilles)
df_ouaga_b = generate_onea_data('Ouaga_Station_B', '2025-01-01', days=365)
df_ouaga_b['power_consumption_kw'] *= 1.3  # Moins efficace
df_ouaga_b['water_demand_m3h'] *= 0.7  # Plus petite

print("Génération données Station Bobo...")
df_bobo = generate_onea_data('Bobo_Station_C', '2025-01-01', days=365)
df_bobo['water_demand_m3h'] *= 1.1  # Légèrement plus grande

# Combiner toutes les stations
df_all = pd.concat([df_ouaga_a, df_ouaga_b, df_bobo], ignore_index=True)

# Sauvegarder
df_all.to_csv('data/raw/onea_historical_data.csv', index=False)
df_ouaga_a.to_csv('data/raw/ouaga_station_A.csv', index=False)
df_ouaga_b.to_csv('data/raw/ouaga_station_B.csv', index=False)
df_bobo.to_csv('data/raw/bobo_station_C.csv', index=False)

print(f"✅ Données générées: {len(df_all)} enregistrements")
print(f"📊 Période: {df_all['timestamp'].min()} à {df_all['timestamp'].max()}")
print(f"🏭 Stations: {df_all['station'].unique()}")

# Statistiques rapides
print("\n📈 Statistiques par station:")
print(df_all.groupby('station').agg({
    'water_demand_m3h': 'mean',
    'power_consumption_kw': 'mean',
    'efficiency': 'mean'
}).round(2))