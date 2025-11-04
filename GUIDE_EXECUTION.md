# 🚀 Guide d'Exécution CityFlow Analytics

## Vue d'ensemble

CityFlow propose **3 façons d'exécuter** le traitement des données.

---

## 🎯 Option 1 : Pipeline Complet (Recommandé) ⭐

**Fichier :** `main.py`

Lance automatiquement :
1. ✅ Traitement des données (processors)
2. ✅ Génération du rapport

### Utilisation

```bash
# Traitement complet pour aujourd'hui
python3 main.py

# Traitement complet pour une date spécifique
python3 main.py 2025-11-03
```

### Exemple de sortie

```
======================================================================
  🚀 CityFlow Analytics - Pipeline Complet
======================================================================

📅 Date de traitement: 2025-11-03
🕐 Démarrage: 2025-11-03 20:30:00
🏠 Environnement: Local (Développement)

======================================================================
  ÉTAPE 1/2 : TRAITEMENT DES DONNÉES
======================================================================

🔄 Lancement du traitement des données...

============================================================
CityFlow Analytics - Traitement des Données
============================================================

[1/6] Chargement configuration...
✓ Configuration chargée

[2/6] Initialisation processeurs...
✓ 6 processeurs initialisés

[3/6] Chargement données brutes...
✓ 6 sources de données chargées

[4/6] Traitement des données...
  → Traitement référentiel géographique...
  → Traitement bikes...
    ✓ bikes traité avec succès
  → Traitement traffic...
    ✓ traffic traité avec succès
  → Traitement weather...
    ✓ weather traité avec succès
  → Traitement comptages...
    ✓ comptages traité avec succès
  → Traitement chantiers...
    ✓ chantiers traité avec succès

[5/6] Enrichissement multi-sources...
✓ Enrichissement terminé

[6/6] Export des métriques...
✓ 6 types de métriques exportés vers MONGODB

✓ Traitement des données terminé avec succès

======================================================================
  ÉTAPE 2/2 : GÉNÉRATION DU RAPPORT
======================================================================

📊 Lancement de la génération du rapport...

============================================================
CityFlow Analytics - Génération Rapport Quotidien
============================================================

[1/3] Chargement des métriques...
  ✓ Métriques comptages chargées depuis MONGODB
  ✓ Métriques bikes chargées depuis MONGODB
  ✓ Métriques traffic chargées depuis MONGODB
  ✓ Métriques weather chargées depuis MONGODB
✓ 4 fichiers métriques chargés

[2/3] Extraction des données...
  ✓ Top 10 tronçons: 10 éléments
  ✓ Top 10 zones: 10 éléments

[3/3] Génération rapport...
✓ Rapport généré avec succès

[Export CSV] → Répertoire local (output/reports/)
✓ Rapport CSV: output/reports/daily_report_2025-11-03.csv

[Export JSON] → MONGODB
✓ Rapport JSON exporté vers MONGODB

============================================================
🏠 Rapport exporté en mode LOCAL DÉVELOPPEMENT
   - CSV : Répertoire local (output/reports/)
   - JSON : MONGODB
============================================================

✓ Génération du rapport terminée avec succès

======================================================================
  ✅ SUCCÈS : Pipeline complet terminé
======================================================================

⏱️  Durée totale: 45.23 secondes (0.75 minutes)
🕐 Fin: 2025-11-03 20:30:45

📂 Fichiers générés:
   📊 Métriques: output/metrics/*_metrics_2025-11-03.json
   📈 Rapport CSV: output/reports/daily_report_2025-11-03.csv
   📄 Rapport JSON: output/reports/daily_report_2025-11-03.json
   💾 Base de données: MongoDB (collection metrics + reports)

💡 Pour visualiser:
   - MongoDB Compass: mongodb://localhost:27017/
   - Fichiers locaux: ls -lh output/reports/

======================================================================
```

### Avantages

✅ Une seule commande  
✅ Pipeline automatisé  
✅ Gestion des erreurs  
✅ Timer et statistiques  
✅ Résumé complet

---

## 🔧 Option 2 : Exécution Manuelle (Étape par étape)

### 2.1 Traiter les données

```bash
python3 processors/main.py
```

**Ce qui se passe :**
- Charge les données brutes
- Traite chaque type de données
- Calcule les métriques
- Exporte vers MongoDB (local) ou DynamoDB (AWS)

### 2.2 Générer le rapport

```bash
python3 report_generator/main.py [date]
```

**Ce qui se passe :**
- Charge les métriques depuis la base de données
- Génère le rapport quotidien
- Exporte CSV + JSON

### Avantages

✅ Contrôle fin sur chaque étape  
✅ Debug plus facile  
✅ Peut relancer seulement une partie

---

## 🤖 Option 3 : Script Shell Automatique

**Fichier :** `setup_and_run.sh`

```bash
./setup_and_run.sh
```

Configure l'environnement et lance le pipeline complet.

---

## 📋 Comparaison des options

| Option | Commande | Avantages | Cas d'usage |
|--------|----------|-----------|-------------|
| **1. Pipeline complet** | `python3 main.py` | ⭐ Simple, Automatisé | Production, Usage quotidien |
| **2. Manuelle** | `python3 processors/main.py` + `python3 report_generator/main.py` | Contrôle fin | Debug, Développement |
| **3. Script shell** | `./setup_and_run.sh` | Setup auto | Première installation |

---

## 🌍 Comportement selon l'environnement

### 🏠 Mode LOCAL (Développement)

```bash
# Configuration automatique via .env
DATABASE_TYPE=mongodb
```

**Stockage :**
- Métriques → MongoDB (collection `metrics`) + fichiers JSON locaux
- Rapport JSON → MongoDB (collection `reports`)
- Rapport CSV → `output/reports/`

### ☁️ Mode AWS (Production)

```bash
# Détection automatique via AWS_EXECUTION_ENV
```

**Stockage :**
- Métriques → DynamoDB (table `cityflow-metrics`)
- Rapport JSON → DynamoDB (table `cityflow-daily-reports`)
- Rapport CSV → S3 (bucket `cityflow-reports`)

---

## 🎯 Exemples d'utilisation

### Traitement quotidien automatique

```bash
# Ajouter dans crontab pour exécution automatique tous les jours à 6h
0 6 * * * cd /path/to/cityflow && python3 main.py >> logs/cron.log 2>&1
```

### Retraiter une date spécifique

```bash
# Retraiter les données du 1er novembre
python3 main.py 2025-11-01
```

### Traiter plusieurs dates

```bash
# Script bash pour traiter une période
for date in 2025-11-{01..07}; do
    echo "Traitement de $date..."
    python3 main.py $date
done
```

### Debug d'une étape spécifique

```bash
# Seulement le traitement
python3 processors/main.py

# Seulement le rapport (si métriques déjà générées)
python3 report_generator/main.py
```

---

## 🐛 Gestion des erreurs

### Le pipeline gère automatiquement :

✅ **Erreur dans processors** : S'arrête avant la génération du rapport
```
❌ ÉCHEC : Le traitement des données a échoué
```

✅ **Erreur dans le rapport** : Métriques sauvegardées, rapport échoué
```
⚠️  PARTIEL : Traitement OK, mais rapport échoué
```

✅ **Interruption manuelle** : Ctrl+C proprement géré
```
⚠️  Interruption par l'utilisateur (Ctrl+C)
```

---

## 📊 Vérifier les résultats

### Fichiers locaux

```bash
# Métriques générées
ls -lh output/metrics/

# Rapports générés
ls -lh output/reports/

# Afficher le rapport CSV
cat output/reports/daily_report_2025-11-03.csv

# Afficher le rapport JSON
cat output/reports/daily_report_2025-11-03.json | jq
```

### MongoDB (local)

```bash
# Se connecter à MongoDB
mongosh cityflow

# Voir les métriques
db.metrics.find().limit(5).pretty()

# Voir les rapports
db.reports.find().pretty()

# Compter les documents
db.metrics.countDocuments()
db.reports.countDocuments()
```

### MongoDB Compass (interface graphique)

1. Ouvrir MongoDB Compass
2. Se connecter à `mongodb://localhost:27017/`
3. Sélectionner la base `cityflow`
4. Explorer les collections `metrics` et `reports`

---

## ⚡ Optimisations

### Traitement parallèle (futur)

```bash
# Traiter plusieurs dates en parallèle
python3 main.py 2025-11-01 &
python3 main.py 2025-11-02 &
python3 main.py 2025-11-03 &
wait
```

### Cache des données

Les métriques sont sauvegardées dans MongoDB, donc :
- ✅ Pas besoin de retraiter si déjà fait
- ✅ Génération de rapport rapide

---

## 🎓 Commandes rapides

```bash
# Pipeline complet (recommandé)
python3 main.py

# Pipeline pour une date
python3 main.py 2025-11-03

# Juste le traitement
python3 processors/main.py

# Juste le rapport
python3 report_generator/main.py

# Test de connexion BDD
python3 test_database_connection.py

# Voir les logs
tail -f logs/cityflow.log  # Si logs configurés
```

---

## 📚 Documentation connexe

- `MONGODB_SETUP.md` - Installation MongoDB
- `LOGIQUE_EXPORT_RAPPORTS.md` - Détails export selon environnement
- `ARCHITECTURE_BDD.md` - Architecture base de données
- `GUIDE_MIGRATION_MONGODB.md` - Migration MongoDB/DynamoDB

---

## ✅ Checklist avant exécution

- [ ] MongoDB est démarré (local) ou AWS configuré (production)
- [ ] `.env` configuré avec `DATABASE_TYPE`
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Données sources présentes dans `bucket-cityflow-paris-s3-raw/`
- [ ] Permissions en écriture sur `output/`

---

**Tout est prêt ! Lancez simplement `python3 main.py` ! 🚀**

