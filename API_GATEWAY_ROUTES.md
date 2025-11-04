# 📋 Routes API CityFlow - Configuration API Gateway

## 🎯 Vue d'Ensemble

Toutes les routes de l'API CityFlow Analytics pour configurer AWS API Gateway.

---

## 📍 Routes Disponibles

### 1. **Health Check** ✅
```
GET /health
GET /api/health
```
**Description** : Vérifie l'état de l'API  
**Paramètres** : Aucun  
**Exemple** :
```bash
curl https://api-gateway-url/prod/health
```

---

### 2. **Statistiques Globales** 📊
```
GET /stats
GET /api/stats
```
**Description** : Récupère les statistiques globales de l'API  
**Paramètres** : Aucun  
**Exemple** :
```bash
curl https://api-gateway-url/prod/stats
```

---

### 3. **Métriques Spécifiques** 🚲
```
GET /metrics/{type}/{date}
GET /api/metrics/{type}/{date}
```
**Description** : Récupère les métriques d'un type spécifique pour une date  
**Paramètres** :
- `type` : Type de métrique (`bikes`, `traffic`, `weather`, `comptages`, `chantiers`, `referentiel`)
- `date` : Date au format `YYYY-MM-DD`

**Exemples** :
```bash
# Métriques vélos
curl https://api-gateway-url/prod/metrics/bikes/2025-11-04

# Métriques trafic
curl https://api-gateway-url/prod/metrics/traffic/2025-11-04

# Métriques météo
curl https://api-gateway-url/prod/metrics/weather/2025-11-04

# Métriques comptages
curl https://api-gateway-url/prod/metrics/comptages/2025-11-04

# Métriques chantiers
curl https://api-gateway-url/prod/metrics/chantiers/2025-11-04

# Métriques référentiel
curl https://api-gateway-url/prod/metrics/referentiel/2025-11-04
```

---

### 4. **Toutes les Métriques d'une Date** 📈
```
GET /metrics/{date}
GET /api/metrics/{date}
```
**Description** : Récupère toutes les métriques disponibles pour une date  
**Paramètres** :
- `date` : Date au format `YYYY-MM-DD`

**Exemple** :
```bash
curl https://api-gateway-url/prod/metrics/2025-11-04
```

---

### 5. **Rapport Quotidien** 📄
```
GET /report/{date}
GET /api/report/{date}
```
**Description** : Récupère le rapport quotidien complet pour une date  
**Paramètres** :
- `date` : Date au format `YYYY-MM-DD`

**Exemple** :
```bash
curl https://api-gateway-url/prod/report/2025-11-04
```

---

### 6. **Page d'Accueil** 🏠
```
GET /
```
**Description** : Informations sur l'API et documentation  
**Paramètres** : Aucun  
**Exemple** :
```bash
curl https://api-gateway-url/prod/
```

---

### 7. **Documentation** 📖
```
GET /docs
```
**Description** : Documentation complète de l'API  
**Paramètres** : Aucun  
**Exemple** :
```bash
curl https://api-gateway-url/prod/docs
```

---

## 🔧 Configuration API Gateway

### Option 1 : Route Catch-All (Recommandé) 🌐

**Configuration la plus simple** : Utiliser une seule route `ANY /{proxy+}` qui redirige tout vers votre EC2.

#### Étape 1 : Créer l'Intégration
- **Type** : HTTP
- **Method** : ANY
- **URL** : `http://15.236.210.200:5000/{proxy}`
- **Name** : `cityflow-ec2-backend`

#### Étape 2 : Créer la Route
- **Method** : ANY
- **Resource path** : `/{proxy+}`
- **Integration target** : `cityflow-ec2-backend`

#### Étape 3 : Déployer
- **Stage name** : `prod`
- **Auto-deploy** : Activé

✅ **Avantage** : Toutes les routes fonctionnent automatiquement !

---

### Option 2 : Routes Spécifiques (Plus Granulaire) 🎯

Si vous voulez un contrôle plus fin, créez des routes spécifiques :

#### Routes à Créer :

1. **Health Check**
   - Method : `GET`
   - Path : `/health`
   - Integration : `http://15.236.210.200:5000/health`

2. **Stats**
   - Method : `GET`
   - Path : `/stats`
   - Integration : `http://15.236.210.200:5000/stats`

3. **Métriques Spécifiques**
   - Method : `GET`
   - Path : `/metrics/{type}/{date}`
   - Integration : `http://15.236.210.200:5000/metrics/{type}/{date}`

4. **Toutes les Métriques**
   - Method : `GET`
   - Path : `/metrics/{date}`
   - Integration : `http://15.236.210.200:5000/metrics/{date}`

5. **Rapport**
   - Method : `GET`
   - Path : `/report/{date}`
   - Integration : `http://15.236.210.200:5000/report/{date}`

6. **Documentation**
   - Method : `GET`
   - Path : `/docs`
   - Integration : `http://15.236.210.200:5000/docs`

---

## 📝 Exemple de Configuration AWS CLI

### Créer l'API (HTTP API)
```bash
aws apigatewayv2 create-api \
    --name cityflow-api \
    --protocol-type HTTP \
    --cors-configuration AllowOrigins='*',AllowMethods='GET,POST,OPTIONS',AllowHeaders='*' \
    --region eu-west-3
```

**Récupérer l'API ID** (noté dans la réponse) :
```bash
API_ID=abc123xyz
```

### Créer l'Intégration HTTP
```bash
aws apigatewayv2 create-integration \
    --api-id $API_ID \
    --integration-type HTTP_PROXY \
    --integration-uri http://15.236.210.200:5000/{proxy} \
    --integration-method ANY \
    --payload-format-version 1.0 \
    --region eu-west-3
```

**Récupérer l'Integration ID** :
```bash
INTEGRATION_ID=integration-123
```

### Créer la Route Catch-All
```bash
aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key 'ANY /{proxy+}' \
    --target integrations/$INTEGRATION_ID \
    --region eu-west-3
```

### Créer le Stage
```bash
aws apigatewayv2 create-stage \
    --api-id $API_ID \
    --stage-name prod \
    --auto-deploy \
    --region eu-west-3
```

### Récupérer l'URL de l'API
```bash
aws apigatewayv2 get-api \
    --api-id $API_ID \
    --region eu-west-3 \
    --query 'ApiEndpoint' \
    --output text
```

---

## 🔒 Sécurité (Optionnel)

### CORS Configuration
Si vous utilisez l'API depuis un navigateur, configurez CORS :

```json
{
  "AllowOrigins": ["*"],
  "AllowMethods": ["GET", "OPTIONS"],
  "AllowHeaders": ["*"],
  "MaxAge": 300
}
```

### Rate Limiting
Configurez des limites de débit dans API Gateway :
- **Default route throttling** : 1000 req/s
- **Per-route throttling** : Selon vos besoins

### API Keys (Optionnel)
Pour restreindre l'accès, créez des clés API :
```bash
aws apigateway create-api-key \
    --name cityflow-api-key \
    --enabled \
    --region eu-west-3
```

---

## ✅ Test de l'API Gateway

Une fois configuré, testez avec :

```bash
# Health check
curl https://VOTRE_API_ID.execute-api.eu-west-3.amazonaws.com/prod/health

# Métriques
curl https://VOTRE_API_ID.execute-api.eu-west-3.amazonaws.com/prod/metrics/bikes/2025-11-04

# Rapport
curl https://VOTRE_API_ID.execute-api.eu-west-3.amazonaws.com/prod/report/2025-11-04
```

---

## 📊 Tableau Récapitulatif

| Route | Méthode | Paramètres | Description |
|-------|---------|------------|-------------|
| `/health` | GET | - | Health check |
| `/stats` | GET | - | Statistiques globales |
| `/metrics/{type}/{date}` | GET | `type`, `date` | Métriques spécifiques |
| `/metrics/{date}` | GET | `date` | Toutes les métriques |
| `/report/{date}` | GET | `date` | Rapport quotidien |
| `/` | GET | - | Page d'accueil |
| `/docs` | GET | - | Documentation |

---

## 🎯 Types de Métriques Disponibles

- `bikes` : Métriques vélos
- `traffic` : Métriques trafic routier
- `weather` : Métriques météo
- `comptages` : Métriques comptages
- `chantiers` : Métriques chantiers
- `referentiel` : Métriques référentiel

---

## 📌 Notes Importantes

1. **Format de Date** : Toujours `YYYY-MM-DD` (ex: `2025-11-04`)
2. **IP EC2** : Remplacer `15.236.210.200` par votre IP EC2 actuelle
3. **Port** : L'API Flask tourne sur le port `5000` par défaut
4. **Proxy** : La route `/{proxy+}` capture tous les chemins et sous-chemins

---

## 🚀 Prochaines Étapes

1. ✅ Créer l'API Gateway via Console AWS ou CLI
2. ✅ Configurer l'intégration HTTP vers EC2
3. ✅ Créer la route `/{proxy+}`
4. ✅ Déployer sur le stage `prod`
5. ✅ Tester les endpoints
6. ✅ Configurer CORS si nécessaire
7. ✅ Optionnel : Ajouter rate limiting et API keys

---

**🎉 Votre API sera accessible via une URL HTTPS permanente !**

