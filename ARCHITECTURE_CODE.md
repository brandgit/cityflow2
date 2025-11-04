# Architecture du Code de Traitement CityFlow Analytics

## 📁 Structure des Répertoires

```
cityflow/
├── main.py                          # Point d'entrée principal
├── config/
│   ├── __init__.py
│   └── settings.py                  # Configuration (chemins, paramètres)
├── processors/                      # Processeurs par type de données
│   ├── __init__.py
│   ├── base_processor.py            # Classe abstraite de base
│   ├── bikes_processor.py           # Traitements API Bikes
│   ├── traffic_processor.py         # Traitements API Traffic RATP
│   ├── weather_processor.py        # Traitements API Weather
│   ├── comptages_processor.py       # Traitements Batch Comptages (CRITIQUE)
│   ├── chantiers_processor.py       # Traitements Batch Chantiers
│   └── referentiel_processor.py     # Traitements Référentiel Géographique
├── utils/                           # Utilitaires partagés
│   ├── __init__.py
│   ├── validators.py                # Fonctions de validation
│   ├── aggregators.py              # Fonctions d'agrégation communes
│   ├── geo_utils.py                # Utilitaires géographiques (longueur, intersection)
│   ├── time_utils.py               # Utilitaires temporels (parsing dates, jour type)
│   ├── traffic_calculations.py      # Calculs spécifiques trafic (temps perdu, etc.)
│   └── file_utils.py                # Utilitaires fichiers (CSV, JSON)
└── models/                          # Modèles de données
    ├── __init__.py
    ├── bike_metrics.py              # Modèles métriques bikes
    ├── traffic_metrics.py           # Modèles métriques trafic
    ├── weather_metrics.py           # Modèles métriques météo
    └── daily_report.py              # Modèle rapport quotidien
```

## 🏗️ Architecture des Classes Processeurs

### Classe Abstraite de Base

```python
# processors/base_processor.py
class BaseProcessor:
    """
    Classe abstraite pour tous les processeurs de données.
    Chaque processeur implémente : validate, aggregate, calculate_indicators
    """
    def validate_and_clean(self, data):
        """Validation et nettoyage des données brutes"""
        raise NotImplementedError
    
    def aggregate_daily(self, cleaned_data):
        """Agrégations quotidiennes"""
        raise NotImplementedError
    
    def calculate_indicators(self, aggregated_data):
        """Calculs d'indicateurs avancés"""
        raise NotImplementedError
    
    def process(self, raw_data):
        """Pipeline complet : validate → aggregate → calculate"""
        cleaned = self.validate_and_clean(raw_data)
        aggregated = self.aggregate_daily(cleaned)
        indicators = self.calculate_indicators(aggregated)
        return indicators
```

### Structure d'un Processeur Spécifique

```python
# processors/bikes_processor.py
class BikesProcessor(BaseProcessor):
    def __init__(self, config):
        self.config = config
    
    def validate_and_clean(self, data):
        """Validation coordonnées GPS, détection défaillances"""
        # Appel utils/validators.py
        pass
    
    def aggregate_daily(self, cleaned_data):
        """Agrégations : total/jour, pic horaire, par arrondissement"""
        # Appel utils/aggregators.py
        pass
    
    def calculate_indicators(self, aggregated_data):
        """Indice fréquentation, détection anomalies"""
        # Appel utils/traffic_calculations.py
        pass
```

## 🔄 Flux de Traitement

```
main.py
  │
  ├─→ Chargement configuration (config/settings.py)
  │
  ├─→ Initialisation processeurs
  │   ├─→ BikesProcessor
  │   ├─→ TrafficProcessor
  │   ├─→ WeatherProcessor
  │   ├─→ ComptagesProcessor (⚠️ avec gestion chunks EC2)
  │   ├─→ ChantiersProcessor
  │   └─→ ReferentielProcessor
  │
  ├─→ Pour chaque type de données :
  │   │
  │   ├─→ 1. VALIDATION & NETTOYAGE
  │   │   ├─→ processors/[type]_processor.py → validate_and_clean()
  │   │   ├─→ utils/validators.py (fonctions réutilisables)
  │   │   └─→ Retourne : données nettoyées
  │   │
  │   ├─→ 2. AGRÉGATIONS QUOTIDIENNES
  │   │   ├─→ processors/[type]_processor.py → aggregate_daily()
  │   │   ├─→ utils/aggregators.py (fonctions communes)
  │   │   └─→ Retourne : données agrégées
  │   │
  │   ├─→ 3. CALCULS D'INDICATEURS
  │   │   ├─→ processors/[type]_processor.py → calculate_indicators()
  │   │   ├─→ utils/traffic_calculations.py (calculs spécifiques)
  │   │   └─→ Retourne : indicateurs finaux
  │   │
  │   └─→ Stockage résultats (préparation DynamoDB/S3)
  │
  └─→ Génération rapport quotidien
      └─→ models/daily_report.py → format JSON/CSV
```

## 📦 Modules Utilitaires

### `utils/validators.py`
```python
def validate_coordinates(lon, lat)
def validate_date_iso(date_string)
def detect_failing_sensors(data, threshold_hours)
def validate_geojson(geo_shape)
def normalize_traffic_status(etat_trafic)
```

### `utils/aggregators.py`
```python
def aggregate_by_hour(data, date_field)
def aggregate_by_arrondissement(data, geo_field)
def calculate_daily_total(data, count_field)
def calculate_hourly_average(data)
def find_peak_hour(data, count_field)
```

### `utils/geo_utils.py`
```python
def calculate_line_length(geo_shape_linestring)  # mètres
def calculate_polygon_area(geo_shape_polygon)    # m²
def point_in_polygon(point, polygon)             # intersection
def get_arrondissement_from_coordinates(lon, lat)
```

### `utils/time_utils.py`
```python
def parse_iso_date(date_string)
def get_day_type(date)  # "Lundi", "Mardi", "Weekend", "Férié"
def calculate_time_difference(date1, date2)
def normalize_hour(hour)
```

### `utils/traffic_calculations.py`
```python
def calculate_lost_time(debit, taux_occupation, longueur_metres, vitesse_ref)
def calculate_observed_speed(taux_occupation, vitesse_ref)
def detect_congestion_alerts(data, seuil_taux=80, duree_min=120)
def calculate_traffic_reliability_index(data)
def compare_to_day_type(current_data, day_type_profile)
```

### `utils/file_utils.py`
```python
def load_csv(file_path, separator=';')
def save_csv(data, file_path)
def load_json(file_path)
def save_json(data, file_path)
def chunk_file(file_path, chunk_size)
```

## 🎯 Modèles de Données

### `models/traffic_metrics.py`
```python
@dataclass
class TrafficMetrics:
    date: str
    identifiant_arc: str
    libelle: str
    debit_horaire_moyen: float
    debit_journalier_total: float
    debit_max: float
    taux_occupation_moyen: float
    etat_trafic_dominant: str
    heure_pic: str
    temps_perdu_minutes: float
    temps_perdu_total_minutes: float
    congestion_alerte: bool
    arrondissement: str
    geo_point_2d: dict
```

### `models/daily_report.py`
```python
@dataclass
class DailyReport:
    date: str
    generated_at: str
    summary: dict
    top_10_troncons_frequentes: list
    top_10_zones_congestionnees: list
    capteurs_defaillants: list
    alertes_congestion: list
    chantiers_actifs: list
```

## ⚙️ Configuration

### `config/settings.py`
```python
# Chemins fichiers
BATCH_DATA_PATH = "bucket-cityflow-paris-s3-raw/cityflow-raw/raw/batch/"
API_DATA_PATH = "bucket-cityflow-paris-s3-raw/cityflow-raw/raw/api/"

# Paramètres traitement
CHUNK_SIZE = 10000  # lignes par chunk
EC2_CHUNK_SIZE = 100000  # lignes pour traitement EC2

# Seuils
TAUX_OCCUPATION_SEUIL = 80  # % pour alerte congestion
TEMPS_PERDU_VITESSE_REF = 50  # km/h
CAPTEUR_DEFAILLANT_HEURES = 6  # heures sans données

# Arrondissements Paris
ARRONDISSEMENTS = list(range(75001, 75021))
```

## 🚀 Point d'Entrée Main

### `main.py` Structure

```python
def main():
    """Point d'entrée principal"""
    
    # 1. Chargement configuration
    config = load_config()
    
    # 2. Initialisation processeurs
    processors = initialize_processors(config)
    
    # 3. Chargement données brutes
    raw_data = load_raw_data(config)
    
    # 4. Traitement par type
    results = {}
    for data_type, processor in processors.items():
        results[data_type] = processor.process(raw_data[data_type])
    
    # 5. Jointures multi-sources (optionnel)
    enriched_results = enrich_multi_source(results)
    
    # 6. Génération rapport
    daily_report = generate_daily_report(results, enriched_results)
    
    # 7. Export (simulation DynamoDB/S3)
    export_results(results, daily_report, config)
    
    return daily_report
```

## 🔗 Dépendances entre Processeurs

```
ReferentielProcessor (1er)
  │
  └─→ Enrichit les autres processeurs
      │
      ├─→ ComptagesProcessor (jointure Identifiant arc)
      │
      ├─→ ChantiersProcessor (enrichissement géographique)
      │
      └─→ BikesProcessor (enrichissement arrondissement)

ComptagesProcessor
  │
  ├─→ Calcule temps perdu
  │
  ├─→ Détecte alertes congestion
  │
  └─→ Génère Top 10

ChantiersProcessor
  │
  └─→ Jointure avec ComptagesProcessor (intersection géographique)
      └─→ Ajuste temps perdu selon présence chantier

WeatherProcessor
  │
  └─→ Corrélation avec BikesProcessor et ComptagesProcessor
      └─→ Impact météo sur mobilité
```

## 📊 Flux de Données Détaillé

### Pour Comptages Routiers (Cas Critique)

```
1. Chargement fichier CSV (6.2 GB)
   └─→ utils/file_utils.py → load_csv()

2. Détection si fichier > limite
   └─→ Si oui : découpe en chunks
   └─→ utils/file_utils.py → chunk_file()

3. Pour chaque chunk :
   ├─→ ComptagesProcessor.validate_and_clean()
   │   ├─→ utils/validators.py → validate_date_iso()
   │   ├─→ utils/validators.py → validate_geojson()
   │   └─→ utils/geo_utils.py → get_arrondissement_from_coordinates()
   │
   ├─→ ComptagesProcessor.aggregate_daily()
   │   ├─→ utils/aggregators.py → aggregate_by_hour()
   │   ├─→ utils/aggregators.py → calculate_daily_total()
   │   └─→ utils/aggregators.py → calculate_hourly_average()
   │
   └─→ ComptagesProcessor.calculate_indicators()
       ├─→ utils/traffic_calculations.py → calculate_lost_time()
       ├─→ utils/traffic_calculations.py → detect_congestion_alerts()
       └─→ utils/geo_utils.py → calculate_line_length()
```

## 🧪 Tests (Structure Recommandée)

```
tests/
├── __init__.py
├── test_validators.py
├── test_aggregators.py
├── test_geo_utils.py
├── test_traffic_calculations.py
├── test_bikes_processor.py
├── test_comptages_processor.py
└── test_daily_report.py
```

## 🔒 Gestion des Erreurs

Chaque processeur doit gérer :
- Fichiers manquants
- Format de données invalide
- Valeurs nulles/incohérentes
- Erreurs de parsing (dates, GeoJSON)
- Timeout sur gros fichiers

Logging centralisé via `logging` module Python.

## 📝 Exemple d'Utilisation

```python
# main.py
from processors import BikesProcessor, ComptagesProcessor
from config import settings

# Initialisation
bikes_proc = BikesProcessor(settings)
comptages_proc = ComptagesProcessor(settings)

# Chargement données
raw_bikes = load_json("api/bikes/data.json")
raw_comptages = load_csv("batch/comptages.csv")

# Traitement
bikes_results = bikes_proc.process(raw_bikes)
comptages_results = comptages_proc.process(raw_comptages)

# Export
save_json(bikes_results, "output/bikes_metrics.json")
save_json(comptages_results, "output/traffic_metrics.json")
```

