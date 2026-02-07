from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import json

class SitePrioritizer:
    """Identifie les stations énergivores prioritaires"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=3, random_state=42)
        self.config = {
            "algorithm": "KMeans_Clustering",
            "n_clusters": 3,
            "features": ["power_consumption", "specific_consumption", "efficiency"]
        }
    
    def analyze_sites(self, df):
        """Analyse et classe les stations par priorité"""
        print("🎯 Analyse des sites...")
        
        # Calculer métriques par station
        stats = df.groupby('station').agg({
            'power_consumption_kw': 'mean',
            'water_demand_m3h': 'mean',
            'efficiency': 'mean'
        }).reset_index()
        
        # Consommation spécifique (kWh/m³) = indicateur clé
        stats['specific_consumption'] = (
            stats['power_consumption_kw'] / stats['water_demand_m3h']
        )
        
        # Normaliser pour clustering
        X = self.scaler.fit_transform(
            stats[['power_consumption_kw', 'specific_consumption']]
        )
        
        # Clustering
        stats['cluster'] = self.model.fit_predict(X)
        
        # Labelliser clusters (du pire au meilleur)
        cluster_scores = stats.groupby('cluster')['specific_consumption'].mean()
        sorted_clusters = cluster_scores.sort_values(ascending=False)
        
        priority_map = {}
        for i, cluster in enumerate(sorted_clusters.index):
            if i == 0:
                priority_map[cluster] = 'CRITIQUE_intervention_urgente'
            elif i == 1:
                priority_map[cluster] = 'MOYEN_optimisation_recommandée'
            else:
                priority_map[cluster] = 'BON_performance_optimale'
        
        stats['priority'] = stats['cluster'].map(priority_map)
        
        # Calcul économies potentielles
        best_specific = stats['specific_consumption'].min()
        stats['potential_savings_pct'] = (
            (stats['specific_consumption'] - best_specific) / 
            stats['specific_consumption'] * 100
        )
        
        # Tri par priorité
        stats = stats.sort_values('specific_consumption', ascending=False)
        
        return stats[['station', 'power_consumption_kw', 'specific_consumption', 
                     'efficiency', 'priority', 'potential_savings_pct']]
    
    def save_config(self, path):
        """Sauvegarde configuration"""
        import os
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/clustering_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

# TEST
if __name__ == "__main__":
    print("="*60)
    print("MODULE 4: PRIORISATION DES SITES")
    print("="*60)
    
    # Charger données
    df = pd.read_csv('data/raw/onea_historical_data.csv', 
                     parse_dates=['timestamp'])
    
    # Analyser
    prioritizer = SitePrioritizer()
    results = prioritizer.analyze_sites(df)
    
    print("\n🎯 CLASSEMENT DES STATIONS:\n")
    print(results.to_string(index=False))
    
    # Interpréter
    print("\n📊 INTERPRÉTATION:")
    for _, row in results.iterrows():
        print(f"\n{row['station']}:")
        print(f"  Priorité: {row['priority']}")
        print(f"  Conso spécifique: {row['specific_consumption']:.3f} kWh/m³")
        print(f"  Économies potentielles: {row['potential_savings_pct']:.1f}%")
    
    # Sauvegarder
    import os
    os.makedirs('models/clustering', exist_ok=True)
    results.to_csv('models/clustering/site_priorities.csv', index=False)
    prioritizer.save_config('models/clustering')
    
    print("\n✅ Analyse terminée et sauvegardée")