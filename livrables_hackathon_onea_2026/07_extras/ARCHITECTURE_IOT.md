# 🔌 ARCHITECTURE IoT - AQUA-PREDICT Phase 2

## Vue d'ensemble
```
┌─────────────────────────────────────────────────────────────────┐
│                     COUCHE TERRAIN (FIELD LAYER)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   CAPTEURS   │  │   CAPTEURS   │  │   CAPTEURS   │         │
│  │              │  │              │  │              │         │
│  │ • Niveau     │  │ • Débit      │  │ • Puissance  │         │
│  │   Réservoir  │  │   Pompe      │  │   Électrique │         │
│  │ • Pression   │  │ • Vibration  │  │ • Tension    │         │
│  │              │  │              │  │ • Courant    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼────────┐                          │
│                    │  GATEWAY IoT   │                          │
│                    │  (LoRaWAN)     │                          │
│                    └───────┬────────┘                          │
└────────────────────────────┼─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│              COUCHE COMMUNICATION (EDGE LAYER)                │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│                    ┌─────────────────┐                       │
│                    │  MQTT BROKER    │                       │
│                    │  (Mosquitto)    │                       │
│                    └────────┬────────┘                       │
│                             │                                 │
└─────────────────────────────┼─────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                COUCHE INTELLIGENCE (CLOUD/EDGE)               │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              AQUA-PREDICT ENGINE                       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │   Prophet   │  │    PuLP     │  │  Isolation   │  │  │
│  │  │  Forecaster │  │ Optimizer   │  │   Forest     │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  │  │
│  │         │                 │                 │          │  │
│  │         └─────────────────┴─────────────────┘          │  │
│  │                           │                             │  │
│  │                  ┌────────▼────────┐                   │  │
│  │                  │  DECISION       │                   │  │
│  │                  │  ENGINE         │                   │  │
│  │                  └────────┬────────┘                   │  │
│  └───────────────────────────┼──────────────────────────┘  │
│                               │                              │
└───────────────────────────────┼──────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────┐
│                COUCHE CONTRÔLE (ACTUATION)                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  CONTRÔLEUR     │  │  CONTRÔLEUR     │                   │
│  │  POMPE 1        │  │  POMPE 2        │                   │
│  │                 │  │                 │                   │
│  │ • ON/OFF        │  │ • ON/OFF        │                   │
│  │ • Variateur     │  │ • Variateur     │                   │
│  │   vitesse       │  │   vitesse       │                   │
│  └─────────────────┘  └─────────────────┘                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Composants détaillés

### 1. Capteurs terrain

#### **A. Capteurs niveau réservoir**
- **Type :** Ultrason ou Pression hydrostatique
- **Modèle recommandé :** Siemens Sitrans LU150 ou équivalent
- **Précision :** ±0.5%
- **Communication :** 4-20mA ou Modbus RTU
- **Prix unitaire :** ~150,000 FCFA
- **Nombre requis :** 1 par réservoir (3 total)

#### **B. Capteurs débit pompe**
- **Type :** Électromagnétique
- **Modèle recommandé :** Endress+Hauser Promag ou équivalent
- **Précision :** ±0.2%
- **Communication :** 4-20mA ou Modbus RTU
- **Prix unitaire :** ~300,000 FCFA
- **Nombre requis :** 1 par pompe (6 total si 2 pompes/station)

#### **C. Compteurs énergie**
- **Type :** Analyseur réseau triphasé
- **Modèle recommandé :** Schneider PM5000 ou équivalent
- **Mesures :** kW, kWh, PF, THD
- **Communication :** Modbus TCP/RTU
- **Prix unitaire :** ~400,000 FCFA
- **Nombre requis :** 1 par station (3 total)

### 2. Gateway IoT

#### **Caractéristiques**
- **Technologie :** LoRaWAN (longue portée, faible consommation)
- **Alternative :** 4G/LTE (si couverture réseau)
- **Modèle recommandé :** 
  - Multitech Conduit ou
  - Kerlink Wirnet Station
- **Prix unitaire :** ~500,000 FCFA
- **Nombre requis :** 1 par site (2-3 total selon distance)

#### **Fonctions**
- Collecte données capteurs
- Conversion protocoles (Modbus → MQTT)
- Buffer local si perte connexion
- Transmission cloud

### 3. MQTT Broker

#### **Configuration**
```yaml
# docker-compose.yml
version: '3'
services:
  mosquitto:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./data:/mosquitto/data
      - ./log:/mosquitto/log
```

#### **Topics MQTT**
```
onea/ouaga_a/reservoir/level      → Niveau réservoir (%)
onea/ouaga_a/pump/flow            → Débit pompe (m³/h)
onea/ouaga_a/energy/power         → Puissance (kW)
onea/ouaga_a/energy/total         → Énergie cumulée (kWh)

onea/ouaga_a/control/pump/cmd     → Commandes pompe
onea/ouaga_a/control/pump/status  → État pompe
```

### 4. Module Contrôle Temps Réel

#### **Code Python : `src/iot_controller.py`**
```python
import paho.mqtt.client as mqtt
import json
from datetime import datetime

class RealTimeController:
    """Contrôleur temps réel pompes"""
    
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker_host, broker_port, 60)
        
        # État système
        self.reservoir_levels = {}
        self.pump_status = {}
        self.power_consumption = {}
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connecté MQTT avec code {rc}")
        # S'abonner à tous les topics
        client.subscribe("onea/#")
    
    def on_message(self, client, userdata, msg):
        """Traiter messages entrants"""
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        # Parser topic
        parts = topic.split('/')
        station = parts[1]
        sensor_type = parts[2]
        
        # Mettre à jour état
        if sensor_type == "reservoir":
            self.reservoir_levels[station] = payload['level']
            self.evaluate_pumping_decision(station)
        
        elif sensor_type == "energy":
            self.power_consumption[station] = payload['power']
            self.detect_anomaly(station, payload['power'])
    
    def evaluate_pumping_decision(self, station):
        """Décision intelligente pompage"""
        
        level = self.reservoir_levels.get(station, 50)
        hour = datetime.now().hour
        
        # Règles décision
        if level < 20:
            # URGENT - pomper immédiatement
            self.send_pump_command(station, "ON", power=100)
            print(f"🔴 URGENT: Pompage {station} activé (niveau {level}%)")
        
        elif level < 60 and (22 <= hour or hour < 6):
            # Opportunité heures creuses
            self.send_pump_command(station, "ON", power=80)
            print(f"🌙 Pompage {station} heures creuses (niveau {level}%)")
        
        elif 18 <= hour < 22 and level > 40:
            # Heures pointe - arrêter si possible
            self.send_pump_command(station, "OFF")
            print(f"⛔ Arrêt {station} heures pointe (niveau {level}%)")
        
        elif level > 85:
            # Réservoir plein
            self.send_pump_command(station, "OFF")
            print(f"✅ Arrêt {station} réservoir plein ({level}%)")
    
    def send_pump_command(self, station, action, power=100):
        """Envoyer commande pompe"""
        
        command = {
            "action": action,
            "power_percent": power,
            "timestamp": datetime.now().isoformat(),
            "source": "AQUA-PREDICT_AI"
        }
        
        topic = f"onea/{station}/control/pump/cmd"
        self.client.publish(topic, json.dumps(command))
    
    def detect_anomaly(self, station, power):
        """Détection anomalie temps réel"""
        
        # Charger modèle Isolation Forest
        from joblib import load
        model = load('models/anomaly_detection/anomaly_detector.pkl')
        
        # TODO: Prédire si anomalie
        # Si anomalie → Alert
        pass
    
    def start(self):
        """Démarrer boucle"""
        self.client.loop_forever()

# Lancement
if __name__ == "__main__":
    controller = RealTimeController()
    controller.start()
```

## Matériel recommandé

### Budget estimatif

| Composant | Quantité | Prix unitaire | Total |
|-----------|----------|---------------|-------|
| Capteurs niveau | 3 | 150,000 | 450,000 |
| Capteurs débit | 6 | 300,000 | 1,800,000 |
| Compteurs énergie | 3 | 400,000 | 1,200,000 |
| Gateway LoRaWAN | 2 | 500,000 | 1,000,000 |
| Contrôleurs pompe | 6 | 200,000 | 1,200,000 |
| Serveur Edge | 1 | 1,500,000 | 1,500,000 |
| Installation | - | - | 2,000,000 |
| **TOTAL** | - | - | **9,150,000 FCFA** |

### ROI
```
Coût infrastructure : 9,150,000 FCFA
Économies annuelles : 122,000,000 FCFA
ROI : 9.15 / 122 = 0.075 an = 27 jours

→ Rentabilité en MOINS D'1 MOIS ! 🚀
```

## Fournisseurs locaux

### Burkina Faso
- **Électronique :** SOBEDIS (Ouagadougou)
- **Instrumentation :** CFAO Technologies
- **Installation :** SIFA (Société Industrielle Faso)

### International (import)
- **Siemens Burkina Faso** (capteurs industriels)
- **Schneider Electric Ouagadougou** (compteurs énergie)
- **Distributeurs agrées LoRaWAN** (via Côte d'Ivoire)

## Déploiement progressif

### Phase 1 (Mois 1-2) : Pilote
- 1 station (Ouaga_A)
- Capteurs essentiels (niveau + énergie)
- Dashboard monitoring
- **Coût : 3M FCFA**

### Phase 2 (Mois 3-4) : Extension
- 2 autres stations
- Contrôle automatique
- **Coût : 6M FCFA**

### Phase 3 (Mois 5-6) : Optimisation
- Machine learning avancé
- Prévision J+14
- **Coût : 500K FCFA (formation)**

## Maintenance

### Coûts annuels
- Abonnement cloud (si utilisé) : 500,000 FCFA
- Calibration capteurs : 200,000 FCFA
- Support technique : 1,000,000 FCFA
- **TOTAL : 1,700,000 FCFA/an**

### Comparé aux économies : 122M FCFA/an
**Rapport coût/bénéfice : 1:72** 🎯