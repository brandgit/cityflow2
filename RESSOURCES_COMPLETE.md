# 📋 Liste Complète des Ressources - CityFlow Analytics

## 🎯 Vue d'ensemble

Ce document liste toutes les ressources du projet CityFlow Analytics, organisées par catégorie.

---

## 📂 Structure du Projet

```
cityflow/
├── 📄 Fichiers racine
├── 📁 api/                    # API REST
├── 📁 config/                 # Configuration
├── 📁 models/                 # Modèles de données
├── 📁 processors/             # Traitement des données
├── 📁 report_generator/       # Génération rapports
├── 📁 utils/                  # Utilitaires partagés
├── 📁 output/                 # Résultats générés
├── 📁 bucket-cityflow-paris-s3-raw/  # Données sources
├── 📁 tests/                  # Tests
├── 📁 venv/                   # Environnement virtuel Python
└── 📄 Documentation (.md)
```

---

## 📄 Fichiers Principaux (Racine)

### 🚀 Scripts d'exécution

| Fichier | Description | Usage |
|---------|-------------|-------|
| `main.py` | ⭐ **Pipeline complet** (traitement + rapport) | `python3 main.py` |
| `setup_and_run.sh` | Script shell pour setup + exécution | `./setup_and_run.sh` |
| `run_tests.py` | Script de tests | `python3 run_tests.py` |
| `test_database_connection.py` | Test connexion BDD (MongoDB/DynamoDB) | `python3 test_database_connection.py` |

### 📋 Configuration

| Fichier | Description |
|---------|-------------|
| `requirements.txt` | Dépendances Python (pymongo, boto3, flask, etc.) |
| `.env` | Variables d'environnement (non versionné) |
| `env.example` | Exemple de configuration `.env` |

### 📚 Documentation Principale

| Fichier | Description |
|---------|-------------|
| `README.md` | 📖 Vue d'ensemble du projet |
| `COMMANDES_RAPIDES.md` | ⚡ Commandes essentielles |
| `RECAP_FINAL.md` | 📊 Récapitulatif complet |
| `API_GUIDE_COMPLET.md` | 🌐 Guide complet API REST |

### 📖 Documentation Architecture

| Fichier | Description |
|---------|-------------|
| `ARCHITECTURE_AWS.md` | Architecture cloud AWS |
| `ARCHITECTURE_CODE.md` | Architecture du code |
| `ARCHITECTURE_BDD.md` | Architecture base de données |
| `DIAGRAMME_ARCHITECTURE.md` | Diagrammes d'architecture |

### 📖 Documentation Technique

| Fichier | Description |
|---------|-------------|
| `GUIDE_EXECUTION.md` | Guide d'exécution détaillé |
| `GUIDE_INSTALLATION.md` | Guide d'installation |
| `GUIDE_TEST.md` | Guide des tests |
| `GUIDE_MIGRATION_MONGODB.md` | Migration vers MongoDB |
| `MONGODB_SETUP.md` | Setup MongoDB |
| `VARIABLES_ENVIRONNEMENT.md` | Variables d'environnement |
| `LIMITES_MONGODB.md` | Limitations MongoDB et solutions |
| `SOLUTIONS_COMPTAGES.md` | Solutions pour gros datasets |
| `LOGIQUE_EXPORT_RAPPORTS.md` | Logique export rapports |

### 📊 Documentation Données

| Fichier | Description |
|---------|-------------|
| `TRAITEMENTS_DONNEES.md` | Traitements des données |
| `RESUME_TRAITEMENTS.md` | Résumé des traitements |
| `TABLEAU_RECAP_TRAITEMENTS.md` | Tableau récapitulatif |
| `CHANGELOG_SEPARATION_RAPPORT.md` | Changelog séparation rapport |

---

## 🌐 API REST (`api/`)

### 📁 Structure

```
api/
├── __init__.py
├── lambda_function.py          # ⭐ Handler AWS Lambda
├── local_server.py             # ⭐ Serveur Flask local
├── test_api.py                 # Tests API
├── README.md                   # Documentation API
├── API_DEPLOYMENT.md           # Guide déploiement AWS
├── handlers/                   # Handlers endpoints
│   ├── __init__.py
│   ├── metrics_handler.py     # GET /metrics/*
│   ├── report_handler.py       # GET /report/*
│   └── stats_handler.py        # GET /stats
└── utils/                      # Utilitaires API
    ├── __init__.py
    ├── response.py             # Formatage réponses HTTP
    └── validation.py           # Validation paramètres
```

### 📄 Fichiers API

| Fichier | Description | Endpoints |
|---------|-------------|-----------|
| `lambda_function.py` | Handler principal Lambda | Tous les endpoints |
| `local_server.py` | Serveur Flask (dev local) | Port 5001 par défaut |
| `test_api.py` | Script de tests | Tests automatisés |
| `handlers/metrics_handler.py` | Logique métriques | `/metrics/{type}/{date}` |
| `handlers/report_handler.py` | Logique rapports | `/report/{date}` |
| `handlers/stats_handler.py` | Logique statistiques | `/stats` |
| `utils/response.py` | Formatage réponses | CORS, JSON, erreurs |
| `utils/validation.py` | Validation | Dates, types métriques |

### 🔗 Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | Statistiques globales |
| `/metrics/{type}/{date}` | GET | Métriques spécifiques |
| `/metrics/{date}` | GET | Toutes les métriques |
| `/report/{date}` | GET | Rapport quotidien |
| `/docs` | GET | Documentation interactive |

---

## ⚙️ Configuration (`config/`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Package config |
| `settings.py` | ⭐ Paramètres globaux (chemins, dates, etc.) |

### Variables principales dans `settings.py`

- Chemins de données (raw, processed, output)
- Formats de dates
- Paramètres de traitement
- Configurations par environnement

---

## 📊 Modèles de Données (`models/`)

| Fichier | Description | Structure |
|---------|-------------|-----------|
| `__init__.py` | Package models | |
| `bike_metrics.py` | Modèle métriques vélos | Compteurs, agrégations |
| `traffic_metrics.py` | Modèle métriques trafic | Perturbations RATP |
| `weather_metrics.py` | Modèle métriques météo | Données météo |
| `daily_report.py` | Modèle rapport quotidien | Résumé, top 10, alertes |

---

## 🔄 Processeurs (`processors/`)

### 📁 Structure

```
processors/
├── __init__.py
├── main.py                    # ⭐ Point d'entrée processors
├── base_processor.py          # Classe de base abstraite
├── bikes_processor.py         # Traitement données vélos
├── traffic_processor.py       # Traitement perturbations RATP
├── weather_processor.py       # Traitement données météo
├── comptages_processor.py     # Traitement comptages routiers (6.2GB)
├── chantiers_processor.py     # Traitement chantiers
├── referentiel_processor.py   # Traitement référentiel géographique
└── utils/                     # Utilitaires processeurs
    ├── __init__.py
    ├── aggregators.py         # Agrégations
    ├── file_utils.py           # Utilitaires fichiers
    ├── geo_utils.py            # Utilitaires géographiques
    ├── time_utils.py           # Utilitaires temps/dates
    ├── traffic_calculations.py # Calculs trafic
    └── validators.py           # Validation données
```

### 📄 Processeurs par Type de Donnée

| Processeur | Source | Format | Taille | Description |
|-----------|--------|--------|--------|-------------|
| `bikes_processor.py` | API JSON | JSON | ~1 MB | 119 compteurs vélos |
| `traffic_processor.py` | API JSON | JSON | ~600 KB | 94 perturbations RATP |
| `weather_processor.py` | API JSON | JSON | ~1 KB | Données météo quotidiennes |
| `comptages_processor.py` | Batch CSV | CSV | **6.2 GB** | 3348 tronçons routiers |
| `chantiers_processor.py` | Batch CSV | CSV | ~500 KB | 68 chantiers |
| `referentiel_processor.py` | Batch CSV | CSV | ~1 MB | 3739 tronçons géographiques |

### 🛠️ Utilitaires Processeurs

| Fichier | Fonctionnalités |
|---------|----------------|
| `aggregators.py` | Agrégations quotidiennes, calculs statistiques |
| `file_utils.py` | Chargement CSV/JSON, gestion chunks |
| `geo_utils.py` | Calculs géographiques, distances, coordonnées |
| `time_utils.py` | Gestion dates, heures, jours fériés |
| `traffic_calculations.py` | Calculs trafic, congestion, alertes |
| `validators.py` | Validation données, nettoyage |

---

## 📈 Générateur de Rapports (`report_generator/`)

### 📁 Structure

```
report_generator/
├── __init__.py
├── main.py                    # ⭐ Point d'entrée rapports
├── daily_report_generator.py  # ⭐ Générateur rapport quotidien
├── README.md                  # Documentation rapports
└── utils/
    ├── __init__.py
    └── file_utils.py          # Utilitaires fichiers
```

### 📄 Fichiers

| Fichier | Description | Fonctionnalités |
|---------|-------------|-----------------|
| `main.py` | Orchestrateur génération | Appel du générateur |
| `daily_report_generator.py` | ⭐ Générateur principal | Chargement métriques, génération, export |
| `utils/file_utils.py` | Utilitaires | Export CSV/JSON |

### 📊 Rapports Générés

| Format | Destination | Contenu |
|--------|-------------|---------|
| **CSV** | `output/reports/` (local) ou S3 (AWS) | Rapport formaté |
| **JSON** | MongoDB (local) ou DynamoDB (AWS) | Rapport complet |

---

## 🔧 Utilitaires Partagés (`utils/`)

### 📁 Structure

```
utils/
├── __init__.py
├── database_service.py        # ⭐ Interface abstraite BDD
├── mongodb_service.py          # ⭐ Implémentation MongoDB
├── dynamodb_service_adapter.py # ⭐ Adaptateur DynamoDB
├── database_factory.py        # ⭐ Factory choix BDD
├── metrics_optimizer.py       # ⭐ Optimisation métriques
├── aws_services.py             # Services AWS (DynamoDB, S3)
├── aggregators.py              # Agrégations
├── file_utils.py               # Utilitaires fichiers
├── geo_utils.py                # Utilitaires géographiques
├── time_utils.py                # Utilitaires temps
├── traffic_calculations.py      # Calculs trafic
└── validators.py                # Validation
```

### 🗄️ Base de Données

| Fichier | Description | Usage |
|---------|-------------|-------|
| `database_service.py` | Interface abstraite | Classe de base pour BDD |
| `mongodb_service.py` | Implémentation MongoDB | Développement local |
| `dynamodb_service_adapter.py` | Adaptateur DynamoDB | Production AWS |
| `database_factory.py` | ⭐ Factory pattern | Choix automatique MongoDB/DynamoDB |
| `metrics_optimizer.py` | ⭐ Optimisation | Version summary pour gros datasets |

### ☁️ AWS

| Fichier | Description | Services |
|---------|-------------|----------|
| `aws_services.py` | Services AWS | DynamoDB, S3 |

### 🛠️ Utilitaires Généraux

| Fichier | Description |
|---------|-------------|
| `aggregators.py` | Agrégations, calculs statistiques |
| `file_utils.py` | Lecture/écriture fichiers |
| `geo_utils.py` | Coordonnées, distances |
| `time_utils.py` | Dates, heures, jours fériés |
| `traffic_calculations.py` | Calculs trafic, congestion |
| `validators.py` | Validation, nettoyage données |

---

## 📦 Données Sources (`bucket-cityflow-paris-s3-raw/`)

### 📁 Structure

```
bucket-cityflow-paris-s3-raw/
└── cityflow-raw/
    └── raw/
        ├── api/                # Données API (JSON)
        │   ├── bikes/
        │   │   └── dt=2025-11-03/hour=02/
        │   ├── traffic/
        │   │   └── dt=2025-11-03/
        │   └── weather/
        │       └── dt=2025-11-03/
        └── batch/              # Données batch (CSV)
            ├── chantiers-perturbants-la-circulation.csv
            ├── comptages-routiers-permanents-2.csv (6.2 GB)
            └── referentiel-geographique-pour-les-donnees-trafic-issues-des-capteurs-permanents.csv
```

### 📊 Données par Type

| Type | Format | Source | Taille | Description |
|------|--------|--------|--------|-------------|
| **Bikes** | JSON | API | ~1 MB | Compteurs vélos |
| **Traffic** | JSON | API | ~600 KB | Perturbations RATP |
| **Weather** | JSON | API | ~1 KB | Données météo |
| **Comptages** | CSV | Batch | **6.2 GB** | Comptages routiers |
| **Chantiers** | CSV | Batch | ~500 KB | Chantiers |
| **Référentiel** | CSV | Batch | ~1 MB | Référentiel géographique |

---

## 📤 Résultats Générés (`output/`)

### 📁 Structure

```
output/
├── metrics/                    # Métriques générées (JSON)
│   ├── bikes_metrics_2025-11-03.json
│   ├── traffic_metrics_2025-11-03.json
│   ├── weather_metrics_2025-11-03.json
│   ├── comptages_metrics_2025-11-03.json
│   ├── chantiers_metrics_2025-11-03.json
│   └── referentiel_metrics_2025-11-03.json
├── processed/                  # Fichiers temporaires (chunks)
│   └── (auto-nettoyé après traitement)
└── reports/                    # Rapports générés
    ├── daily_report_2025-11-03.csv
    └── daily_report_2025-11-03.json
```

### 📊 Métriques Générées

| Fichier | Lignes | Taille | Description |
|---------|--------|--------|-------------|
| `bikes_metrics_*.json` | 1,482 | ~1 MB | Métriques vélos |
| `traffic_metrics_*.json` | 613 | ~600 KB | Métriques trafic |
| `weather_metrics_*.json` | 14 | ~1 KB | Métriques météo |
| `comptages_metrics_*.json` | 7.4M | ~16+ MB | Métriques comptages (summary MongoDB) |
| `chantiers_metrics_*.json` | 469 | ~500 KB | Métriques chantiers |
| `referentiel_metrics_*.json` | 40K | ~1 MB | Métriques référentiel |

### 📋 Rapports Générés

| Fichier | Format | Description |
|---------|--------|-------------|
| `daily_report_*.csv` | CSV | Rapport formaté (excel-compatible) |
| `daily_report_*.json` | JSON | Rapport complet (API) |

---

## 🧪 Tests (`tests/`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Package tests |
| *(à venir)* | Tests unitaires, intégration |

### 📄 Scripts de Test

| Fichier | Description | Usage |
|---------|-------------|-------|
| `run_tests.py` | Script de tests | `python3 run_tests.py` |
| `test_database_connection.py` | Test connexion BDD | `python3 test_database_connection.py` |
| `api/test_api.py` | Tests API | `python3 api/test_api.py` |

---

## 🐍 Environnement Python (`venv/`)

| Composant | Description |
|-----------|-------------|
| `bin/` | Exécutables Python (activate, pip, python) |
| `lib/` | Bibliothèques installées (site-packages) |
| `pyvenv.cfg` | Configuration environnement virtuel |

### 📦 Dépendances Installées

| Package | Version | Usage |
|---------|---------|-------|
| `pymongo` | >=4.6.0 | MongoDB local |
| `boto3` | >=1.28.0 | AWS services |
| `flask` | >=3.0.0 | Serveur API local |
| `flask-cors` | >=4.0.0 | CORS pour API |
| `python-dateutil` | >=2.8.2 | Utilitaires dates |
| `holidays` | >=0.34 | Jours fériés |
| `python-dotenv` | >=1.0.0 | Variables d'environnement |

---

## 📚 Documentation Complète

### 📖 Documentation Principale (Racine)

| Fichier | Pages | Description |
|---------|-------|-------------|
| `README.md` | Vue d'ensemble | Introduction, installation, usage |
| `COMMANDES_RAPIDES.md` | ⚡ Commandes | Commandes essentielles |
| `RECAP_FINAL.md` | 📊 Récapitulatif | Vue d'ensemble complète |
| `API_GUIDE_COMPLET.md` | 🌐 Guide API | Guide complet API REST |

### 🏗️ Documentation Architecture

| Fichier | Description |
|---------|-------------|
| `ARCHITECTURE_AWS.md` | Architecture cloud AWS |
| `ARCHITECTURE_CODE.md` | Architecture code source |
| `ARCHITECTURE_BDD.md` | Architecture base de données |
| `DIAGRAMME_ARCHITECTURE.md` | Diagrammes UML |

### 📘 Documentation Technique

| Fichier | Description |
|---------|-------------|
| `GUIDE_EXECUTION.md` | Guide exécution détaillé |
| `GUIDE_INSTALLATION.md` | Guide installation |
| `GUIDE_TEST.md` | Guide tests |
| `GUIDE_MIGRATION_MONGODB.md` | Migration MongoDB |
| `MONGODB_SETUP.md` | Setup MongoDB |
| `VARIABLES_ENVIRONNEMENT.md` | Variables d'environnement |
| `LIMITES_MONGODB.md` | Limitations MongoDB |
| `SOLUTIONS_COMPTAGES.md` | Solutions gros datasets |
| `LOGIQUE_EXPORT_RAPPORTS.md` | Logique export |

### 📊 Documentation Données

| Fichier | Description |
|---------|-------------|
| `TRAITEMENTS_DONNEES.md` | Traitements des données |
| `RESUME_TRAITEMENTS.md` | Résumé traitements |
| `TABLEAU_RECAP_TRAITEMENTS.md` | Tableau récapitulatif |
| `CHANGELOG_SEPARATION_RAPPORT.md` | Changelog |

### 🌐 Documentation API

| Fichier | Description |
|---------|-------------|
| `api/README.md` | Documentation API complète |
| `api/API_DEPLOYMENT.md` | Guide déploiement AWS |
| `API_GUIDE_COMPLET.md` | Guide utilisateur API |

### 📈 Documentation Rapports

| Fichier | Description |
|---------|-------------|
| `report_generator/README.md` | Documentation rapports |

---

## 🎯 Ressources par Catégorie

### 🚀 Exécution

- `main.py` - Pipeline complet
- `processors/main.py` - Traitement données
- `report_generator/main.py` - Génération rapports
- `api/local_server.py` - Serveur API local
- `api/lambda_function.py` - Handler Lambda AWS
- `setup_and_run.sh` - Script shell

### 🗄️ Base de Données

- `utils/database_service.py` - Interface abstraite
- `utils/mongodb_service.py` - MongoDB local
- `utils/dynamodb_service_adapter.py` - DynamoDB AWS
- `utils/database_factory.py` - Factory pattern
- `utils/metrics_optimizer.py` - Optimisation métriques

### 🌐 API REST

- `api/lambda_function.py` - Handler principal
- `api/local_server.py` - Serveur Flask
- `api/handlers/*` - Handlers endpoints
- `api/utils/*` - Utilitaires API

### 🔄 Traitement

- `processors/*_processor.py` - Processeurs par type
- `processors/utils/*` - Utilitaires processeurs
- `utils/*` - Utilitaires partagés

### 📊 Génération

- `report_generator/daily_report_generator.py` - Générateur
- `report_generator/main.py` - Orchestrateur

### 📚 Documentation

- 24 fichiers `.md` de documentation
- README dans chaque module
- Guides d'installation, exécution, déploiement

---

## 📊 Statistiques du Projet

### Fichiers Code

- **Python** : ~40 fichiers
- **Documentation** : 24 fichiers Markdown
- **Configuration** : 3 fichiers (.env, requirements.txt, etc.)

### Lignes de Code (estimation)

- **Processors** : ~3,000 lignes
- **API** : ~1,500 lignes
- **Utils** : ~2,000 lignes
- **Report Generator** : ~500 lignes
- **Total** : ~7,000 lignes Python

### Documentation

- **Pages** : ~24 fichiers Markdown
- **Lignes** : ~15,000 lignes de documentation

---

## 🎯 Points d'Entrée Principaux

| Point d'Entrée | Commande | Description |
|----------------|----------|-------------|
| **Pipeline complet** | `python3 main.py` | Traitement + Rapport |
| **Processors uniquement** | `python3 processors/main.py` | Traitement données |
| **Rapport uniquement** | `python3 report_generator/main.py` | Génération rapport |
| **API locale** | `python3 api/local_server.py` | Serveur API (port 5001) |
| **Tests API** | `python3 api/test_api.py` | Tests API |
| **Test BDD** | `python3 test_database_connection.py` | Test connexion |

---

## ✅ Checklist Ressources

### Code Source
- [x] Processors (6 types de données)
- [x] Report Generator
- [x] API REST (Lambda + Flask)
- [x] Base de données (MongoDB + DynamoDB)
- [x] Utilitaires partagés
- [x] Configuration

### Documentation
- [x] README principal
- [x] Guides d'installation
- [x] Guides d'exécution
- [x] Documentation API
- [x] Documentation architecture
- [x] Guides déploiement

### Données
- [x] Sources (API + Batch)
- [x] Métriques générées
- [x] Rapports générés

### Tests
- [x] Scripts de test
- [x] Tests API
- [x] Tests connexion BDD

---

## 🎉 Résumé

**Total Ressources :**
- 📄 **Fichiers Python** : ~40
- 📚 **Documentation** : 24 fichiers MD
- 📊 **Données sources** : 6 types
- 📤 **Résultats** : Métriques + Rapports
- 🧪 **Tests** : 3 scripts
- ⚙️ **Configuration** : .env, requirements.txt

**Le projet CityFlow Analytics est complet et opérationnel !** 🚀

