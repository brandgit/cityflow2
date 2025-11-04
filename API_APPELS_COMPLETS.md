# 📡 Liste Complète des Appels API - CityFlow Analytics

## 🌐 Base URL

### 🏠 Développement Local
```
http://localhost:5001
```

### ☁️ Production AWS
```
https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
```

---

## 📋 Endpoints Disponibles

### 1. 🏥 Health Check

**Endpoint :** `GET /health`

**Description :** Vérifie que l'API fonctionne correctement

**Exemple cURL :**
```bash
curl http://localhost:5001/health
```

**Exemple avec jq :**
```bash
curl http://localhost:5001/health | jq
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

**Code de réponse :** `200 OK`

---

### 2. 📊 Statistiques Globales

**Endpoint :** `GET /stats`

**Description :** Récupère les statistiques globales de l'API et de la base de données

**Exemple cURL :**
```bash
curl http://localhost:5001/stats
```

**Exemple avec jq :**
```bash
curl http://localhost:5001/stats | jq
```

**Réponse :**
```json
{
  "api_version": "1.0.0",
  "database_type": "mongodb",
  "environment": "Local",
  "timestamp": "2025-11-03T20:00:00",
  "metric_types_available": [
    "bikes",
    "traffic",
    "weather",
    "comptages",
    "chantiers",
    "referentiel"
  ],
  "database_stats": {
    "metrics_count": 5,
    "reports_count": 1
  }
}
```

**Code de réponse :** `200 OK`

---

### 3. 🚴 Métriques Vélos (Bikes)

**Endpoint :** `GET /metrics/bikes/{date}`

**Description :** Récupère les métriques des compteurs vélos pour une date spécifique

**Paramètres :**
- `date` : Format `YYYY-MM-DD` (ex: `2025-11-03`)

**Exemple cURL :**
```bash
# Métriques du 3 novembre 2025
curl http://localhost:5001/metrics/bikes/2025-11-03
```

**Exemple avec jq :**
```bash
# Nombre total de compteurs
curl http://localhost:5001/metrics/bikes/2025-11-03 | jq '.data.metrics | length'

# Top 10 compteurs
curl http://localhost:5001/metrics/bikes/2025-11-03 | jq '.data.top_counters[:10]'

# Compteurs par arrondissement
curl http://localhost:5001/metrics/bikes/2025-11-03 | jq '.data.metrics | group_by(.arrondissement) | map({arr: .[0].arrondissement, count: length})'
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
        "pic_horaire": 21,
        "arrondissement": "75012",
        "coordinates": {
          "lon": 2.37559,
          "lat": 48.84613
        },
        "anomalie_detectee": false
      }
      // ... autres compteurs
    ],
    "top_counters": [
      // Top 10 compteurs les plus fréquentés
    ],
    "failing_sensors": [
      // Capteurs en panne
    ]
  }
}
```

**Code de réponse :** `200 OK` (succès) ou `404 Not Found` (date inexistante)

---

### 4. 🚗 Métriques Trafic (Perturbations RATP)

**Endpoint :** `GET /metrics/traffic/{date}`

**Description :** Récupère les métriques de trafic (perturbations RATP) pour une date

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/metrics/traffic/2025-11-03
```

**Exemple avec jq :**
```bash
# Nombre de perturbations
curl http://localhost:5001/metrics/traffic/2025-11-03 | jq '.data.metrics | length'

# Perturbations actives
curl http://localhost:5001/metrics/traffic/2025-11-03 | jq '.data.metrics | map(select(.statut == "active"))'
```

**Réponse :**
```json
{
  "metric_type": "traffic",
  "date": "2025-11-03",
  "data": {
    "metrics": [
      {
        "id": "perturbation_123",
        "type": "Travaux",
        "ligne": "Ligne 1",
        "statut": "active",
        "impact": "Modéré",
        "description": "Travaux de maintenance"
      }
      // ... autres perturbations
    ],
    "statistiques": {
      "total_perturbations": 94,
      "actives": 12,
      "par_type": {...}
    }
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 5. 🌤️ Métriques Météo

**Endpoint :** `GET /metrics/weather/{date}`

**Description :** Récupère les données météorologiques pour une date

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/metrics/weather/2025-11-03
```

**Exemple avec jq :**
```bash
# Température moyenne
curl http://localhost:5001/metrics/weather/2025-11-03 | jq '.data.temperature_moyenne'

# Conditions météo
curl http://localhost:5001/metrics/weather/2025-11-03 | jq '.data.conditions'
```

**Réponse :**
```json
{
  "metric_type": "weather",
  "date": "2025-11-03",
  "data": {
    "temperature_moyenne": 15.5,
    "temperature_min": 12.0,
    "temperature_max": 18.0,
    "precipitation": 0.0,
    "conditions": "Ensoleillé",
    "humidite": 65,
    "vent_vitesse": 10.5
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 6. 🚦 Métriques Comptages Routiers

**Endpoint :** `GET /metrics/comptages/{date}`

**Description :** Récupère les métriques de comptages routiers (version summary si MongoDB)

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/metrics/comptages/2025-11-03
```

**Exemple avec jq :**
```bash
# Top 10 tronçons les plus fréquentés
curl http://localhost:5001/metrics/comptages/2025-11-03 | jq '.data.top_10_troncons'

# Zones congestionnées
curl http://localhost:5001/metrics/comptages/2025-11-03 | jq '.data.top_10_zones_congestionnees'

# Alertes congestion
curl http://localhost:5001/metrics/comptages/2025-11-03 | jq '.data.alertes_congestion'
```

**Réponse (version summary MongoDB) :**
```json
{
  "metric_type": "comptages",
  "date": "2025-11-03",
  "data": {
    "global_metrics": {
      "total_vehicules_paris": 1234567,
      "temps_perdu_total_minutes": 89456,
      "nombre_troncons_satures": 45
    },
    "top_10_troncons": [
      {
        "libelle": "Boulevard Haussmann",
        "total_vehicules": 45678,
        "etat_trafic_dominant": "Saturé"
      }
      // ... top 10
    ],
    "top_10_zones_congestionnees": [
      // ... zones congestionnées
    ],
    "alertes_congestion": [
      // ... alertes
    ],
    "total_troncons": 3348,
    "note": "Liste complète disponible dans fichier local uniquement"
  }
}
```

**Réponse (version complète DynamoDB) :**
```json
{
  "metric_type": "comptages",
  "date": "2025-11-03",
  "data": {
    "metrics": [
      {
        "libelle": "Boulevard Haussmann",
        "identifiant_arc": "12345",
        "total_vehicules": 45678,
        "etat_trafic_dominant": "Saturé",
        "vitesse_moyenne": 25.5,
        "temps_perdu_minutes": 120
      }
      // ... 3348 tronçons
    ],
    "global_metrics": {...},
    "top_10_troncons": [...],
    "top_10_zones_congestionnees": [...],
    "alertes_congestion": [...]
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 7. 🏗️ Métriques Chantiers

**Endpoint :** `GET /metrics/chantiers/{date}`

**Description :** Récupère les métriques des chantiers perturbant la circulation

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/metrics/chantiers/2025-11-03
```

**Exemple avec jq :**
```bash
# Nombre de chantiers actifs
curl http://localhost:5001/metrics/chantiers/2025-11-03 | jq '.data.chantiers_actifs | length'

# Chantiers par arrondissement
curl http://localhost:5001/metrics/chantiers/2025-11-03 | jq '.data.chantiers_actifs | group_by(.arrondissement)'
```

**Réponse :**
```json
{
  "metric_type": "chantiers",
  "date": "2025-11-03",
  "data": {
    "chantiers_actifs": [
      {
        "nom": "Travaux rue de Rivoli",
        "arrondissement": "75001",
        "date_debut": "2025-11-01",
        "date_fin": "2025-11-10",
        "impact_circulation": "Forte"
      }
      // ... autres chantiers
    ],
    "statistiques": {
      "total_chantiers": 68,
      "par_arrondissement": {...}
    }
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 8. 🗺️ Métriques Référentiel Géographique

**Endpoint :** `GET /metrics/referentiel/{date}`

**Description :** Récupère le référentiel géographique des tronçons

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/metrics/referentiel/2025-11-03
```

**Exemple avec jq :**
```bash
# Nombre de tronçons
curl http://localhost:5001/metrics/referentiel/2025-11-03 | jq '.data.statistiques.nombre_troncons'

# Longueur totale
curl http://localhost:5001/metrics/referentiel/2025-11-03 | jq '.data.statistiques.longueur_totale_metres'
```

**Réponse :**
```json
{
  "metric_type": "referentiel",
  "date": "2025-11-03",
  "data": {
    "mapping": {
      "identifiant_arc_12345": {
        "libelle": "Boulevard Haussmann",
        "longueur_metres": 1250.5,
        "coordinates": {
          "start": {"lon": 2.3314, "lat": 48.8738},
          "end": {"lon": 2.3401, "lat": 48.8745}
        }
      }
      // ... autres tronçons
    },
    "statistiques": {
      "nombre_troncons": 3739,
      "longueur_totale_metres": 1250000,
      "longueur_moyenne_metres": 334.5
    }
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 9. 📈 Toutes les Métriques d'une Date

**Endpoint :** `GET /metrics/{date}`

**Description :** Récupère toutes les métriques (bikes, traffic, weather, comptages, chantiers, référentiel) pour une date

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/metrics/2025-11-03
```

**Exemple avec jq :**
```bash
# Liste des types de métriques disponibles
curl http://localhost:5001/metrics/2025-11-03 | jq '.metrics | keys'

# Vérifier si toutes les métriques sont présentes
curl http://localhost:5001/metrics/2025-11-03 | jq '.metrics | to_entries | map({type: .key, present: (.value != null)})'
```

**Réponse :**
```json
{
  "date": "2025-11-03",
  "metrics": {
    "bikes": {
      "metrics": [...],
      "top_counters": [...]
    },
    "traffic": {
      "metrics": [...],
      "statistiques": {...}
    },
    "weather": {
      "temperature_moyenne": 15.5,
      "conditions": "Ensoleillé"
    },
    "comptages": {
      "global_metrics": {...},
      "top_10_troncons": [...]
    },
    "chantiers": {
      "chantiers_actifs": [...]
    },
    "referentiel": {
      "mapping": {...},
      "statistiques": {...}
    }
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 10. 📋 Rapport Quotidien

**Endpoint :** `GET /report/{date}`

**Description :** Récupère le rapport quotidien complet pour une date

**Paramètres :**
- `date` : Format `YYYY-MM-DD`

**Exemple cURL :**
```bash
curl http://localhost:5001/report/2025-11-03
```

**Exemple avec jq :**
```bash
# Résumé du rapport
curl http://localhost:5001/report/2025-11-03 | jq '.report.summary'

# Top 10 tronçons les plus fréquentés
curl http://localhost:5001/report/2025-11-03 | jq '.report.top_10_troncons_frequentes'

# Zones congestionnées
curl http://localhost:5001/report/2025-11-03 | jq '.report.top_10_zones_congestionnees'

# Alertes congestion
curl http://localhost:5001/report/2025-11-03 | jq '.report.alertes_congestion'
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
      "total_velos_paris": 15234,
      "nombre_perturbations_actives": 12,
      "temperature_moyenne": 15.5,
      "conditions_meteo": "Ensoleillé"
    },
    "top_10_troncons_frequentes": [
      {
        "libelle": "Boulevard Haussmann",
        "total_vehicules": 45678,
        "etat_trafic": "Saturé"
      }
      // ... top 10
    ],
    "top_10_zones_congestionnees": [
      {
        "zone": "Centre de Paris",
        "temps_perdu_minutes": 1200,
        "nombre_troncons": 15
      }
      // ... top 10
    ],
    "alertes_congestion": [
      {
        "troncon": "Boulevard Haussmann",
        "niveau": "Critique",
        "temps_perdu_minutes": 45
      }
      // ... alertes
    ],
    "capteurs_defaillants": [
      {
        "id_compteur": "12345",
        "type": "bikes",
        "derniere_mesure": "2025-11-02T10:00:00"
      }
      // ... capteurs
    ]
  }
}
```

**Code de réponse :** `200 OK` ou `404 Not Found`

---

### 11. 📖 Documentation Interactive

**Endpoint :** `GET /docs`

**Description :** Documentation interactive de l'API

**Exemple cURL :**
```bash
curl http://localhost:5001/docs
```

**Exemple navigateur :**
```
http://localhost:5001/docs
```

**Réponse :**
```json
{
  "title": "CityFlow Analytics API Documentation",
  "version": "1.0.0",
  "base_url_local": "http://localhost:5001",
  "base_url_aws": "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod",
  "endpoints": [
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check de l'API"
    }
    // ... tous les endpoints
  ]
}
```

**Code de réponse :** `200 OK`

---

### 12. 🏠 Page d'Accueil

**Endpoint :** `GET /`

**Description :** Page d'accueil avec informations sur l'API

**Exemple cURL :**
```bash
curl http://localhost:5001/
```

**Exemple navigateur :**
```
http://localhost:5001/
```

**Réponse :**
```json
{
  "service": "CityFlow Analytics API",
  "version": "1.0.0",
  "status": "running",
  "documentation": "/docs",
  "endpoints": {
    "health": "/health",
    "stats": "/stats",
    "metrics": {
      "specific": "/metrics/{type}/{date}",
      "all": "/metrics/{date}"
    },
    "report": "/report/{date}"
  },
  "examples": {
    "bikes": "http://localhost:5001/metrics/bikes/2025-11-03",
    "all_metrics": "http://localhost:5001/metrics/2025-11-03",
    "report": "http://localhost:5001/report/2025-11-03"
  }
}
```

**Code de réponse :** `200 OK`

---

## 🔧 Codes de Réponse HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| **200** | OK | Requête réussie |
| **400** | Bad Request | Paramètres invalides (date mal formatée, type invalide) |
| **404** | Not Found | Ressource non trouvée (date inexistante, métriques non générées) |
| **500** | Internal Server Error | Erreur serveur (base de données, traitement) |

---

## 📝 Exemples d'Utilisation par Langage

### 🐍 Python

```python
import requests

BASE_URL = "http://localhost:5001"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Métriques bikes
response = requests.get(f"{BASE_URL}/metrics/bikes/2025-11-03")
bikes_data = response.json()
print(f"Nombre de compteurs: {len(bikes_data['data']['metrics'])}")

# Rapport quotidien
response = requests.get(f"{BASE_URL}/report/2025-11-03")
report = response.json()
print(f"Total véhicules: {report['report']['summary']['total_vehicules_paris']}")
```

### 🌐 JavaScript (Fetch)

```javascript
const BASE_URL = 'http://localhost:5001';

// Health check
async function checkHealth() {
  const response = await fetch(`${BASE_URL}/health`);
  const data = await response.json();
  console.log(data);
}

// Métriques bikes
async function getBikesMetrics(date) {
  const response = await fetch(`${BASE_URL}/metrics/bikes/${date}`);
  const data = await response.json();
  return data.data.metrics;
}

// Rapport quotidien
async function getReport(date) {
  const response = await fetch(`${BASE_URL}/report/${date}`);
  const data = await response.json();
  return data.report;
}

// Utilisation
const bikes = await getBikesMetrics('2025-11-03');
console.log(`Total compteurs: ${bikes.length}`);
```

### ⚛️ React

```jsx
import React, { useEffect, useState } from 'react';

function CityFlowDashboard() {
  const [report, setReport] = useState(null);
  const date = '2025-11-03';

  useEffect(() => {
    fetch(`http://localhost:5001/report/${date}`)
      .then(res => res.json())
      .then(data => setReport(data.report));
  }, [date]);

  if (!report) return <div>Chargement...</div>;

  return (
    <div>
      <h1>Rapport du {report.date}</h1>
      <p>Total véhicules: {report.summary.total_vehicules_paris.toLocaleString()}</p>
      <p>Temps perdu: {report.summary.temps_perdu_total_minutes.toLocaleString()} min</p>
    </div>
  );
}
```

### 📱 Swift (iOS)

```swift
import Foundation

let baseURL = "http://localhost:5001"

func getBikesMetrics(date: String) async throws -> [String: Any] {
    let url = URL(string: "\(baseURL)/metrics/bikes/\(date)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONSerialization.jsonObject(with: data) as! [String: Any]
}

// Utilisation
Task {
    do {
        let metrics = try await getBikesMetrics(date: "2025-11-03")
        print(metrics)
    } catch {
        print("Erreur: \(error)")
    }
}
```

---

## 🧪 Tests avec cURL

### Script de Test Complet

```bash
#!/bin/bash

BASE_URL="http://localhost:5001"
DATE="2025-11-03"

echo "=== Test Health Check ==="
curl -s "${BASE_URL}/health" | jq

echo -e "\n=== Test Stats ==="
curl -s "${BASE_URL}/stats" | jq

echo -e "\n=== Test Métriques Bikes ==="
curl -s "${BASE_URL}/metrics/bikes/${DATE}" | jq '.data.metrics | length'

echo -e "\n=== Test Métriques Traffic ==="
curl -s "${BASE_URL}/metrics/traffic/${DATE}" | jq '.data.metrics | length'

echo -e "\n=== Test Métriques Weather ==="
curl -s "${BASE_URL}/metrics/weather/${DATE}" | jq

echo -e "\n=== Test Toutes Métriques ==="
curl -s "${BASE_URL}/metrics/${DATE}" | jq '.metrics | keys'

echo -e "\n=== Test Rapport ==="
curl -s "${BASE_URL}/report/${DATE}" | jq '.report.summary'
```

**Sauvegarder comme `test_api.sh` et exécuter :**
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 📊 Cas d'Usage

### 1. Dashboard Temps Réel

```javascript
// Récupérer toutes les métriques du jour
setInterval(async () => {
  const response = await fetch('http://localhost:5001/metrics/2025-11-03');
  const data = await response.json();
  updateDashboard(data.metrics);
}, 30000); // Refresh toutes les 30 secondes
```

### 2. Analyse de Trafic

```python
import requests

# Récupérer comptages et référentiel
comptages = requests.get('http://localhost:5001/metrics/comptages/2025-11-03').json()
referentiel = requests.get('http://localhost:5001/metrics/referentiel/2025-11-03').json()

# Analyser zones congestionnées
for zone in comptages['data']['top_10_zones_congestionnees']:
    print(f"{zone['zone']}: {zone['temps_perdu_minutes']} min perdus")
```

### 3. Application Mobile

```swift
// iOS - Afficher métriques vélos
func loadBikesMetrics(date: String) {
    Task {
        let metrics = try await getBikesMetrics(date: date)
        DispatchQueue.main.async {
            self.bikesData = metrics
            self.tableView.reloadData()
        }
    }
}
```

### 4. Intégration GPS (Waze, Google Maps)

```python
# Récupérer état trafic pour calcul d'itinéraire
def get_traffic_status(troncon_id: str, date: str):
    response = requests.get(f'http://localhost:5001/metrics/comptages/{date}')
    comptages = response.json()
    
    # Trouver le tronçon
    for troncon in comptages['data']['metrics']:
        if troncon['identifiant_arc'] == troncon_id:
            return troncon['etat_trafic_dominant']  # "Fluide", "Dense", "Saturé"
    
    return "Inconnu"
```

---

## 🔐 Sécurité et Authentification

### Actuellement
- ✅ CORS activé pour développement
- ✅ Validation des paramètres
- ⚠️ Pas d'authentification (à ajouter en production)

### Pour Production AWS

```bash
# Avec clé API
curl -H "x-api-key: YOUR_API_KEY" \
  https://xxx.execute-api.amazonaws.com/prod/metrics/bikes/2025-11-03

# Avec JWT
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://xxx.execute-api.amazonaws.com/prod/metrics/bikes/2025-11-03
```

---

## 📋 Checklist des Appels API

### Endpoints de Base
- [ ] `GET /health` - Health check
- [ ] `GET /stats` - Statistiques
- [ ] `GET /` - Page d'accueil
- [ ] `GET /docs` - Documentation

### Métriques Spécifiques
- [ ] `GET /metrics/bikes/{date}` - Métriques vélos
- [ ] `GET /metrics/traffic/{date}` - Métriques trafic
- [ ] `GET /metrics/weather/{date}` - Métriques météo
- [ ] `GET /metrics/comptages/{date}` - Métriques comptages
- [ ] `GET /metrics/chantiers/{date}` - Métriques chantiers
- [ ] `GET /metrics/referentiel/{date}` - Métriques référentiel

### Métriques Globales
- [ ] `GET /metrics/{date}` - Toutes les métriques

### Rapports
- [ ] `GET /report/{date}` - Rapport quotidien

---

## 🎯 Résumé

**Total Endpoints :** 12 endpoints

**Catégories :**
- 🏥 **Health & Info** : 3 endpoints (health, stats, docs)
- 🚴 **Métriques Spécifiques** : 6 endpoints (bikes, traffic, weather, comptages, chantiers, référentiel)
- 📈 **Métriques Globales** : 1 endpoint (toutes les métriques)
- 📋 **Rapports** : 1 endpoint (rapport quotidien)
- 🏠 **Info** : 1 endpoint (page d'accueil)

**Format de réponse :** JSON

**Codes HTTP :** 200 (OK), 400 (Bad Request), 404 (Not Found), 500 (Error)

**Tous les endpoints sont documentés et prêts à l'emploi !** 🚀

