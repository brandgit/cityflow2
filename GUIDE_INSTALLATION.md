# Guide d'Installation et Exécution - CityFlow Analytics

## 📋 Commandes Complètes : De l'Environnement à l'Exécution

### ÉTAPE 1 : Vérification de l'Environnement Système

```bash
# 1.1 Vérifier Python 3 installé
python3 --version
# Doit afficher: Python 3.x.x (minimum 3.7)

# 1.2 Vérifier pip
python3 -m pip --version

# 1.3 Vérifier répertoire courant
pwd
# Doit être dans: .../cityflow
```

### ÉTAPE 2 : Création de l'Environnement Virtuel (Optionnel mais Recommandé)

```bash
# 2.1 Créer environnement virtuel
python3 -m venv venv

# 2.2 Activer l'environnement virtuel
# Sur macOS/Linux:
source venv/bin/activate

# Sur Windows (si applicable):
# venv\Scripts\activate

# 2.3 Vérifier activation (commande prompt change)
# Le prompt devrait afficher (venv)
```

### ÉTAPE 3 : Installation des Dépendances

```bash
# 3.1 Installer dépendances optionnelles (recommandé)
pip install -r requirements.txt

# OU installer manuellement:
pip install python-dateutil holidays

# 3.2 Vérifier installation
pip list | grep -E "dateutil|holidays"
```

**Note:** Les dépendances sont optionnelles - le code fonctionne sans elles.

### ÉTAPE 4 : Vérification de la Structure du Projet

```bash
# 4.1 Vérifier structure des répertoires
ls -la processors/ utils/ models/ config/

# 4.2 Vérifier fichiers principaux
ls -la main.py run_tests.py README.md

# 4.3 Vérifier que les données sont présentes (si disponibles)
ls -la bucket-cityflow-paris-s3-raw/cityflow-raw/raw/batch/ 2>/dev/null || echo "⚠ Données batch non trouvées"
ls -la bucket-cityflow-paris-s3-raw/cityflow-raw/raw/api/ 2>/dev/null || echo "⚠ Données API non trouvées"
```

### ÉTAPE 5 : Tests de Validation

```bash
# 5.1 Exécuter suite de tests automatique
python3 run_tests.py

# Résultat attendu: "✓ TOUS LES TESTS RÉUSSIS!"

# 5.2 Test individuel des imports
python3 -c "from processors import BikesProcessor; print('✓ Import OK')"

# 5.3 Test de la configuration
python3 -c "from config import settings; print('✓ Config:', settings.CHUNK_SIZE)"
```

### ÉTAPE 6 : Configuration des Chemins (Si Nécessaire)

```bash
# 6.1 Vérifier chemins dans config/settings.py
python3 -c "
from config import settings
from pathlib import Path

print('Batch path exists:', Path(settings.BATCH_DATA_PATH).exists())
print('API path exists:', Path(settings.API_DATA_PATH).exists())
print('Output dir exists:', settings.OUTPUT_DIR.exists())
"

# 6.2 Si chemins incorrects, modifier config/settings.py
# Éditer le fichier si nécessaire
```

### ÉTAPE 7 : Test avec Données Minimales

```bash
# 7.1 Test processeur Weather (sans données externes)
python3 -c "
from processors import WeatherProcessor

processor = WeatherProcessor()
data = {
    'days': [{
        'datetime': '2025-11-03',
        'tempmax': 15.0,
        'tempmin': 10.0,
        'temp': 12.5,
        'precip': 0.0,
        'windspeed': 10.0,
        'conditions': 'Clear'
    }]
}

result = processor.process(data)
print('✓ Succès:', result['success'])
print('✓ Indicateurs:', list(result.get('indicators', {}).keys()))
"
```

### ÉTAPE 8 : Exécution du Processus Complet

```bash
# 8.1 Exécuter le traitement complet
python3 main.py

# Le script va:
# - Charger la configuration
# - Initialiser tous les processeurs
# - Charger les données brutes
# - Traiter chaque type de données
# - Générer le rapport quotidien
# - Exporter les résultats
```

### ÉTAPE 9 : Vérification des Résultats

```bash
# 9.1 Vérifier création répertoires output
ls -la output/
ls -la output/metrics/
ls -la output/reports/

# 9.2 Lister fichiers générés
ls -lh output/metrics/*.json 2>/dev/null || echo "Aucun fichier métriques"
ls -lh output/reports/*.json 2>/dev/null || echo "Aucun fichier rapport"

# 9.3 Afficher contenu rapport JSON
python3 -c "
import json
from pathlib import Path
from datetime import datetime

date = datetime.now().strftime('%Y-%m-%d')
report_path = Path(f'output/reports/daily_report_{date}.json')

if report_path.exists():
    with open(report_path) as f:
        report = json.load(f)
    print('=== RAPPORT QUOTIDIEN ===')
    print(f'Date: {report.get(\"date\")}')
    print(f'\nSummary:')
    for k, v in report.get('summary', {}).items():
        print(f'  {k}: {v}')
    print(f'\nTop 10 tronçons: {len(report.get(\"top_10_troncons_frequentes\", []))} éléments')
    print(f'Alertes congestion: {len(report.get(\"alertes_congestion\", []))} éléments')
else:
    print('⚠ Rapport non trouvé')
"

# 9.4 Afficher premier fichier métriques (exemple)
python3 -c "
import json
from pathlib import Path
from glob import glob

metrics_files = glob('output/metrics/*.json')
if metrics_files:
    with open(metrics_files[0]) as f:
        data = json.load(f)
    print(f'\n=== MÉTRIQUES ({Path(metrics_files[0]).name}) ===')
    print(f'Clés disponibles: {list(data.keys())}')
"
```

### ÉTAPE 10 : Nettoyage (Optionnel)

```bash
# 10.1 Désactiver environnement virtuel (si activé)
deactivate

# 10.2 Supprimer fichiers temporaires (optionnel)
rm -rf output/processed/*.csv 2>/dev/null || true

# 10.3 Garder les outputs (métriques et rapports) pour analyse
```

---

## 🚀 Script d'Exécution Automatique Complète

Créer un fichier `setup_and_run.sh` :

```bash
#!/bin/bash
# Script d'installation et exécution automatique

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "CityFlow Analytics - Installation & Run"
echo "=========================================="

# Étape 1: Vérifications
echo -e "\n[1/7] Vérifications système..."
python3 --version || { echo "✗ Python 3 requis"; exit 1; }
echo "✓ Python 3 OK"

# Étape 2: Environnement virtuel (optionnel)
echo -e "\n[2/7] Environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
else
    echo "✓ Environnement virtuel existant"
fi

source venv/bin/activate 2>/dev/null || true

# Étape 3: Dépendances
echo -e "\n[3/7] Installation dépendances..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt || echo "⚠ Dépendances optionnelles non installées (continue quand même)"
fi

# Étape 4: Tests
echo -e "\n[4/7] Tests de validation..."
python3 run_tests.py || { echo "✗ Tests échoués"; exit 1; }

# Étape 5: Vérification structure
echo -e "\n[5/7] Vérification structure..."
[ -d "processors" ] || { echo "✗ Répertoire processors manquant"; exit 1; }
[ -d "utils" ] || { echo "✗ Répertoire utils manquant"; exit 1; }
[ -d "models" ] || { echo "✗ Répertoire models manquant"; exit 1; }
[ -d "config" ] || { echo "✗ Répertoire config manquant"; exit 1; }
echo "✓ Structure OK"

# Étape 6: Exécution
echo -e "\n[6/7] Exécution traitement complet..."
python3 main.py || { echo "✗ Erreur lors de l'exécution"; exit 1; }

# Étape 7: Vérification outputs
echo -e "\n[7/7] Vérification outputs..."
if [ -d "output/reports" ] && [ "$(ls -A output/reports/*.json 2>/dev/null)" ]; then
    echo "✓ Rapports générés"
    ls -lh output/reports/*.json | tail -1
else
    echo "⚠ Aucun rapport généré"
fi

echo -e "\n=========================================="
echo "✓ PROCESSUS TERMINÉ AVEC SUCCÈS!"
echo "=========================================="
```

Rendre exécutable et lancer :
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

---

## 📝 Commandes Rapides (Cheat Sheet)

```bash
# Installation rapide
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Test rapide
python3 run_tests.py

# Exécution complète
python3 main.py

# Vérification résultats
ls output/reports/ && cat output/reports/daily_report_$(date +%Y-%m-%d).json | python3 -m json.tool | head -30

# Désactivation environnement
deactivate
```

---

## 🔧 Dépannage

### Erreur: ModuleNotFoundError
```bash
# Solution 1: Vérifier PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Solution 2: Réinstaller dans venv
source venv/bin/activate
pip install -r requirements.txt
```

### Erreur: Fichier non trouvé
```bash
# Vérifier chemins dans config
python3 -c "from config import settings; print(settings.BATCH_DATA_PATH)"
```

### Erreur: Permission denied
```bash
# Rendre scripts exécutables
chmod +x setup_and_run.sh run_tests.py
```

---

## ✅ Checklist Complète

Avant exécution :
- [ ] Python 3 installé (3.7+)
- [ ] Répertoire `cityflow` comme répertoire courant
- [ ] Structure complète (processors/, utils/, models/, config/)
- [ ] Tests passent (`python3 run_tests.py`)

Après exécution :
- [ ] `output/metrics/` contient fichiers JSON
- [ ] `output/reports/` contient rapport quotidien
- [ ] Rapport JSON lisible et contient données
- [ ] Rapport CSV généré

