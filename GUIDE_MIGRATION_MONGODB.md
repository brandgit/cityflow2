# 🎉 Guide de Migration MongoDB - CityFlow Analytics

## ✅ Ce qui a été implémenté

L'architecture hybride MongoDB/DynamoDB est maintenant **complètement opérationnelle** !

---

## 📦 Fichiers créés

### 1. **Couche d'abstraction**

✅ `utils/database_service.py` - Interface abstraite commune  
✅ `utils/mongodb_service.py` - Implémentation MongoDB pour local  
✅ `utils/dynamodb_service_adapter.py` - Adaptateur DynamoDB pour production  
✅ `utils/database_factory.py` - Factory pour choisir automatiquement

### 2. **Fichiers modifiés**

✅ `processors/main.py` - Utilise maintenant `get_database_service()`  
✅ `report_generator/daily_report_generator.py` - Utilise maintenant `get_database_service()`  
✅ `.env` - Ajout configuration MongoDB  
✅ `env.example` - Ajout configuration MongoDB  
✅ `requirements.txt` - Ajout pymongo

### 3. **Documentation**

✅ `MONGODB_SETUP.md` - Guide complet installation MongoDB  
✅ `ARCHITECTURE_BDD.md` - Architecture détaillée  
✅ `test_database_connection.py` - Script de test connexion  
✅ `GUIDE_MIGRATION_MONGODB.md` - Ce fichier

---

## 🚀 Installation (3 étapes)

### Étape 1 : Installer MongoDB

#### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Windows
1. Télécharger : https://www.mongodb.com/try/download/community
2. Installer avec options par défaut
3. MongoDB démarre automatiquement

#### Linux
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

### Étape 2 : Installer MongoDB Compass (Interface Graphique)

Télécharger : https://www.mongodb.com/try/download/compass

Connecter à : `mongodb://localhost:27017/`

### Étape 3 : Installer les dépendances Python

```bash
cd /Users/brandbetsaleltikouetikoue/Desktop/EFREI_PARIS/M1/introduction-au-cloud-camputing/cityflow

# Installer pymongo
pip3 install pymongo

# Ou installer toutes les dépendances
pip3 install -r requirements.txt
```

---

## 🧪 Test de connexion

```bash
# Tester la connexion à la base de données
python3 test_database_connection.py
```

**Sortie attendue si OK** :
```
============================================================
📦 Base de données: MongoDB (développement local)
============================================================
✓ Connecté à MongoDB: mongodb://localhost:27017/ / cityflow
✓ Connexion à la base de données OK

============================================================
✅ SUCCÈS : La connexion fonctionne correctement!
============================================================
```

---

## 📊 Utilisation

### 1. Traiter les données (sauvegarde dans MongoDB)

```bash
python3 processors/main.py
```

**Ce qui se passe** :
1. ✅ Charge les données brutes depuis `bucket-cityflow-paris-s3-raw/`
2. ✅ Traite chaque type de données (bikes, traffic, weather, etc.)
3. ✅ Calcule les métriques
4. ✅ **Sauvegarde dans MongoDB** (collection `metrics`)
5. ✅ Sauvegarde aussi en local (backup) dans `output/metrics/`

**Sortie attendue** :
```
============================================================
📦 Base de données: MongoDB (développement local)
============================================================
✓ Connecté à MongoDB: mongodb://localhost:27017/ / cityflow
...
[4/6] Traitement des données...
  → Traitement bikes...
    ✓ bikes traité avec succès
...
[6/6] Export des métriques...
✓ Métriques bikes exportées vers MONGODB
  ✓ Nouvelles métriques bikes insérées (ID: 673...)
  → Sauvegarde locale (backup): output/metrics/bikes_metrics_2025-11-03.json
...
✓ 6 types de métriques exportés vers MONGODB
```

### 2. Générer le rapport (lecture depuis MongoDB)

```bash
python3 report_generator/main.py
```

**Ce qui se passe** :
1. ✅ **Charge les métriques depuis MongoDB**
2. ✅ Génère le rapport quotidien
3. ✅ **Sauvegarde le rapport dans MongoDB** (collection `reports`)
4. ✅ Sauvegarde aussi en local (CSV et JSON) dans `output/reports/`

**Sortie attendue** :
```
============================================================
📦 Base de données: MongoDB (développement local)
============================================================
✓ Connecté à MongoDB: mongodb://localhost:27017/ / cityflow
...
  ✓ Métriques comptages chargées depuis MONGODB
  ✓ Métriques bikes chargées depuis MONGODB
  ✓ Métriques traffic chargées depuis MONGODB
  ✓ Métriques weather chargées depuis MONGODB
  ✓ Métriques chantiers chargées depuis MONGODB
...
✓ Rapport généré avec succès
✓ Rapport CSV: output/reports/daily_report_2025-11-03.csv
✓ Rapport JSON exporté vers MONGODB
  ✓ Nouveau rapport inséré (ID: 673...)
```

### 3. Visualiser dans MongoDB Compass

1. Ouvrir MongoDB Compass
2. Se connecter à `mongodb://localhost:27017/`
3. Sélectionner la base de données **`cityflow`**
4. Explorer les collections :
   - **`metrics`** : Toutes les métriques par type et date
   - **`reports`** : Tous les rapports générés

**Exemples de requêtes** :

```javascript
// Voir toutes les métriques du jour
{ "date": "2025-11-03" }

// Voir les métriques bikes uniquement
{ "metric_type": "bikes", "date": "2025-11-03" }

// Voir le dernier rapport
// (Trier par date décroissante, limite 1)
```

---

## 🔄 Basculer vers DynamoDB (Production)

Quand vous déployez sur AWS :

### 1. Modifier `.env`

```bash
# Changer une seule ligne !
DATABASE_TYPE=dynamodb

# S'assurer que les configs AWS sont définies
AWS_REGION=us-east-1
DYNAMODB_METRICS_TABLE=cityflow-metrics
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports
```

### 2. Configurer AWS CLI

```bash
aws configure
```

### 3. Créer les tables DynamoDB

```bash
# Table métriques
aws dynamodb create-table \
  --table-name cityflow-metrics \
  --attribute-definitions \
    AttributeName=metric_type,AttributeType=S \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=metric_type,KeyType=HASH \
    AttributeName=date,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Table rapports
aws dynamodb create-table \
  --table-name cityflow-daily-reports \
  --attribute-definitions \
    AttributeName=report_id,AttributeType=S \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=report_id,KeyType=HASH \
    AttributeName=date,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 4. Exécuter normalement

```bash
python3 processors/main.py
```

**Le code bascule automatiquement vers DynamoDB !** 🎉

---

## 📁 Structure MongoDB

### Collection `metrics`

```javascript
{
  "_id": ObjectId("673abc123..."),
  "metric_type": "bikes",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T14:30:00",
  "metrics": {
    "total_passages": 15234,
    "moyenne_passages_par_compteur": 127.8,
    "total_compteurs_actifs": 119,
    "top_10_compteurs": [...]
  },
  "created_at": ISODate("2025-11-03T14:30:00.000Z"),
  "updated_at": ISODate("2025-11-03T14:30:00.000Z")
}
```

### Collection `reports`

```javascript
{
  "_id": ObjectId("673def456..."),
  "report_id": "daily_report_2025-11-03",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T15:00:00",
  "report": {
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
  },
  "created_at": ISODate("2025-11-03T15:00:00.000Z"),
  "updated_at": ISODate("2025-11-03T15:00:00.000Z")
}
```

---

## 🎯 Avantages de cette implémentation

| Avantage | Description |
|----------|-------------|
| ✅ **Flexibilité** | Changer de BDD en 1 ligne dans `.env` |
| ✅ **Développement rapide** | Pas besoin de AWS en local |
| ✅ **Visualisation** | MongoDB Compass = interface graphique intuitive |
| ✅ **Performance locale** | Pas de latence réseau |
| ✅ **Gratuit** | MongoDB Community Edition gratuit |
| ✅ **Production ready** | DynamoDB scale automatiquement |
| ✅ **Code unifié** | Même interface pour MongoDB et DynamoDB |
| ✅ **Backup automatique** | Fichiers JSON locaux en développement |

---

## 🐛 Dépannage

### Erreur : "Connection refused"

**Problème** : MongoDB n'est pas démarré

**Solution** :
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Vérifier le statut
mongosh --eval "db.version()"
```

### Erreur : "pymongo non disponible"

**Problème** : Librairie non installée

**Solution** :
```bash
pip3 install pymongo
```

### MongoDB Compass ne se connecte pas

**Vérifier que MongoDB fonctionne** :
```bash
mongosh --eval "db.version()"
```

Si erreur, redémarrer MongoDB.

---

## 📚 Fichiers de référence

- `MONGODB_SETUP.md` - Installation détaillée MongoDB
- `ARCHITECTURE_BDD.md` - Architecture technique
- `test_database_connection.py` - Test de connexion
- `.env` - Configuration DATABASE_TYPE

---

## 🎓 Résumé

### Avant (code original)
```python
# Hardcodé pour DynamoDB uniquement
save_metrics_to_dynamodb(metrics, type, date)
```

### Après (nouvelle architecture)
```python
# Flexible : MongoDB ou DynamoDB selon .env
db_service = get_database_service()
db_service.save_metrics(metrics, type, date)
```

**Un seul changement** dans `.env` et tout bascule ! 🚀

---

## ✅ Pour commencer maintenant

```bash
# 1. Installer MongoDB
brew install mongodb-community  # macOS
brew services start mongodb-community

# 2. Installer pymongo
pip3 install pymongo

# 3. Tester la connexion
python3 test_database_connection.py

# 4. Traiter les données
python3 processors/main.py

# 5. Générer le rapport
python3 report_generator/main.py

# 6. Visualiser dans MongoDB Compass
# Ouvrir Compass → mongodb://localhost:27017/ → Database: cityflow
```

**C'est tout ! Vous êtes prêt ! 🎉**

