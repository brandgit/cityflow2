# Guide de Test - CityFlow Analytics

## 🔍 Étapes de Test

### Étape 1 : Vérification de l'Environnement

```bash
# 1. Vérifier que vous êtes dans le bon répertoire
pwd
# Doit afficher: .../cityflow

# 2. Vérifier la structure des répertoires
ls -la processors/ utils/ models/ config/

# 3. Vérifier que Python 3 est installé
python3 --version
# Doit afficher: Python 3.x.x
```

### Étape 2 : Test des Imports (Vérification Syntaxe)

```bash
# Test import des modules principaux
python3 -c "from processors import BikesProcessor; print('✓ Processors OK')"
python3 -c "from utils import validators; print('✓ Utils OK')"
python3 -c "from models import TrafficMetrics; print('✓ Models OK')"
python3 -c "from config import settings; print('✓ Config OK')"
```

**Résultat attendu** : Tous les imports doivent fonctionner sans erreur

### Étape 3 : Test de la Configuration

```bash
# Test chargement configuration
python3 -c "
from config import settings
print('✓ Chemin batch:', settings.BATCH_DATA_PATH)
print('✓ Chemin API:', settings.API_DATA_PATH)
print('✓ Taille chunk:', settings.CHUNK_SIZE)
print('✓ Configuration chargée avec succès')
"
```

### Étape 4 : Test des Utilitaires Individuels

Créer un fichier de test : `test_utils.py`

```python
# test_utils.py
from utils.validators import validate_coordinates, validate_date_iso
from utils.aggregators import calculate_daily_total
from utils.geo_utils import calculate_line_length

# Test validation coordonnées
assert validate_coordinates(2.3522, 48.8566) == True  # Paris
assert validate_coordinates(200, 100) == False  # Invalide

# Test validation date
date_valid = validate_date_iso("2025-11-03T02:00:00+01:00")
assert date_valid is not None

# Test agrégation
test_data = [{"count": 10}, {"count": 20}, {"count": 30}]
total = calculate_daily_total(test_data, "count")
assert total == 60.0

print("✓ Tous les tests utilitaires passés")
```

Exécuter :
```bash
python3 test_utils.py
```

### Étape 5 : Test d'un Processeur Simple (Weather)

Créer un fichier : `test_weather.py`

```python
# test_weather.py
from processors import WeatherProcessor
from utils.file_utils import load_json
from config import settings

# Charger données test
weather_data = load_json("path/to/weather.json")  # Si disponible
# OU créer données test minimales
weather_data = {
    "days": [{
        "datetime": "2025-11-03",
        "tempmax": 15.6,
        "tempmin": 7.3,
        "temp": 11.6,
        "precip": 0.0,
        "windspeed": 15.5,
        "conditions": "Partially cloudy"
    }]
}

# Initialiser processeur
processor = WeatherProcessor()

# Test pipeline complet
result = processor.process(weather_data)

print("✓ Résultat:", result.get("success"))
print("✓ Indicateurs:", result.get("indicators", {}).keys())
```

Exécuter :
```bash
python3 test_weather.py
```

### Étape 6 : Test Processeur Bikes (Avec Données Réelles)

Créer un fichier : `test_bikes.py`

```python
# test_bikes.py
from processors import BikesProcessor
from utils.file_utils import load_json, find_json_files
from config import settings
import json

# Chercher fichiers bikes
bikes_files = find_json_files(str(settings.BIKES_JSON_PATH))

if bikes_files:
    print(f"✓ Fichier trouvé: {bikes_files[0]}")
    
    # Charger données (premiers enregistrements seulement pour test)
    data = load_json(bikes_files[0])
    
    # Limiter pour test rapide
    if data and "results" in data:
        data["results"] = data["results"][:100]  # Premiers 100 seulement
    
    # Traiter
    processor = BikesProcessor()
    result = processor.process(data)
    
    print("✓ Succès:", result.get("success"))
    if result.get("success"):
        indicators = result.get("indicators", {})
        print("✓ Métriques générées:", len(indicators.get("metrics", [])))
        print("✓ Top compteurs:", len(indicators.get("top_counters", [])))
else:
    print("⚠ Aucun fichier bikes trouvé - test ignoré")
```

Exécuter :
```bash
python3 test_bikes.py
```

### Étape 7 : Test Processeur Comptages (Sur Petit Échantillon)

Créer un fichier : `test_comptages_sample.py`

```python
# test_comptages_sample.py
from processors import ComptagesProcessor
from utils.file_utils import load_csv
from config import settings

# Créer données test minimales
test_data = [
    {
        "Identifiant arc": "1067",
        "Libelle": "Quai_d'Issy",
        "Date et heure de comptage": "2025-11-03T19:00:00+01:00",
        "Débit horaire": "769.0",
        "Taux d'occupation": "4.43",
        "Etat trafic": "Fluide",
        "Identifiant noeud amont": "560",
        "Identifiant noeud aval": "593",
        "Etat arc": "Ouvert",
        "geo_shape": '{"coordinates": [[2.271, 48.840], [2.270, 48.840]], "type": "LineString"}',
        "geo_point_2d": "48.839727155124635, 2.2702033361716216"
    }
]

processor = ComptagesProcessor()

# Test pipeline
result = processor.process(test_data)

print("✓ Succès:", result.get("success"))
if result.get("success"):
    indicators = result.get("indicators", {})
    print("✓ Métriques:", len(indicators.get("metrics", [])))
    print("✓ Top 10 tronçons:", len(indicators.get("top_10_troncons", [])))
```

Exécuter :
```bash
python3 test_comptages_sample.py
```

### Étape 8 : Test Main.py (Test Complet)

```bash
# Exécuter le traitement complet
python3 main.py
```

**Vérifications à faire** :

1. ✅ Vérifier que tous les processeurs s'initialisent
2. ✅ Vérifier que les données sont chargées
3. ✅ Vérifier que chaque type est traité
4. ✅ Vérifier que le rapport est généré
5. ✅ Vérifier les fichiers output créés

### Étape 9 : Vérification des Outputs

```bash
# Vérifier structure output
ls -la output/
ls -la output/metrics/
ls -la output/reports/

# Vérifier contenu rapport JSON
python3 -c "
import json
from pathlib import Path
from datetime import datetime

date = datetime.now().strftime('%Y-%m-%d')
report_path = Path(f'output/reports/daily_report_{date}.json')

if report_path.exists():
    with open(report_path) as f:
        report = json.load(f)
    print('✓ Rapport trouvé')
    print('✓ Summary:', report.get('summary', {}))
    print('✓ Top 10 tronçons:', len(report.get('top_10_troncons_frequentes', [])))
    print('✓ Alertes:', len(report.get('alertes_congestion', [])))
else:
    print('⚠ Rapport non trouvé')
"
```

### Étape 10 : Test avec Données Réelles (Si Disponibles)

Si vous avez accès aux fichiers de données :

```bash
# Vérifier présence fichiers batch
ls -lh bucket-cityflow-paris-s3-raw/cityflow-raw/raw/batch/*.csv

# Vérifier présence fichiers API
find bucket-cityflow-paris-s3-raw/cityflow-raw/raw/api -name "*.json" | head -5

# Si fichiers présents, tester avec échantillon
# (Pour éviter de traiter 6.2 GB de données en test)
```

## 🐛 Tests de Dépannage

### Test 1 : Vérifier Erreurs d'Import

```bash
python3 -c "
try:
    from processors.base_processor import BaseProcessor
    print('✓ BaseProcessor OK')
except Exception as e:
    print(f'✗ Erreur: {e}')

try:
    from utils.validators import validate_coordinates
    print('✓ Validators OK')
except Exception as e:
    print(f'✗ Erreur: {e}')
"
```

### Test 2 : Vérifier Chemins Fichiers

```bash
python3 -c "
from config import settings
from pathlib import Path

print('Vérification chemins:')
print(f'  Batch data: {settings.BATCH_DATA_PATH.exists()}')
print(f'  API data: {settings.API_DATA_PATH.exists()}')
print(f'  Output dir: {settings.OUTPUT_DIR.exists()}')
"
```

### Test 3 : Test Calcul Temps Perdu

```bash
python3 -c "
from utils.traffic_calculations import calculate_lost_time

# Test avec valeurs normales
temps_perdu, temps_total = calculate_lost_time(
    debit_horaire=1000,
    taux_occupation=50,
    longueur_metres=1000
)

print(f'✓ Temps perdu: {temps_perdu:.2f} minutes')
print(f'✓ Temps total: {temps_total:.2f} minutes')
assert temps_perdu > 0
print('✓ Calcul temps perdu fonctionne')
"
```

## 📊 Script de Test Automatique Complet

Créer un fichier `run_tests.py` :

```python
#!/usr/bin/env python3
"""
Script de test automatique pour CityFlow Analytics
"""

import sys
from pathlib import Path

def test_imports():
    """Test 1: Imports"""
    print("\n[TEST 1] Vérification imports...")
    try:
        from processors import BikesProcessor, TrafficProcessor
        from utils import validators, aggregators
        from models import TrafficMetrics
        from config import settings
        print("  ✓ Tous les imports réussis")
        return True
    except Exception as e:
        print(f"  ✗ Erreur import: {e}")
        return False

def test_configuration():
    """Test 2: Configuration"""
    print("\n[TEST 2] Vérification configuration...")
    try:
        from config import settings
        assert settings.CHUNK_SIZE > 0
        assert settings.OUTPUT_DIR is not None
        print(f"  ✓ Configuration valide (CHUNK_SIZE={settings.CHUNK_SIZE})")
        return True
    except Exception as e:
        print(f"  ✗ Erreur config: {e}")
        return False

def test_validators():
    """Test 3: Validators"""
    print("\n[TEST 3] Test validators...")
    try:
        from utils.validators import validate_coordinates, validate_date_iso
        
        assert validate_coordinates(2.3522, 48.8566) == True
        assert validate_coordinates(200, 100) == False
        
        date = validate_date_iso("2025-11-03T02:00:00+01:00")
        assert date is not None
        
        print("  ✓ Validators fonctionnent")
        return True
    except Exception as e:
        print(f"  ✗ Erreur validators: {e}")
        return False

def test_aggregators():
    """Test 4: Aggregators"""
    print("\n[TEST 4] Test aggregators...")
    try:
        from utils.aggregators import calculate_daily_total
        
        test_data = [{"count": 10}, {"count": 20}]
        total = calculate_daily_total(test_data, "count")
        assert total == 30.0
        
        print("  ✓ Aggregators fonctionnent")
        return True
    except Exception as e:
        print(f"  ✗ Erreur aggregators: {e}")
        return False

def test_traffic_calculations():
    """Test 5: Calculs trafic"""
    print("\n[TEST 5] Test calculs trafic...")
    try:
        from utils.traffic_calculations import calculate_lost_time
        
        temps_perdu, temps_total = calculate_lost_time(
            debit_horaire=1000,
            taux_occupation=50,
            longueur_metres=1000
        )
        
        assert temps_perdu >= 0
        assert temps_total >= 0
        
        print(f"  ✓ Calcul temps perdu: {temps_perdu:.2f} min")
        return True
    except Exception as e:
        print(f"  ✗ Erreur calculs trafic: {e}")
        return False

def test_processors():
    """Test 6: Processeurs"""
    print("\n[TEST 6] Test processeurs...")
    try:
        from processors import WeatherProcessor
        
        # Test données minimales
        weather_data = {
            "days": [{
                "datetime": "2025-11-03",
                "tempmax": 15.0,
                "tempmin": 10.0,
                "temp": 12.5,
                "precip": 0.0,
                "windspeed": 10.0,
                "conditions": "Clear"
            }]
        }
        
        processor = WeatherProcessor()
        result = processor.process(weather_data)
        
        assert result.get("success") == True
        
        print("  ✓ Processeur Weather fonctionne")
        return True
    except Exception as e:
        print(f"  ✗ Erreur processeurs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_output_directories():
    """Test 7: Répertoires output"""
    print("\n[TEST 7] Vérification répertoires output...")
    try:
        from config import settings
        
        # Vérifier création automatique
        assert settings.OUTPUT_DIR.exists()
        assert settings.METRICS_DIR.exists()
        assert settings.REPORTS_DIR.exists()
        
        print("  ✓ Répertoires output créés")
        return True
    except Exception as e:
        print(f"  ✗ Erreur répertoires: {e}")
        return False

def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("CityFlow Analytics - Suite de Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_validators,
        test_aggregators,
        test_traffic_calculations,
        test_processors,
        test_output_directories
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("✓ TOUS LES TESTS RÉUSSIS!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) échoué(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Exécuter :
```bash
python3 run_tests.py
```

## ✅ Checklist de Test Finale

- [ ] Tous les imports fonctionnent
- [ ] Configuration chargée correctement
- [ ] Utilitaires testés individuellement
- [ ] Au moins un processeur testé (Weather ou Bikes)
- [ ] Calcul temps perdu fonctionne
- [ ] Répertoires output créés
- [ ] Main.py s'exécute sans erreur fatale
- [ ] Fichiers rapport générés dans output/reports/
- [ ] Métriques exportées dans output/metrics/

## 🚨 Problèmes Courants

**Import Error** :
```bash
# Solution: Vérifier PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 main.py
```

**Fichier non trouvé** :
- Vérifier que les données sont dans `bucket-cityflow-paris-s3-raw/`
- Ou modifier les chemins dans `config/settings.py`

**Erreur mémoire (fichier trop gros)** :
- Utiliser `process_large_file()` pour comptages
- Ou traiter seulement un échantillon pour test

