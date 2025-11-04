# 🚀 Commandes Rapides - CityFlow Analytics

## Installation et Exécution

### 🌟 Option 1 : Pipeline Complet (Recommandé)

```bash
# Lance traitement + rapport en une seule commande
python3 main.py

# Ou pour une date spécifique
python3 main.py 2025-11-03
```

### 🔧 Option 2 : Exécution Manuelle (Étape par étape)

```bash
# 1. Traiter les données
python3 processors/main.py

# 2. Générer le rapport
python3 report_generator/main.py

# 3. Vérification résultats
ls -la output/reports/
```

### 🤖 Option 3 : Script Shell Automatique

```bash
# Setup + traitement complet
./setup_and_run.sh
```

---

## 🌐 Option 4 : API REST (Exposition des métriques)

```bash
# Démarrer l'API locale (port 5001 par défaut, évite conflit AirPlay)
python3 api/local_server.py

# Ou avec un port personnalisé
API_PORT=8080 python3 api/local_server.py

# Dans un autre terminal, tester
curl http://localhost:5001/health
curl http://localhost:5001/metrics/bikes/2025-11-03
curl http://localhost:5001/report/2025-11-03
```

---

## 📋 Commandes Détaillées

### Installation

```bash
# Créer environnement virtuel (optionnel)
python3 -m venv venv
source venv/bin/activate

# Installer dépendances (optionnel)
pip install -r requirements.txt
```

### Validation

```bash
# Suite de tests complète
python3 run_tests.py

# Test import unique
python3 -c "from processors import BikesProcessor; print('OK')"
```

### Exécution

```bash
# Traitement complet
python3 main.py
```

### Vérification

```bash
# Voir rapports générés
ls -lh output/reports/

# Afficher résumé rapport
python3 -c "
import json
from datetime import datetime
date = datetime.now().strftime('%Y-%m-%d')
with open(f'output/reports/daily_report_{date}.json') as f:
    r = json.load(f)
print('Summary:', r['summary'])
"
```

---

## 🔍 Commandes de Diagnostic

```bash
# Vérifier structure
ls -la processors/ utils/ models/ config/

# Vérifier Python
python3 --version

# Vérifier chemins config
python3 -c "from config import settings; print(settings.BATCH_DATA_PATH)"

# Tester un processeur
python3 -c "
from processors import WeatherProcessor
p = WeatherProcessor()
result = p.process({'days': [{'datetime': '2025-11-03', 'tempmax': 15, 'tempmin': 10, 'temp': 12.5, 'precip': 0, 'windspeed': 10, 'conditions': 'Clear'}]})
print('Success:', result['success'])
"
```

---

## 🧹 Nettoyage

```bash
# Supprimer fichiers temporaires (garder outputs)
rm -rf output/processed/*.csv 2>/dev/null || true

# Supprimer environnement virtuel
rm -rf venv/

# Garder seulement les rapports (supprimer métriques intermédiaires)
# rm -rf output/metrics/
```

