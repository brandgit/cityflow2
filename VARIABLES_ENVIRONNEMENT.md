# Variables d'environnement pour CityFlow Analytics

Ce document décrit toutes les variables d'environnement nécessaires pour configurer le projet en production AWS.

## Configuration AWS

### DynamoDB
- `DYNAMODB_METRICS_TABLE` : Nom de la table DynamoDB pour stocker les métriques (défaut: `cityflow-metrics`)
- `DYNAMODB_REPORTS_TABLE` : Nom de la table DynamoDB pour stocker les rapports (défaut: `cityflow-daily-reports`)
- `AWS_REGION` : Région AWS (défaut: `us-east-1`)

### S3
- `S3_REPORTS_BUCKET` : Nom du bucket S3 pour stocker les rapports CSV (défaut: `cityflow-reports`)
- `S3_REPORTS_PREFIX` : Préfixe dans le bucket pour les rapports (défaut: `reports`)

## Chemins de données (optionnels)

En production EC2, ces chemins pointent vers S3 (via EFS ou montage) :

- `DATA_DIR` : Répertoire racine des données
- `BATCH_DATA_PATH` : Chemin des données batch (CSV)
- `API_DATA_PATH` : Chemin des données API (JSON)
- `COMPTAGES_CSV` : Chemin du fichier comptages-routiers-permanents-2.csv
- `CHANTIERS_CSV` : Chemin du fichier chantiers-perturbants-la-circulation.csv
- `REFERENTIEL_CSV` : Chemin du fichier référentiel géographique

## Mode de fonctionnement

- `USE_DYNAMODB` : Forcer l'utilisation de DynamoDB même en local (`true`/`false`)
- `USE_S3` : Forcer l'utilisation de S3 même en local (`true`/`false`)
- `AWS_EXECUTION_ENV` : Automatiquement défini dans Lambda/EC2

## Logs

- `LOG_LEVEL` : Niveau de log (défaut: `INFO`)

## Exemple de configuration pour EC2

```bash
export AWS_REGION=eu-west-1
export DYNAMODB_METRICS_TABLE=cityflow-metrics-prod
export DYNAMODB_REPORTS_TABLE=cityflow-daily-reports-prod
export S3_REPORTS_BUCKET=cityflow-reports-prod
export S3_REPORTS_PREFIX=reports
export DATA_DIR=/mnt/efs/data
```

## Notes

- En développement local, les métriques sont sauvegardées dans `output/metrics/` par défaut
- En production AWS (Lambda/EC2), les métriques sont automatiquement stockées dans DynamoDB
- Les rapports CSV sont stockés dans S3 et les rapports JSON dans DynamoDB

