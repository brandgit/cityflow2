# 🏗️ Architecture Base de Données - CityFlow Analytics

## Vue d'ensemble

CityFlow utilise une **architecture hybride flexible** qui permet de basculer facilement entre MongoDB (développement local) et DynamoDB (production AWS) sans modifier le code.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│  (processors/main.py, report_generator/main.py)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Factory (database_factory.py)         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  get_database_service() → Retourne le bon service │    │
│  │  - Si DATABASE_TYPE=mongodb → MongoDBService       │    │
│  │  - Si DATABASE_TYPE=dynamodb → DynamoDBAdapter     │    │
│  │  - Si AWS_EXECUTION_ENV → DynamoDBAdapter          │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐     ┌──────────────────────────┐
│  MongoDBService     │     │ DynamoDBServiceAdapter   │
│  (local)            │     │ (production AWS)         │
├─────────────────────┤     ├──────────────────────────┤
│ - save_metrics()    │     │ - save_metrics()         │
│ - load_metrics()    │     │ - load_metrics()         │
│ - save_report()     │     │ - save_report()          │
│ - load_report()     │     │ - load_report()          │
│ - query_by_date()   │     │ - query_by_date()        │
└──────────┬──────────┘     └────────────┬─────────────┘
           │                             │
           ▼                             ▼
    ┌──────────────┐            ┌────────────────┐
    │   MongoDB    │            │   DynamoDB     │
    │  (localhost) │            │   (AWS Cloud)  │
    └──────────────┘            └────────────────┘
```

---

## 🔧 Composants

### 1. Interface Abstraite : `DatabaseService`

Définit le contrat commun pour tous les services de base de données.

**Fichier** : `utils/database_service.py`

**Méthodes** :
- `save_metrics(metrics, data_type, date)` : Sauvegarde des métriques
- `load_metrics(data_type, date)` : Charge des métriques
- `save_report(report, date)` : Sauvegarde un rapport
- `load_report(date)` : Charge un rapport
- `query_metrics_by_date_range(data_type, start, end)` : Requête sur plage de dates

### 2. Implémentation MongoDB : `MongoDBService`

Service pour développement local avec MongoDB.

**Fichier** : `utils/mongodb_service.py`

**Caractéristiques** :
- ✅ Connexion à MongoDB local (localhost:27017)
- ✅ Gestion automatique des index
- ✅ Upsert pour éviter les doublons
- ✅ Support du context manager
- ✅ Gestion des erreurs de connexion

**Collections** :
- `metrics` : Stocke les métriques par type et date
- `reports` : Stocke les rapports quotidiens

**Index créés** :
```javascript
metrics.createIndex({ metric_type: 1, date: 1 }, { unique: true })
metrics.createIndex({ date: 1 })
reports.createIndex({ date: 1 }, { unique: true })
```

### 3. Adaptateur DynamoDB : `DynamoDBServiceAdapter`

Adaptateur qui réutilise les fonctions existantes dans `aws_services.py`.

**Fichier** : `utils/dynamodb_service_adapter.py`

**Caractéristiques** :
- ✅ Réutilise `save_metrics_to_dynamodb()` existant
- ✅ Réutilise `load_metrics_from_dynamodb()` existant
- ✅ Mode simulation si boto3 non disponible
- ✅ Support TTL pour expiration automatique

### 4. Factory : `database_factory.py`

Fabrique qui choisit automatiquement le bon service.

**Fichier** : `utils/database_factory.py`

**Logique de sélection** :
1. Si `AWS_EXECUTION_ENV` existe → **DynamoDB** (Lambda/EC2)
2. Si `DATABASE_TYPE=dynamodb` → **DynamoDB**
3. Si `DATABASE_TYPE=mongodb` → **MongoDB**
4. Par défaut → **MongoDB**

---

## 🎯 Utilisation

### Configuration via `.env`

#### Développement local (MongoDB)
```bash
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=cityflow
```

#### Production AWS (DynamoDB)
```bash
DATABASE_TYPE=dynamodb
AWS_REGION=us-east-1
DYNAMODB_METRICS_TABLE=cityflow-metrics
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports
```

### Dans le code

```python
from utils.database_factory import get_database_service

# Obtenir le service (MongoDB ou DynamoDB selon config)
db_service = get_database_service()

# Sauvegarder des métriques
db_service.save_metrics(
    metrics={"total": 1234, "moyenne": 56.7},
    data_type="bikes",
    date="2025-11-03"
)

# Charger des métriques
metrics = db_service.load_metrics(
    data_type="bikes",
    date="2025-11-03"
)

# Fermer la connexion (si MongoDB)
if hasattr(db_service, 'close'):
    db_service.close()
```

---

## 📊 Modèle de données

### Structure Métriques

**MongoDB** :
```javascript
{
  "_id": ObjectId("..."),
  "metric_type": "bikes",           // Type: bikes, traffic, weather, etc.
  "date": "2025-11-03",             // Date au format YYYY-MM-DD
  "timestamp": "2025-11-03T14:30",  // Timestamp de sauvegarde
  "metrics": {                       // Métriques calculées
    "total_passages": 15234,
    "moyenne": 127.8,
    "top_10": [...]
  },
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

**DynamoDB** :
```javascript
{
  "metric_type": "bikes",            // Partition Key
  "date": "2025-11-03",              // Sort Key
  "timestamp": "2025-11-03T14:30",
  "metrics": {
    "total_passages": 15234,
    "moyenne": 127.8,
    "top_10": [...]
  },
  "ttl": 1735689600                  // Expiration (1 an)
}
```

### Structure Rapports

**MongoDB** :
```javascript
{
  "_id": ObjectId("..."),
  "report_id": "daily_report_2025-11-03",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T15:00",
  "report": {
    "date": "2025-11-03",
    "summary": {...},
    "top_10_troncons": [...],
    // ...
  },
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

**DynamoDB** :
```javascript
{
  "report_id": "daily_report_2025-11-03",  // Partition Key
  "date": "2025-11-03",                     // Sort Key
  "timestamp": "2025-11-03T15:00",
  "report": {
    "date": "2025-11-03",
    "summary": {...},
    "top_10_troncons": [...],
    // ...
  },
  "ttl": 1735689600
}
```

---

## 🔄 Migration

### De MongoDB vers DynamoDB

1. **Changer la configuration** :
   ```bash
   # Dans .env
   DATABASE_TYPE=dynamodb
   ```

2. **Configurer AWS** :
   ```bash
   aws configure
   ```

3. **Créer les tables DynamoDB** :
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
     --billing-mode PAY_PER_REQUEST

   # Table rapports
   aws dynamodb create-table \
     --table-name cityflow-daily-reports \
     --attribute-definitions \
       AttributeName=report_id,AttributeType=S \
       AttributeName=date,AttributeType=S \
     --key-schema \
       AttributeName=report_id,KeyType=HASH \
       AttributeName=date,KeyType=RANGE \
     --billing-mode PAY_PER_REQUEST
   ```

4. **Exécuter normalement** : Le code bascule automatiquement !

### De DynamoDB vers MongoDB

1. **Installer MongoDB** (voir `MONGODB_SETUP.md`)

2. **Changer la configuration** :
   ```bash
   # Dans .env
   DATABASE_TYPE=mongodb
   ```

3. **Exécuter normalement** : Le code bascule automatiquement !

---

## 🚀 Avantages de cette architecture

| Avantage | Description |
|----------|-------------|
| **Flexibilité** | Basculer entre MongoDB et DynamoDB en changeant 1 ligne |
| **Testabilité** | Tester en local sans AWS |
| **Performance** | MongoDB local = pas de latence réseau |
| **Coût** | MongoDB local = gratuit, DynamoDB = pay-per-use |
| **Scalabilité** | DynamoDB scale automatiquement en production |
| **Maintenabilité** | Interface unique, code unifié |

---

## 📝 Résumé des fichiers

```
utils/
├── database_service.py          # Interface abstraite
├── mongodb_service.py           # Implémentation MongoDB
├── dynamodb_service_adapter.py  # Adaptateur DynamoDB
├── database_factory.py          # Factory pour choisir le service
└── aws_services.py              # Fonctions DynamoDB existantes

processors/
└── main.py                      # Utilise get_database_service()

report_generator/
└── daily_report_generator.py    # Utilise get_database_service()

config/
├── .env                         # Configuration DATABASE_TYPE
└── settings.py                  # Paramètres globaux

docs/
├── MONGODB_SETUP.md             # Guide installation MongoDB
└── ARCHITECTURE_BDD.md          # Ce fichier
```

---

## 🎓 Pour aller plus loin

- **MongoDB** : https://docs.mongodb.com/
- **DynamoDB** : https://docs.aws.amazon.com/dynamodb/
- **Design Patterns** : Factory Pattern, Adapter Pattern
- **SOLID Principles** : Dependency Inversion Principle

