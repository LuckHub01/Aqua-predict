import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
import json
from utils import create_time_features

class DemandForecaster:
    """Prévision de demande en eau avec Prophet"""
    
    def __init__(self, station_name):
        self.station_name = station_name
        self.model = None
        self.config = {
            "algorithm": "Prophet",
            "version": "1.1.4",
            "station": station_name,
            "forecast_horizon": "24h",
            "features": [
                "historical_demand",
                "temperature",
                "hour_of_day",
                "day_of_week",
                "is_market_day",
                "seasonality"
            ],
            "hyperparameters": {
                "changepoint_prior_scale": 0.05,
                "seasonality_prior_scale": 10,
                "seasonality_mode": "multiplicative",
                "daily_seasonality": True,
                "weekly_seasonality": True,
                "yearly_seasonality": True
            }
        }
    
    def prepare_data(self, df):
        """Prépare données pour Prophet (format ds, y)"""
        prophet_df = df[['timestamp', 'water_demand_m3h']].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Ajouter regresseurs externes
        prophet_df['temperature'] = df['temperature_celsius'].values
        prophet_df['is_market_day'] = df['is_market_day'].values
        
        return prophet_df
    
    def train(self, df):
        """Entraîne le modèle"""
        print(f"🚀 Entraînement modèle pour {self.station_name}...")
        
        prophet_df = self.prepare_data(df)
        
        # Initialiser Prophet
        self.model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            seasonality_mode='multiplicative',
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        
        # Ajouter regresseurs
        self.model.add_regressor('temperature')
        self.model.add_regressor('is_market_day')
        
        # Entraîner
        self.model.fit(prophet_df)
        
        print("✅ Entraînement terminé")
        
    def forecast(self, periods=24):
        """Prévision à H+periods heures"""
        future = self.model.make_future_dataframe(periods=periods, freq='H')
        
        # Ajouter regresseurs pour futur (valeurs moyennes)
        future['temperature'] = 30  # Température moyenne
        future['is_market_day'] = 0  # Par défaut non
        
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    
    def save(self, path):
        """Sauvegarde modèle + config"""
        joblib.dump(self.model, f"{path}/{self.station_name}_prophet.pkl")
        with open(f"{path}/{self.station_name}_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"💾 Modèle sauvegardé: {path}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Charger données
    df = pd.read_csv('data/raw/bobo_station_C.csv', parse_dates=['timestamp'])
    
    # Train sur 90% des données
    split_idx = int(len(df) * 0.9)
    train_df = df[:split_idx]
    test_df = df[split_idx:]
    
    # Entraîner
    forecaster = DemandForecaster('Bobo_Station_C')
    forecaster.train(train_df)
    
    # Prévision 24h
    forecast = forecaster.forecast(periods=24)
    print("\n📊 Prévisions prochaines 24h:")
    print(forecast.head(10))
    
    # Évaluation
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    
    # Comparer avec données test
    actual = test_df['water_demand_m3h'][:24].values
    predicted = forecast['yhat'].values
    
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    
    print(f"\n📈 Performance:")
    print(f"   MAE: {mae:.2f} m3/h")
    print(f"   RMSE: {rmse:.2f} m3/h")
    print(f"   MAPE: {mape:.2f}%")
    
    # Sauvegarder
    forecaster.save('models/demand_forecasting')