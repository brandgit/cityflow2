# 🌐 Guide Complet API CityFlow Analytics

## 🎯 Vue d'ensemble

Une API REST complète pour exposer les métriques et rapports CityFlow, avec support **automatique** MongoDB (local) et DynamoDB (AWS).

---

## ✨ Fonctionnalités

✅ **Architecture hybride** : MongoDB local ↔ DynamoDB AWS (automatique)  
✅ **Compatible Lambda** : Déploiement AWS sans modification  
✅ **Serveur local** : Flask pour développement  
✅ **CORS activé** : Utilisable depuis applications web  
✅ **Validation** : Paramètres validés automatiquement  
✅ **Fallback intelligent** : Fichiers locaux si BDD échoue  
✅ **Documentation** : Endpoints auto-documentés

---

## 📂 Structure Créée

```
api/
├── __init__.py                    # Package API
├── lambda_function.py             # ⭐ Handler AWS Lambda
├── local_server.py                # ⭐ Serveur Flask (dev local)
├── test_api.py                    # Tests automatisés
├── README.md                      # Documentation API
├── API_DEPLOYMENT.md              # Guide déploiement AWS
├── handlers/                      # Handlers par endpoint
│   ├── __init__.py
│   ├── metrics_handler.py         # Logique métriques
│   ├── report_handler.py          # Logique rapports
│   └── stats_handler.py           # Logique statistiques
└── utils/                         # Utilitaires API
    ├── __init__.py
    ├── response.py                # Formatage HTTP
    └── validation.py              # Validation paramètres
```

---

## 🚀 Démarrage

### 🏠 Mode Local (5 minutes)

#### 1. Installer Flask

```bash
pip install flask flask-cors
```

#### 2. S'assurer que les métriques existent

```bash
# Si pas encore fait
python3 main.py
```

#### 3. Démarrer l'API

```bash
python3 api/local_server.py
```

**Serveur démarré** : `http://localhost:5000` ✅

#### 4. Tester

```bash
# Dans un autre terminal
curl http://localhost:5000/health

# Ou dans le navigateur
http://localhost:5000/docs
```

---

### ☁️ Mode AWS Lambda (30 minutes)

Voir le guide complet : **`api/API_DEPLOYMENT.md`**

**Résumé :**
1. Créer rôle IAM
2. Packager le code
3. Déployer Lambda
4. Configurer API Gateway
5. Tester l'URL publique

---

## 📡 Endpoints Disponibles

### 1. **Health Check**

```http
GET /health
```

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

**Usage :**
```bash
curl http://localhost:5000/health
```

---

### 2. **Statistiques Globales**

```http
GET /stats
```

**Réponse :**
```json
{
  "api_version": "1.0.0",
  "database_type": "mongodb",
  "environment": "Local",
  "metric_types_available": ["bikes", "traffic", "weather", "comptages", "chantiers", "referentiel"],
  "database_stats": {
    "metrics_count": 5,
    "reports_count": 1
  }
}
```

**Usage :**
```bash
curl http://localhost:5000/stats | jq
```

---

### 3. **Métriques Spécifiques**

```http
GET /metrics/{type}/{date}
```

**Paramètres :**
- `type` : `bikes`, `traffic`, `weather`, `comptages`, `chantiers`, `referentiel`
- `date` : `YYYY-MM-DD`

**Exemples :**

```bash
# Métriques vélos
curl http://localhost:5000/metrics/bikes/2025-11-03

# Perturbations RATP
curl http://localhost:5000/metrics/traffic/2025-11-03

# Météo
curl http://localhost:5000/metrics/weather/2025-11-03

# Comptages routiers (summary si MongoDB)
curl http://localhost:5000/metrics/comptages/2025-11-03
```

**Réponse (exemple bikes) :**
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
        "pic_horaire": 21,
        "arrondissement": "75012",
        "coordinates": {"lon": 2.37559, "lat": 48.84613},
        "anomalie_detectee": false
      }
      // ... autres compteurs
    ],
    "top_counters": [...],
    "failing_sensors": [...]
  }
}
```

---

### 4. **Toutes les Métriques**

```http
GET /metrics/{date}
```

Récupère **toutes** les métriques d'une date (bikes, traffic, weather, etc.)

**Exemple :**
```bash
curl http://localhost:5000/metrics/2025-11-03 | jq '.metrics | keys'
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

### 5. **Rapport Quotidien**

```http
GET /report/{date}
```

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
      "nombre_troncons_satures": 45,
      "taux_disponibilite_capteurs": 97.5,
      "total_velos_paris": 15234
    },
    "top_10_troncons_frequentes": [...],
    "top_10_zones_congestionnees": [...],
    "alertes_congestion": [...],
    "capteurs_defaillants": [...]
  }
}
```

---

## 🔧 Gestion Base de Données (Automatique)

### Comment ça marche ?

L'API utilise **`database_factory`** pour choisir automatiquement :

```python
# api/handlers/metrics_handler.py
from utils.database_factory import get_database_service

def get_metrics(metric_type, date):
    # Choix automatique MongoDB ou DynamoDB !
    db_service = get_database_service()
    return db_service.load_metrics(metric_type, date)
```

### 🏠 En Local

```bash
# .env
DATABASE_TYPE=mongodb
```

**L'API charge depuis** : MongoDB (`localhost:27017`)

### ☁️ En AWS Lambda

```bash
# Variables Lambda
DATABASE_TYPE=dynamodb
```

**L'API charge depuis** : DynamoDB (tables AWS)

**Aucune modification de code !** 🎉

---

## 🧪 Tests

### Test local (sans serveur)

```bash
python3 api/test_api.py --mode lambda
```

**Teste directement** la fonction Lambda sans serveur Flask.

### Test serveur HTTP

```bash
# Terminal 1 : Démarrer le serveur
python3 api/local_server.py

# Terminal 2 : Lancer les tests
python3 api/test_api.py --mode http
```

### Test tous les modes

```bash
python3 api/test_api.py --mode both
```

---

## 💻 Utilisation depuis Applications

### Frontend React/Vue

```javascript
// Récupérer métriques
async function getBikesMetrics(date) {
  const response = await fetch(`http://localhost:5000/metrics/bikes/${date}`);
  const data = await response.json();
  return data.data.metrics;
}

// Utiliser dans composant
const metrics = await getBikesMetrics('2025-11-03');
console.log('Total compteurs:', metrics.length);
```

### Python

```python
import requests

# API Client
class CityFlowAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_metrics(self, metric_type, date):
        url = f"{self.base_url}/metrics/{metric_type}/{date}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['data']
    
    def get_report(self, date):
        url = f"{self.base_url}/report/{date}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['report']

# Utilisation
api = CityFlowAPI()
bikes = api.get_metrics('bikes', '2025-11-03')
print(f"Compteurs actifs: {len(bikes['metrics'])}")
```

---

## 🎨 Dashboard Exemple

```html
<!DOCTYPE html>
<html>
<head>
    <title>CityFlow Dashboard</title>
</head>
<body>
    <h1>CityFlow Analytics</h1>
    <div id="summary"></div>
    
    <script>
        async function loadDashboard() {
            // Charger rapport du jour
            const response = await fetch('http://localhost:5000/report/2025-11-03');
            const {report} = await response.json();
            
            // Afficher résumé
            document.getElementById('summary').innerHTML = `
                <h2>Résumé du ${report.date}</h2>
                <p>Total véhicules: ${report.summary.total_vehicules_paris.toLocaleString()}</p>
                <p>Temps perdu: ${report.summary.temps_perdu_total_minutes.toLocaleString()} min</p>
                <p>Tronçons saturés: ${report.summary.nombre_troncons_satures}</p>
            `;
        }
        
        loadDashboard();
    </script>
</body>
</html>
```

---

## 📊 Codes de Réponse

| Code | Signification | Exemple |
|------|---------------|---------|
| **200** | Succès | Métriques trouvées |
| **400** | Mauvaise requête | Format date invalide |
| **404** | Non trouvé | Métriques inexistantes pour cette date |
| **500** | Erreur serveur | Erreur base de données |

---

## 🔒 Sécurité

### CORS

CORS activé par défaut pour développement :

```python
headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
}
```

### Production

Pour production, restreindre les origines :

```python
# Dans lambda_function.py
"Access-Control-Allow-Origin": "https://your-domain.com"
```

### Authentification (future)

Options pour ajouter l'authentification :
- API Key (API Gateway)
- JWT tokens
- AWS Cognito
- OAuth 2.0

---

## 📚 Documentation

- **`api/README.md`** - Documentation API
- **`api/API_DEPLOYMENT.md`** - Déploiement AWS
- **`API_GUIDE_COMPLET.md`** - Ce fichier (guide complet)

---

## ✅ Checklist

### Pour développement local
- [ ] MongoDB démarré
- [ ] Métriques générées (`python3 main.py`)
- [ ] Flask installé (`pip install flask flask-cors`)
- [ ] Serveur démarré (`python3 api/local_server.py`)
- [ ] Tests OK (`curl http://localhost:5000/health`)

### Pour production AWS
- [ ] Tables DynamoDB créées
- [ ] Rôle IAM configuré
- [ ] Code packageé (`zip -r api-lambda.zip ...`)
- [ ] Lambda déployée
- [ ] API Gateway configuré
- [ ] URL publique testée

---

## 🎓 Résumé

### Commandes essentielles

```bash
# Développement local
python3 api/local_server.py                    # Démarrer serveur
python3 api/test_api.py                        # Tester
curl http://localhost:5000/health              # Health check

# Production AWS
zip -r api-lambda.zip api/ utils/ config/      # Packager
aws lambda create-function ...                 # Déployer
curl https://xxx.execute-api.amazonaws.com/prod/health  # Tester
```

### Architecture

| Composant | Local | AWS |
|-----------|-------|-----|
| **Serveur** | Flask (port 5000) | API Gateway + Lambda |
| **Base de données** | MongoDB | DynamoDB |
| **Changement code** | ❌ Aucun | ❌ Aucun |
| **Configuration** | `.env` DATABASE_TYPE=mongodb | Lambda env DATABASE_TYPE=dynamodb |

---

## 🎉 Félicitations !

Vous avez maintenant une **API REST complète** qui :
- ✅ Fonctionne en local avec MongoDB
- ✅ Se déploie sur AWS avec DynamoDB
- ✅ Nécessite ZÉRO modification de code
- ✅ Gère automatiquement le fallback
- ✅ Est documentée et testée

**Démarrez avec :**
```bash
python3 api/local_server.py
```

**Puis ouvrez :**
```
http://localhost:5000/docs
```

🚀 **Votre API CityFlow est opérationnelle !**

