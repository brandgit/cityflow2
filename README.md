# CityFlow Analytics - Traitement des Données

## 📋 Vue d'Ensemble

Ce projet implémente une plateforme de traitement de données urbaines pour CityFlow Analytics. Il traite des données hétérogènes (API temps réel et batch) et génère des métriques et rapports quotidiens.

## 🏗️ Architecture

```
cityflow/
├── main.py                    # Point d'entrée principal
├── config/                    # Configuration centralisée
│   └── settings.py
├── processors/               # Processeurs par type de données
│   ├── base_processor.py     # Classe abstraite
│   ├── bikes_processor.py    # Compteurs vélos
│   ├── traffic_processor.py  # Perturbations RATP
│   ├── weather_processor.py  # Météo
│   ├── comptages_processor.py # Comptages routiers (CRITIQUE)
│   ├── chantiers_processor.py # Chantiers perturbants
│   └── referentiel_processor.py # Référentiel géographique
├── utils/                    # Utilitaires partagés
│   ├── validators.py         # Validation données
│   ├── aggregators.py        # Agrégations
│   ├── geo_utils.py          # Calculs géographiques
│   ├── time_utils.py         # Utilitaires temporels
│   ├── traffic_calculations.py # Calculs trafic (temps perdu)
│   └── file_utils.py         # Manipulation fichiers
└── models/                   # Modèles de données
    ├── traffic_metrics.py
    ├── bike_metrics.py
    ├── weather_metrics.py
    └── daily_report.py
```

## 🚀 Installation

1. **Installer les dépendances** (optionnel) :
```bash
pip install -r requirements.txt
```

Note: Le code fonctionne sans dépendances externes (gestion optionnelle de `holidays` et `dateutil`).

## 📊 Utilisation

### ⭐ Exécution Complète (Recommandé)

```bash
# Lance traitement + rapport automatiquement
python3 main.py

# Ou pour une date spécifique
python3 main.py 2025-11-03
```

Le pipeline :
1. Charge la configuration
2. Initialise tous les processeurs
3. Charge les données brutes depuis les répertoires configurés
4. Traite chaque type de données (validation → agrégation → calculs)
5. Exporte les métriques (MongoDB local ou DynamoDB AWS)
6. Génère le rapport quotidien
7. Exporte les rapports (fichiers locaux ou S3)

### 🔧 Exécution Manuelle (Étape par étape)

```bash
# Étape 1 : Traiter les données
python3 processors/main.py

# Étape 2 : Générer le rapport
python3 report_generator/main.py
```

### Structure des Traitements

Chaque processeur implémente 3 étapes :

1. **Validation & Nettoyage** (`validate_and_clean`)
   - Valide les coordonnées GPS, dates, GeoJSON
   - Détecte les valeurs aberrantes
   - Nettoie les données

2. **Agrégations Quotidiennes** (`aggregate_daily`)
   - Agrège par heure, arrondissement, tronçon
   - Calcule totaux, moyennes, pics

3. **Calculs d'Indicateurs** (`calculate_indicators`)
   - Calcule temps perdu, alertes congestion
   - Détecte anomalies, capteurs défaillants
   - Génère Top 10

### Processeur Comptages Routiers (Cas Critique)

Pour le fichier volumineux (6.2 GB), le processeur :
- Détecte automatiquement si fichier > 500 MB
- Découpe en chunks de 100,000 lignes
- Traite chaque chunk indépendamment
- Ré-agrège les résultats finaux

## 📁 Fichiers de Configuration

Les chemins sont définis dans `config/settings.py` :

- **Données Batch** : `bucket-cityflow-paris-s3-raw/cityflow-raw/raw/batch/`
- **Données API** : `bucket-cityflow-paris-s3-raw/cityflow-raw/raw/api/`
- **Output** : `output/` (créé automatiquement)

## 📤 Output Généré

Après exécution, les fichiers suivants sont créés :

```
output/
├── metrics/
│   ├── bikes_metrics_YYYY-MM-DD.json
│   ├── traffic_metrics_YYYY-MM-DD.json
│   ├── weather_metrics_YYYY-MM-DD.json
│   ├── comptages_metrics_YYYY-MM-DD.json
│   └── ...
└── reports/
    ├── daily_report_YYYY-MM-DD.json
    └── daily_report_YYYY-MM-DD.csv
```

### Format Rapport Quotidien JSON

```json
{
  "date": "2025-11-03",
  "summary": {
    "total_vehicules_paris": 1234567,
    "temps_perdu_total_minutes": 89456,
    "nombre_troncons_satures": 45
  },
  "top_10_troncons_frequentes": [...],
  "top_10_zones_congestionnees": [...],
  "alertes_congestion": [...],
  "capteurs_defaillants": [...]
}
```

## 🔧 Traitements Implémentés

### API Bikes
- ✅ Validation coordonnées GPS
- ✅ Détection capteurs défaillants
- ✅ Agrégation par compteur, arrondissement
- ✅ Calcul indice fréquentation cyclable

### API Traffic (RATP)
- ✅ Parsing disruptions et périodes
- ✅ Extraction lignes impactées
- ✅ Calcul taux fiabilité transport
- ✅ Alertes disruptions critiques

### API Weather
- ✅ Validation cohérence températures
- ✅ Catégorisation jour météo
- ✅ Calcul impact mobilité

### Batch Comptages Routiers ⚠️ CRITIQUE
- ✅ Découpe automatique gros fichiers
- ✅ Calcul débit horaire/journalier par tronçon
- ✅ **Calcul temps perdu** (formule complexe)
- ✅ Détection alertes congestion
- ✅ Top 10 tronçons fréquentés
- ✅ Top 10 zones congestionnées

### Batch Chantiers
- ✅ Détection chantiers actifs
- ✅ Agrégation par arrondissement
- ✅ Calcul impact estimé

### Référentiel Géographique
- ✅ Calcul longueurs tronçons
- ✅ Création table de mapping
- ✅ Enrichissement données

## 📝 Calcul Temps Perdu

Formule implémentée dans `utils/traffic_calculations.py` :

```
1. Vitesse observée = f(taux_occupation, vitesse_référence)
2. Temps normal = longueur / vitesse_référence
3. Temps observé = longueur / vitesse_observée
4. Temps perdu = temps_observé - temps_normal
5. Temps perdu total = temps_perdu × nombre_véhicules
```

## 🔍 Détection Anomalies

- Capteurs défaillants : inactifs > 6h ou valeur constante > 12h
- Anomalies trafic : variation > 300% vs historique
- Alertes congestion : taux occupation > 80% pendant > 2h

## 📚 Documentation

- `ARCHITECTURE_CODE.md` : Architecture détaillée
- `DIAGRAMME_ARCHITECTURE.md` : Diagrammes visuels
- `TRAITEMENTS_DONNEES.md` : Traitements par type de données
- `TABLEAU_RECAP_TRAITEMENTS.md` : Tableau récapitulatif

## ⚠️ Notes

- Les dépendances `holidays` et `dateutil` sont optionnelles
- Le code gère automatiquement leur absence
- Pour une précision maximale, installer `requirements.txt`

## 🐛 Dépannage

**Erreur import modules** :
```bash
# Vérifier que vous êtes dans le répertoire cityflow
pwd
# Doit afficher: .../cityflow
```

**Fichiers manquants** :
- Vérifier que les données sont dans `bucket-cityflow-paris-s3-raw/`
- Les chemins sont configurables dans `config/settings.py`

## 📈 Prochaines Étapes

Pour intégrer avec AWS :
1. Adapter les processeurs pour Lambda
2. Configurer S3 triggers
3. Implémenter DynamoDB writers
4. Configurer EventBridge pour traitement quotidien

