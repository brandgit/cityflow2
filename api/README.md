# 🌐 CityFlow Analytics API REST

## Vue d'ensemble

API REST pour exposer les métriques et rapports CityFlow Analytics.

**Architecture hybride :**
- 🏠 **Développement local** : Flask + MongoDB
- ☁️ **Production AWS** : API Gateway + Lambda + DynamoDB

---

## 📂 Structure

```
api/
├── __init__.py                    # Package API
├── lambda_function.py             # Handler AWS Lambda (point d'entrée)
├── local_server.py                # Serveur Flask pour développement local
├── handlers/                      # Handlers par endpoint
│   ├── __init__.py
│   ├── metrics_handler.py         # GET métriques
│   ├── report_handler.py          # GET rapports
│   └── stats_handler.py           # GET statistiques
├── utils/                         # Utilitaires API
│   ├── __init__.py
│   ├── response.py                # Formatage réponses HTTP
│   └── validation.py              # Validation paramètres
└── README.md                      # Ce fichier
```

---

## 🚀 Démarrage Rapide

### 🏠 Mode Local (Développement)

#### 1. Installer les dépendances

```bash
pip install flask flask-cors
```

#### 2. Démarrer le serveur

```bash
python3 api/local_server.py
```

**Serveur démarré sur** : `http://localhost:5000`

#### 3. Tester les endpoints

```bash
# Health check
curl http://localhost:5000/health

# Statistiques
curl http://localhost:5000/stats

# Métriques bikes
curl http://localhost:5000/metrics/bikes/2025-11-03

# Toutes les métriques
curl http://localhost:5000/metrics/2025-11-03

# Rapport quotidien
curl http://localhost:5000/report/2025-11-03
```

---

### ☁️ Mode AWS Lambda (Production)

#### 1. Packager le code

```bash
# Créer un package de déploiement
cd /path/to/cityflow
zip -r api-lambda.zip api/ utils/ config/ models/ -x "*.pyc" -x "__pycache__/*"
```

#### 2. Créer la fonction Lambda

```bash
aws lambda create-function \
  --function-name cityflow-api \
  --runtime python3.10 \
  --handler api.lambda_function.lambda_handler \
  --zip-file fileb://api-lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{DATABASE_TYPE=dynamodb,DYNAMODB_METRICS_TABLE=cityflow-metrics}"
```

#### 3. Créer l'API Gateway

```bash
# Créer API REST
aws apigateway create-rest-api \
  --name cityflow-api \
  --description "CityFlow Analytics API"

# Créer les ressources et méthodes
# Configurer intégration Lambda
# Déployer sur stage "prod"
```

#### 4. Tester

```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health
```

---

## 📡 Endpoints

### 🏥 Health Check

**GET** `/health`

Vérifie que l'API fonctionne.

**Réponse :**
```json
{
  "status": "healthy",
  "service": "CityFlow Analytics API",
  "version": "1.0.0",
  "database": "mongodb",
  "environment": "Local"
}
```

---

### 📊 Statistiques

**GET** `/stats`

Statistiques globales de l'API.

**Réponse :**
```json
{
  "api_version": "1.0.0",
  "database_type": "mongodb",
  "environment": "Local",
  "timestamp": "2025-11-03T20:00:00",
  "metric_types_available": ["bikes", "traffic", "weather", "comptages", "chantiers", "referentiel"],
  "database_stats": {
    "metrics_count": 5,
    "reports_count": 1
  }
}
```

---

### 🚴 Métriques Spécifiques

**GET** `/metrics/{type}/{date}`

Récupère les métriques d'un type spécifique.

**Paramètres :**
- `type` : Type de métrique (`bikes`, `traffic`, `weather`, `comptages`, `chantiers`, `referentiel`)
- `date` : Date au format `YYYY-MM-DD`

**Exemples :**

```bash
# Métriques vélos du 3 novembre
curl http://localhost:5000/metrics/bikes/2025-11-03

# Perturbations RATP
curl http://localhost:5000/metrics/traffic/2025-11-03

# Comptages routiers (version summary si MongoDB)
curl http://localhost:5000/metrics/comptages/2025-11-03
```

**Réponse :**
```json
{
  "metric_type": "bikes",
  "date": "2025-11-03",
  "data": {
    "metrics": [
      {
        "id_compteur": "100007049-101007049",
        "nom_compteur": "28 boulevard Diderot O-E",
        "total_jour": 57.0,
        "moyenne_horaire": 2.375,
        "arrondissement": "75012",
        "coordinates": {"lon": 2.37559, "lat": 48.84613}
      }
      // ... autres compteurs
    ],
    "top_counters": [...],
    "failing_sensors": [...]
  }
}
```

---

### 📈 Toutes les Métriques

**GET** `/metrics/{date}`

Récupère toutes les métriques pour une date.

**Exemple :**
```bash
curl http://localhost:5000/metrics/2025-11-03
```

**Réponse :**
```json
{
  "date": "2025-11-03",
  "metrics": {
    "bikes": {...},
    "traffic": {...},
    "weather": {...},
    "comptages": {...},
    "chantiers": {...},
    "referentiel": {...}
  }
}
```

---

### 📋 Rapport Quotidien

**GET** `/report/{date}`

Récupère le rapport quotidien complet.

**Exemple :**
```bash
curl http://localhost:5000/report/2025-11-03
```

**Réponse :**
```json
{
  "date": "2025-11-03",
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
  }
}
```

---

## 🔒 Gestion de la Base de Données

L'API bascule **automatiquement** entre MongoDB et DynamoDB :

### 🏠 En Local
```bash
# .env
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=cityflow
```

**L'API utilise** : MongoDB local

### ☁️ En AWS Lambda
```bash
# Variables d'environnement Lambda
DATABASE_TYPE=dynamodb
DYNAMODB_METRICS_TABLE=cityflow-metrics
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports
```

**L'API utilise** : DynamoDB

**Aucune modification de code nécessaire !**

---

## 🧪 Tests

### Test local avec curl

```bash
# Health check
curl http://localhost:5000/health | jq

# Stats
curl http://localhost:5000/stats | jq

# Métriques bikes
curl http://localhost:5000/metrics/bikes/2025-11-03 | jq '.data.metrics | length'

# Rapport
curl http://localhost:5000/report/2025-11-03 | jq '.report.summary'
```

### Test avec navigateur

Ouvrir dans un navigateur :
- http://localhost:5000
- http://localhost:5000/docs
- http://localhost:5000/metrics/bikes/2025-11-03

---

## 🔐 CORS

Le serveur local et Lambda sont configurés avec **CORS activé** :

```python
headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
}
```

Permet l'accès depuis :
- ✅ Applications web (React, Vue, Angular)
- ✅ Postman, Insomnia
- ✅ curl, wget
- ✅ Mobile apps

---

## 🚀 Déploiement AWS

### Prérequis

- AWS CLI configuré
- Rôle IAM avec permissions :
  - DynamoDB: GetItem, Query, Scan
  - CloudWatch: Logs
  - Lambda: Execution

### Étapes de déploiement

#### 1. Créer le rôle IAM

```bash
aws iam create-role \
  --role-name cityflow-api-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy \
  --role-name cityflow-api-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name cityflow-api-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess
```

#### 2. Packager et déployer

```bash
# Package
cd /path/to/cityflow
zip -r api-lambda.zip api/ utils/ config/ models/ -x "*.pyc" -x "__pycache__/*"

# Déployer
aws lambda create-function \
  --function-name cityflow-api \
  --runtime python3.10 \
  --handler api.lambda_function.lambda_handler \
  --zip-file fileb://api-lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/cityflow-api-lambda-role \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{DATABASE_TYPE=dynamodb,DYNAMODB_METRICS_TABLE=cityflow-metrics,DYNAMODB_REPORTS_TABLE=cityflow-daily-reports,AWS_REGION=us-east-1}"
```

#### 3. Créer API Gateway

```bash
# Via console AWS ou Terraform/CloudFormation
# Configurer routes RESTful
# Activer CORS
# Déployer sur stage "prod"
```

#### 4. URL finale

```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/metrics/bikes/2025-11-03
```

---

## 📦 Dépendances

### Pour développement local

```bash
pip install flask flask-cors
```

### Pour AWS Lambda

Aucune dépendance supplémentaire ! (Flask non requis dans Lambda)

---

## 🔍 Codes de réponse

| Code | Description | Exemple |
|------|-------------|---------|
| **200** | Succès | Métriques trouvées |
| **400** | Mauvaise requête | Date invalide |
| **404** | Non trouvé | Métriques inexistantes pour cette date |
| **500** | Erreur serveur | Erreur base de données |

---

## 💡 Exemples d'utilisation

### Depuis une application web (JavaScript)

```javascript
// Récupérer métriques bikes
fetch('http://localhost:5000/metrics/bikes/2025-11-03')
  .then(response => response.json())
  .then(data => {
    console.log('Compteurs vélos:', data.data.metrics.length);
    console.log('Top 10:', data.data.top_counters);
  });

// Récupérer rapport
fetch('http://localhost:5000/report/2025-11-03')
  .then(response => response.json())
  .then(data => {
    console.log('Summary:', data.report.summary);
  });
```

### Depuis Python

```python
import requests

# Métriques bikes
response = requests.get('http://localhost:5000/metrics/bikes/2025-11-03')
data = response.json()
print(f"Total compteurs: {len(data['data']['metrics'])}")

# Rapport
response = requests.get('http://localhost:5000/report/2025-11-03')
report = response.json()
print(f"Véhicules Paris: {report['report']['summary']['total_vehicules_paris']}")
```

---

## 🎯 Cas d'usage

### Dashboard temps réel

```javascript
// Récupérer toutes les métriques du jour
setInterval(() => {
  fetch('/metrics/2025-11-03')
    .then(r => r.json())
    .then(data => updateDashboard(data));
}, 30000);  // Refresh toutes les 30s
```

### Application mobile

```swift
// iOS - Swift
let url = URL(string: "https://api.cityflow.com/metrics/bikes/2025-11-03")!
URLSession.shared.dataTask(with: url) { data, response, error in
    // Traiter les données
}.resume()
```

### Intégration GPS

```python
# Waze, Google Maps, etc.
def get_traffic_status(troncon_id: str, date: str):
    response = requests.get(f'https://api.cityflow.com/metrics/comptages/{date}')
    metrics = response.json()
    
    # Trouver le tronçon
    for troncon in metrics['data']['metrics']:
        if troncon['libelle'] == troncon_id:
            return troncon['etat_trafic_dominant']  # "Fluide", "Dense", "Saturé"
```

---

## 🔧 Configuration

### Variables d'environnement

#### Local (.env)
```bash
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=cityflow
```

#### AWS Lambda (Console AWS)
```bash
DATABASE_TYPE=dynamodb
DYNAMODB_METRICS_TABLE=cityflow-metrics
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports
AWS_REGION=us-east-1
```

---

## 📊 Performance

### Temps de réponse typiques

| Endpoint | Local (MongoDB) | AWS (DynamoDB) |
|----------|-----------------|----------------|
| `/health` | ~10ms | ~50ms |
| `/stats` | ~50ms | ~100ms |
| `/metrics/bikes/{date}` | ~100ms | ~200ms |
| `/metrics/{date}` | ~500ms | ~800ms |
| `/report/{date}` | ~200ms | ~300ms |

### Optimisations

- ✅ Métriques comptages en version summary (MongoDB)
- ✅ Fallback vers fichiers locaux si BDD échoue
- ✅ Connexion BDD fermée après chaque requête
- ✅ CORS activé pour requêtes cross-origin

---

## 🐛 Dépannage

### Erreur : "Flask non disponible"

```bash
pip install flask flask-cors
```

### Erreur : "Connection refused" (MongoDB)

```bash
# Vérifier que MongoDB est démarré
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
```

### Erreur : "Metrics not found"

Vérifier que les métriques ont été générées :
```bash
python3 processors/main.py
ls -lh output/metrics/
```

---

## 📖 Documentation interactive

Une fois le serveur démarré, accéder à :

- **`http://localhost:5000`** → Page d'accueil
- **`http://localhost:5000/docs`** → Documentation complète

---

## 🎓 Architecture

```
┌──────────────────────────────────────────────┐
│  Client (Web, Mobile, curl)                  │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ API Gateway    │  (AWS) ou Flask (Local)
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Lambda Handler │
        │ (lambda_function.py)
        └────────┬───────┘
                 │
       ┌─────────┴──────────┐
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────┐
│ Handlers     │    │ Database     │
│ (metrics,    │    │ Factory      │
│  report,     │    │              │
│  stats)      │    │              │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │      ┌────────────┴────────────┐
       │      │                         │
       │      ▼                         ▼
       │  ┌─────────┐            ┌──────────┐
       └→ │ MongoDB │            │ DynamoDB │
          │ (Local) │            │  (AWS)   │
          └─────────┘            └──────────┘
```

---

## ✅ Checklist déploiement

### Local
- [ ] MongoDB installé et démarré
- [ ] Flask installé (`pip install flask flask-cors`)
- [ ] Métriques générées (`python3 processors/main.py`)
- [ ] `.env` configuré avec `DATABASE_TYPE=mongodb`
- [ ] Serveur démarré (`python3 api/local_server.py`)

### AWS
- [ ] Tables DynamoDB créées
- [ ] Rôle IAM configuré
- [ ] Lambda function déployée
- [ ] API Gateway configuré
- [ ] Variables d'environnement définies
- [ ] Tests de connectivité OK

---

## 🎉 Prêt à utiliser !

```bash
# Démarrer le serveur local
python3 api/local_server.py

# Dans un autre terminal, tester
curl http://localhost:5000/health
```

**Votre API est maintenant opérationnelle !** 🚀

