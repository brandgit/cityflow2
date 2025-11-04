#!/bin/bash

# Script pour créer et configurer AWS API Gateway pour CityFlow Analytics API
# Usage: ./setup_api_gateway.sh [EC2_IP] [REGION]

set -e

# Configuration
EC2_IP="${1:-15.236.210.200}"
EC2_PORT="${EC2_PORT:-5000}"
REGION="${2:-eu-west-3}"
API_NAME="cityflow-api"
STAGE_NAME="prod"

echo "🚀 Configuration API Gateway pour CityFlow Analytics"
echo "=================================================="
echo "📍 EC2 IP: $EC2_IP"
echo "📍 Port: $EC2_PORT"
echo "📍 Région: $REGION"
echo ""

# Vérifier que AWS CLI est installé
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI n'est pas installé"
    echo "💡 Installation: pip install awscli"
    exit 1
fi

# Vérifier les credentials AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Credentials AWS non configurés"
    echo "💡 Configurez avec: aws configure"
    exit 1
fi

echo "✅ AWS CLI configuré"
echo ""

# Étape 1 : Créer l'API HTTP
echo "📦 Étape 1 : Création de l'API HTTP..."
API_RESPONSE=$(aws apigatewayv2 create-api \
    --name "$API_NAME" \
    --protocol-type HTTP \
    --cors-configuration AllowOrigins='*',AllowMethods='GET,OPTIONS',AllowHeaders='*',MaxAge=300 \
    --region "$REGION" \
    --output json)

API_ID=$(echo "$API_RESPONSE" | jq -r '.ApiId')
API_ENDPOINT=$(echo "$API_RESPONSE" | jq -r '.ApiEndpoint')

if [ -z "$API_ID" ] || [ "$API_ID" == "null" ]; then
    echo "❌ Erreur lors de la création de l'API"
    exit 1
fi

echo "✅ API créée : $API_ID"
echo "📍 Endpoint : $API_ENDPOINT"
echo ""

# Étape 2 : Créer l'intégration HTTP
echo "📦 Étape 2 : Création de l'intégration HTTP..."
INTEGRATION_URI="http://${EC2_IP}:${EC2_PORT}/{proxy}"

INTEGRATION_RESPONSE=$(aws apigatewayv2 create-integration \
    --api-id "$API_ID" \
    --integration-type HTTP_PROXY \
    --integration-uri "$INTEGRATION_URI" \
    --integration-method ANY \
    --payload-format-version "1.0" \
    --region "$REGION" \
    --output json)

INTEGRATION_ID=$(echo "$INTEGRATION_RESPONSE" | jq -r '.IntegrationId')

if [ -z "$INTEGRATION_ID" ] || [ "$INTEGRATION_ID" == "null" ]; then
    echo "❌ Erreur lors de la création de l'intégration"
    exit 1
fi

echo "✅ Intégration créée : $INTEGRATION_ID"
echo "📍 URI : $INTEGRATION_URI"
echo ""

# Étape 3 : Créer la route catch-all
echo "📦 Étape 3 : Création de la route catch-all..."
ROUTE_RESPONSE=$(aws apigatewayv2 create-route \
    --api-id "$API_ID" \
    --route-key "ANY /{proxy+}" \
    --target "integrations/$INTEGRATION_ID" \
    --region "$REGION" \
    --output json)

ROUTE_ID=$(echo "$ROUTE_RESPONSE" | jq -r '.RouteId')
echo "✅ Route créée : $ROUTE_ID"
echo ""

# Étape 4 : Créer le stage
echo "📦 Étape 4 : Création du stage '$STAGE_NAME'..."
STAGE_RESPONSE=$(aws apigatewayv2 create-stage \
    --api-id "$API_ID" \
    --stage-name "$STAGE_NAME" \
    --auto-deploy \
    --region "$REGION" \
    --output json)

echo "✅ Stage créé : $STAGE_NAME"
echo ""

# Étape 5 : Récupérer l'URL finale
FINAL_URL="${API_ENDPOINT}/${STAGE_NAME}"

echo "=================================================="
echo "🎉 API Gateway configuré avec succès !"
echo "=================================================="
echo ""
echo "📋 Informations de l'API :"
echo "   API ID      : $API_ID"
echo "   Stage       : $STAGE_NAME"
echo "   URL         : $FINAL_URL"
echo "   EC2 Backend : http://${EC2_IP}:${EC2_PORT}"
echo ""
echo "🧪 Tests :"
echo "   Health     : curl $FINAL_URL/health"
echo "   Stats      : curl $FINAL_URL/stats"
echo "   Métriques  : curl $FINAL_URL/metrics/bikes/2025-11-04"
echo "   Rapport    : curl $FINAL_URL/report/2025-11-04"
echo ""
echo "📝 Routes disponibles :"
echo "   GET /health"
echo "   GET /stats"
echo "   GET /metrics/{type}/{date}"
echo "   GET /metrics/{date}"
echo "   GET /report/{date}"
echo "   GET /docs"
echo ""
echo "💡 Pour supprimer l'API :"
echo "   aws apigatewayv2 delete-api --api-id $API_ID --region $REGION"
echo ""

# Sauvegarder les informations dans un fichier
CONFIG_FILE="api_gateway_config.json"
cat > "$CONFIG_FILE" <<EOF
{
  "api_id": "$API_ID",
  "api_name": "$API_NAME",
  "stage_name": "$STAGE_NAME",
  "region": "$REGION",
  "url": "$FINAL_URL",
  "ec2_backend": "http://${EC2_IP}:${EC2_PORT}",
  "integration_id": "$INTEGRATION_ID",
  "route_id": "$ROUTE_ID",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "💾 Configuration sauvegardée dans : $CONFIG_FILE"
echo ""

