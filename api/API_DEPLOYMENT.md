# 🚀 Guide de Déploiement API CityFlow sur AWS

## Vue d'ensemble

Déployer l'API REST sur AWS avec :
- **API Gateway** : Point d'entrée HTTP
- **Lambda** : Exécution du code API
- **DynamoDB** : Stockage des métriques et rapports
- **CloudWatch** : Logs et monitoring

---

## 📋 Prérequis

- ✅ Compte AWS configuré
- ✅ AWS CLI installé et configuré
- ✅ Tables DynamoDB créées (`cityflow-metrics`, `cityflow-daily-reports`)
- ✅ Métriques générées et stockées dans DynamoDB

---

## 🔧 Étape 1 : Créer le Rôle IAM

### 1.1 Créer le fichier de politique de confiance

Créer `lambda-trust-policy.json` :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 1.2 Créer le rôle

```bash
aws iam create-role \
  --role-name cityflow-api-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json
```

### 1.3 Attacher les politiques

```bash
# Permissions Lambda de base (logs CloudWatch)
aws iam attach-role-policy \
  --role-name cityflow-api-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Permissions DynamoDB (lecture seule)
aws iam attach-role-policy \
  --role-name cityflow-api-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess
```

---

## 📦 Étape 2 : Packager le Code

### 2.1 Créer le package Lambda

```bash
cd /Users/brandbetsaleltikouetikoue/Desktop/EFREI_PARIS/M1/introduction-au-cloud-camputing/cityflow

# Créer répertoire de build
mkdir -p build

# Copier les fichiers nécessaires
cp -r api/ build/
cp -r utils/ build/
cp -r config/ build/
cp -r models/ build/

# Créer le zip (exclure __pycache__ et fichiers inutiles)
cd build
zip -r ../api-lambda.zip . -x "*.pyc" -x "*__pycache__*" -x "*.git*"
cd ..

# Vérifier le contenu
unzip -l api-lambda.zip | head -20
```

### 2.2 Taille du package

```bash
ls -lh api-lambda.zip
# Devrait être < 50 MB (limite Lambda)
```

---

## 🎯 Étape 3 : Créer la Fonction Lambda

### 3.1 Créer la fonction

```bash
aws lambda create-function \
  --function-name cityflow-api \
  --runtime python3.10 \
  --handler api.lambda_function.lambda_handler \
  --zip-file fileb://api-lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/cityflow-api-lambda-role \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{DATABASE_TYPE=dynamodb,DYNAMODB_METRICS_TABLE=cityflow-metrics,DYNAMODB_REPORTS_TABLE=cityflow-daily-reports,AWS_REGION=us-east-1}" \
  --region us-east-1
```

**Remplacer `YOUR_ACCOUNT_ID`** par votre ID de compte AWS.

### 3.2 Tester la fonction

```bash
# Créer un event de test
cat > test-event.json << 'EOF'
{
  "httpMethod": "GET",
  "path": "/health",
  "pathParameters": {},
  "queryStringParameters": {}
}
EOF

# Invoquer la fonction
aws lambda invoke \
  --function-name cityflow-api \
  --payload file://test-event.json \
  response.json

# Voir la réponse
cat response.json | jq
```

**Réponse attendue :**
```json
{
  "statusCode": 200,
  "headers": {...},
  "body": "{\"status\":\"healthy\",\"service\":\"CityFlow Analytics API\"}"
}
```

---

## 🌐 Étape 4 : Créer API Gateway

### 4.1 Créer l'API REST

```bash
aws apigateway create-rest-api \
  --name cityflow-api \
  --description "CityFlow Analytics API REST" \
  --region us-east-1
```

**Notez l'API ID** retourné (ex: `abc123xyz`)

### 4.2 Configurer via Console AWS (plus simple)

1. Aller sur **AWS Console → API Gateway**
2. Sélectionner l'API `cityflow-api`
3. **Créer les ressources** :
   - `/health` (GET)
   - `/stats` (GET)
   - `/metrics/{type}/{date}` (GET)
   - `/metrics/{date}` (GET)
   - `/report/{date}` (GET)

4. Pour chaque ressource :
   - **Méthode** : GET
   - **Type d'intégration** : Lambda Function
   - **Fonction Lambda** : `cityflow-api`
   - **Proxy Lambda** : Oui

5. **Activer CORS** pour chaque ressource

6. **Déployer l'API** :
   - Créer un nouveau stage : `prod`
   - Déployer

### 4.3 URL finale

```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
```

---

## 🧪 Étape 5 : Tests

### Test health check

```bash
curl https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "service": "CityFlow Analytics API",
  "version": "1.0.0",
  "database": "dynamodb",
  "environment": "AWS"
}
```

### Test métriques

```bash
curl https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/metrics/bikes/2025-11-03
```

### Test rapport

```bash
curl https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/report/2025-11-03
```

---

## 📊 Étape 6 : Monitoring (optionnel)

### CloudWatch Logs

```bash
# Voir les logs
aws logs tail /aws/lambda/cityflow-api --follow
```

### CloudWatch Metrics

Dans la console AWS → CloudWatch → Métriques :
- Invocations
- Durée
- Erreurs
- Throttles

### Alarmes

Créer des alarmes pour :
- Taux d'erreur > 5%
- Durée d'exécution > 10s
- Throttling

---

## 💰 Estimation des Coûts

### Lambda

- **1M requêtes/mois** : ~$0.20
- **Durée moyenne 500ms** : ~$0.83
- **Total** : ~$1/mois

### API Gateway

- **1M requêtes/mois** : ~$3.50

### DynamoDB

- **Lecture on-demand** : $0.25 par million de requêtes

**Total estimé** : ~$5/mois pour 1M requêtes

---

## 🔄 Mise à Jour du Code

### Mettre à jour la fonction Lambda

```bash
# Recréer le package
cd build
zip -r ../api-lambda.zip . -x "*.pyc" -x "*__pycache__*"
cd ..

# Mettre à jour la fonction
aws lambda update-function-code \
  --function-name cityflow-api \
  --zip-file fileb://api-lambda.zip
```

### Mettre à jour les variables d'environnement

```bash
aws lambda update-function-configuration \
  --function-name cityflow-api \
  --environment Variables="{DATABASE_TYPE=dynamodb,DYNAMODB_METRICS_TABLE=cityflow-metrics-v2}"
```

---

## 🔐 Sécurité

### Ajouter une clé API

1. **API Gateway Console** → **API Keys**
2. Créer une nouvelle clé API
3. Créer un **Usage Plan**
4. Associer l'API et la clé

### Utiliser la clé

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/metrics/bikes/2025-11-03
```

### Limiter le taux de requêtes

Dans Usage Plan :
- **Rate** : 1000 requêtes/seconde
- **Burst** : 2000
- **Quota** : 1,000,000/mois

---

## 🎯 Architecture Finale

```
Internet
   │
   ▼
┌──────────────────┐
│   CloudFront     │ (optionnel - CDN)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  API Gateway     │ ← URL publique
│  (REST API)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Lambda          │ ← Code Python
│  cityflow-api    │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│DynamoDB │ │CloudWatch│
│(Data)   │ │(Logs)    │
└─────────┘ └──────────┘
```

---

## ✅ Résumé

| Aspect | Local | AWS |
|--------|-------|-----|
| **Serveur** | Flask | API Gateway + Lambda |
| **Base de données** | MongoDB | DynamoDB |
| **URL** | http://localhost:5000 | https://xxx.execute-api.amazonaws.com/prod |
| **CORS** | Activé | Activé |
| **Coût** | Gratuit | ~$5/mois (1M req) |
| **Scalabilité** | Limitée | Infinie |

**Le même code fonctionne partout !** 🎉

