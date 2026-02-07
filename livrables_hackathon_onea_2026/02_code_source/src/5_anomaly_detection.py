from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
import json
import joblib

class AnomalyDetector:
    """Détecte les anomalies énergétiques (fuites, pannes)"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,  # 5% données anormales
            random_state=42
        )
        self.config = {
            "algorithm": "Isolation_Forest",
            "contamination": 0.05,
            "features": ["power_consumption", "efficiency", "specific_consumption"]
        }
    
    def train(self, df):
        """Entraîne sur données normales"""
        print("🚀 Entraînement détecteur anomalies...")
        
        # Features
        df['specific_consumption'] = (
            df['power_consumption_kw'] / df['water_demand_m3h']
        )
        
        X = df[['power_consumption_kw', 'efficiency', 
                'specific_consumption']].values
        
        self.model.fit(X)
        print("✅ Entraînement terminé")
    
    def detect(self, df):
        """Détecte anomalies dans nouvelles données"""
        # Features
        df = df.copy()
        df['specific_consumption'] = (
            df['power_consumption_kw'] / df['water_demand_m3h']
        )
        
        X = df[['power_consumption_kw', 'efficiency', 
                'specific_consumption']].values
        
        # Prédiction (-1 = anomalie, 1 = normal)
        predictions = self.model.predict(X)
        scores = self.model.score_samples(X)
        
        df['is_anomaly'] = (predictions == -1).astype(int)
        df['anomaly_score'] = scores
        
        # Classifier types d'anomalies
        anomalies = df[df['is_anomaly'] == 1].copy()
        
        if len(anomalies) > 0:
            anomalies['anomaly_type'] = 'unknown'
            
            # Efficacité basse
            mask_eff = anomalies['efficiency'] < 0.55
            anomalies.loc[mask_eff, 'anomaly_type'] = 'efficiency_drop_maintenance_needed'
            
            # Surconsommation
            mask_power = (anomalies['power_consumption_kw'] > 
                         df['power_consumption_kw'].quantile(0.95))
            anomalies.loc[mask_power, 'anomaly_type'] = 'power_spike_check_equipment'
            
            # Fuite potentielle (haute conso, faible efficacité)
            mask_leak = ((anomalies['specific_consumption'] > 
                         df['specific_consumption'].quantile(0.9)) & 
                        (anomalies['efficiency'] < 0.6))
            anomalies.loc[mask_leak, 'anomaly_type'] = 'potential_leak_inspect_network'
        
        return anomalies[['timestamp', 'station', 'anomaly_type', 
                         'power_consumption_kw', 'efficiency', 
                         'specific_consumption', 'anomaly_score']]
    
    def save(self, path):
        """Sauvegarde modèle"""
        import os
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model, f"{path}/anomaly_detector.pkl")
        with open(f"{path}/anomaly_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

# TEST
if __name__ == "__main__":
    print("="*60)
    print("MODULE 5: DÉTECTION ANOMALIES")
    print("="*60)
    
    # Charger données
    df = pd.read_csv('data/raw/onea_historical_data.csv', 
                     parse_dates=['timestamp'])
    
    # Split train/test
    split = int(len(df) * 0.8)
    train_df = df[:split]
    test_df = df[split:]
    
    # Entraîner
    detector = AnomalyDetector()
    detector.train(train_df)
    
    # Détecter anomalies
    anomalies = detector.detect(test_df)
    
    print(f"\n🚨 {len(anomalies)} anomalies détectées sur {len(test_df)} enregistrements")
    print(f"   Taux: {len(anomalies)/len(test_df)*100:.2f}%\n")
    
    if len(anomalies) > 0:
        print("📋 ANOMALIES PAR TYPE:")
        print(anomalies['anomaly_type'].value_counts())
        
        print("\n🔍 EXEMPLES D'ANOMALIES:\n")
        print(anomalies.head(10).to_string(index=False))
    
    # Sauvegarder
    import os
    os.makedirs('models/anomaly_detection', exist_ok=True)
    anomalies.to_csv('models/anomaly_detection/detected_anomalies.csv', index=False)
    detector.save('models/anomaly_detection')
    
    print("\n✅ Détection terminée et sauvegardée")