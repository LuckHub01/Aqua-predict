
# GUIDE IMPLÉMENTATION - AQUA-PREDICT

## Installation

### Prérequis
- Python 3.9+
- pip
- 4GB RAM minimum
- 10GB espace disque

### Étapes installation

1. **Créer environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

2. **Installer dépendances**
```bash
pip install -r requirements.txt
```

3. **Générer données (si test)**
```bash
python src/1_data_generation.py
```

4. **Entraîner modèles**
```bash
python src/2_demand_forecasting.py
python src/4_site_prioritization.py
python src/5_anomaly_detection.py
```

5. **Lancer dashboard**
```bash
streamlit run src/7_dashboard.py
```

## Configuration

### Adapter aux données ONEA réelles

Modifier `src/1_data_generation.py`:
```python
# Remplacer par vraies données
df = pd.read_csv('donnees_onea_reelles.csv')
```

### Tarifs électricité

Vérifier `src/3_optimization_engine.py`:
```python
def get_tariff(hour):
    # Adapter selon tarifs SONABEL actuels
    if 22 <= hour or hour < 6:
        return 65  # Heures creuses
    # ...
```

## Utilisation quotidienne

### 1. Consulter prévisions
- Ouvrir dashboard
- Page "Prévisions & Recommandations"
- Sélectionner station
- Analyser pics prévus

### 2. Suivre recommandations
- Consulter section recommandations
- Prioriser actions HAUTE
- Planifier interventions MOYENNE
- Monitorer actions BASSE

### 3. Surveiller anomalies
- Page "Anomalies"
- Vérifier nouvelles détections
- Investiguer fuites signalées

## Maintenance

### Hebdomadaire
- Vérifier données collectées
- Valider prévisions vs réel
- Ajuster si dérives

### Mensuelle
- Réentraîner Prophet
- Mettre à jour clustering
- Analyser performance

### Trimestrielle
- Audit complet modèles
- Optimisation hyperparamètres
- Rapport économies réalisées

## Support

Contact: inaparehub@gmail.com

