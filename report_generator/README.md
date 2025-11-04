# Report Generator - Génération de Rapports Quotidiens

## 📋 Description

Module **séparé et indépendant** pour générer les rapports quotidiens à partir des métriques calculées.

**Conçu pour s'exécuter dans une instance AWS distincte** du traitement principal.

## 🏗️ Structure

```
report_generator/
├── __init__.py
├── main.py                        # ✨ Point d'entrée principal (instance séparée)
├── daily_report_generator.py      # Classe principale DailyReportGenerator
└── README.md                      # Documentation
```

## 🚀 Utilisation

### Exécution Standalone

```bash
# Générer le rapport pour aujourd'hui
python report_generator/main.py

# Générer le rapport pour une date spécifique
python report_generator/main.py 2025-11-03

# Avec variable d'environnement (AWS Lambda)
REPORT_DATE=2025-11-03 python report_generator/main.py
```

### Utilisation Programmée

```python
from report_generator import DailyReportGenerator

# Initialiser le générateur
generator = DailyReportGenerator()

# Générer et exporter en une fois
files = generator.generate_and_export("2025-11-03")

# OU étape par étape
report = generator.generate_report("2025-11-03")
files = generator.export_report(report)
```

## 📊 Fonctionnement

### 1. Chargement des Métriques

Lit les fichiers JSON depuis `output/metrics/` (ou S3 en production) :
- ✅ `comptages_metrics_YYYY-MM-DD.json`
- ✅ `bikes_metrics_YYYY-MM-DD.json`
- ✅ `weather_metrics_YYYY-MM-DD.json`
- ✅ `chantiers_metrics_YYYY-MM-DD.json`
- ✅ `traffic_metrics_YYYY-MM-DD.json` (optionnel)

### 2. Génération du Rapport

Combine toutes les métriques dans un `DailyReport` avec :
- Summary (totaux, temps perdu, tronçons saturés)
- Top 10 tronçons fréquentés
- Top 10 zones congestionnées
- Capteurs défaillants
- Alertes congestion
- Chantiers actifs
- Impact météo

### 3. Export

Génère deux fichiers dans `output/reports/` (ou S3) :
- `daily_report_YYYY-MM-DD.json` (complet)
- `daily_report_YYYY-MM-DD.csv` (format tabulaire)

## 📝 Prérequis

**Les métriques doivent avoir été calculées préalablement** par le traitement principal :

```bash
# Étape 1: Traitement (instance séparée)
python main.py

# Étape 2: Génération rapport (cette instance)
python report_generator/main.py
```

## 🏛️ Architecture AWS

### Instance Séparée

Ce module s'exécute dans une **Lambda ou EC2 distincte** :

```
EventBridge (00:30 UTC)
    │
    ▼
Lambda/EC2 Instance 2
    │
    ├─→ Lit métriques depuis S3
    ├─→ Génère rapport
    └─→ Upload rapport → S3
```

**Variables d'environnement AWS** :
- `S3_BUCKET_METRICS_PATH` : Chemin S3 des métriques
- `S3_BUCKET_REPORTS_PATH` : Chemin S3 pour rapports
- `REPORT_DATE` : Date du rapport (optionnel)

## ✅ Avantages de la Séparation

1. ✅ **Séparation des responsabilités** : Traitement ≠ Génération rapport
2. ✅ **Instances distinctes AWS** : Scalabilité indépendante
3. ✅ **Réutilisable** : Régénérer rapport sans retraiter données
4. ✅ **Flexible** : Générer plusieurs rapports (dates différentes)
5. ✅ **Robuste** : Échec traitement n'empêche pas régénération rapport

## 🔍 Logs et Monitoring

Le module affiche :
- Nombre de métriques chargées
- Éléments extraits (Top 10, alertes, etc.)
- Chemins fichiers générés
- Erreurs si métriques manquantes

## 📁 Fichiers Générés

Le rapport quotidien contient :

**JSON** (`daily_report_YYYY-MM-DD.json`) :
- Structure complète avec toutes les données
- Utilisé pour API, intégration, traitement automatisé

**CSV** (`daily_report_YYYY-MM-DD.csv`) :
- Format tabulaire lisible
- Utilisé pour Excel, consultation rapide, partage
