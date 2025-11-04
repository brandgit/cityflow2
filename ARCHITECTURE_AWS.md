# Architecture AWS - CityFlow Analytics

## 🏗️ Séparation des Instances

Le projet est conçu pour s'exécuter sur **deux instances AWS distinctes** :

### Instance 1 : Traitement des Données
- **Point d'entrée** : `main.py`
- **Services AWS** : Lambda (batch) + EC2 (gros fichiers)
- **Trigger** : EventBridge (cron quotidien) ou S3 (nouveau fichier)
- **Output** : Métriques dans `output/metrics/` → S3

### Instance 2 : Génération Rapport
- **Point d'entrée** : `report_generator/main.py`
- **Services AWS** : Lambda ou EC2
- **Trigger** : EventBridge (cron, après traitement) ou S3 (métriques disponibles)
- **Input** : Lit depuis S3 `output/metrics/*.json`
- **Output** : Rapport dans `output/reports/` → S3

---

## 📊 Flux AWS Complet

```
┌─────────────────────────────────────────────────────────┐
│              EVENTBRIDGE (Cron 00:00 UTC)               │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐      ┌──────────────────────┐
│ INSTANCE 1   │      │   INSTANCE 2          │
│ Processing   │      │   Report Generator    │
├──────────────┤      ├──────────────────────┤
│ Lambda/EC2   │      │ Lambda/EC2           │
│              │      │                      │
│ main.py      │      │ report_generator/    │
│              │      │   main.py            │
└──────┬───────┘      └──────┬───────────────┘
       │                      │
       │ (traitement)         │ (génération)
       │                      │
       ▼                      ▼
┌──────────────┐      ┌──────────────────────┐
│ S3 Bucket    │      │ S3 Bucket            │
│              │      │                      │
│ metrics/     │ ────►│ reports/             │
│  - bikes_*   │ READ │  - daily_report_*   │
│  - comptages │      │                      │
│  - weather_* │      │                      │
└──────────────┘      └──────────────────────┘
```

---

## 🔄 Déclenchement Automatique

### Option 1 : EventBridge Séquentiel

```yaml
# Rule 1: Traitement (00:00 UTC)
Schedule: cron(0 0 * * ? *)
Target: Lambda (main.py)

# Rule 2: Génération Rapport (00:30 UTC, après traitement)
Schedule: cron(30 0 * * ? *)
Target: Lambda (report_generator/main.py)
```

### Option 2 : S3 Event Triggers

```yaml
# Traitement déclenché par upload S3 raw/
S3 Event: s3://bucket-cityflow-raw/raw/**/*
Trigger: Lambda (main.py)

# Rapport déclenché quand métriques disponibles
S3 Event: s3://bucket-cityflow-processed/metrics/*_metrics_*.json
Trigger: Lambda (report_generator/main.py)
```

---

## 📝 Configuration Lambda

### Lambda Processing (`main.py`)

```python
# Lambda handler
def lambda_handler(event, context):
    from main import main
    results = main()
    return {
        'statusCode': 200,
        'body': {
            'success': results is not None,
            'metrics_exported': list of files
        }
    }
```

### Lambda Report Generator (`report_generator/main.py`)

```python
# Lambda handler
def lambda_handler(event, context):
    from report_generator.main import main
    # Date peut venir de event ou environ
    date = event.get('date') or context.date
    exit_code = main()
    return {
        'statusCode': 200 if exit_code == 0 else 500,
        'body': {
            'date': date,
            'report_generated': True
        }
    }
```

---

## 🔧 Variables d'Environnement

### Pour Processing (main.py)
```
S3_BUCKET_RAW=cityflow-raw
S3_BUCKET_PROCESSED=cityflow-processed
DYNAMODB_TABLE_PREFIX=CityFlow
```

### Pour Report Generator (report_generator/main.py)
```
S3_BUCKET_METRICS=cityflow-processed/metrics
S3_BUCKET_REPORTS=cityflow-processed/reports
REPORT_DATE=2025-11-03  # Optionnel
```

---

## 📦 Structure S3 Recommandée

```
s3://cityflow-data/
├── raw/                          # Données brutes (input)
│   ├── batch/
│   │   ├── comptages-*.csv
│   │   └── chantiers-*.csv
│   └── api/
│       ├── bikes/
│       ├── traffic/
│       └── weather/
│
├── processed/                    # Données traitées
│   ├── metrics/                  # ✨ Sortie Processing
│   │   ├── bikes_metrics_*.json
│   │   ├── comptages_metrics_*.json
│   │   ├── weather_metrics_*.json
│   │   └── ...
│   │
│   └── reports/                  # ✨ Sortie Report Generator
│       ├── daily_report_*.json
│       └── daily_report_*.csv
│
└── archive/                      # Archivage (optionnel)
    └── processed/chunks/         # Chunks nettoyés après traitement
```

---

## 🚀 Exécution Locale (Simulation)

### Traitement
```bash
python main.py
```

### Génération Rapport
```bash
python report_generator/main.py
# OU avec date spécifique
python report_generator/main.py 2025-11-03
```

---

## 🔐 IAM Roles Requis

### Lambda Processing
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::cityflow-raw/*",
    "arn:aws:s3:::cityflow-processed/*"
  ]
}
```

### Lambda Report Generator
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject"
  ],
  "Resource": [
    "arn:aws:s3:::cityflow-processed/metrics/*",
    "arn:aws:s3:::cityflow-processed/reports/*"
  ]
}
```

---

## ⏱️ Timeline Recommandée

```
00:00 UTC - EventBridge déclenche Processing
00:00-00:25 - Traitement des données
00:25 - Métriques exportées dans S3
00:30 - EventBridge déclenche Report Generator
00:30-00:35 - Génération rapport
00:35 - Rapport disponible dans S3
```

---

## 📊 Monitoring

### CloudWatch Metrics

**Processing** :
- Durée traitement
- Nombre de chunks traités
- Taille fichiers métriques générés
- Erreurs par type de données

**Report Generator** :
- Durée génération
- Nombre de métriques chargées
- Taille rapport généré
- Erreurs chargement métriques

---

## ✅ Avantages de la Séparation

1. **Scalabilité** : Les deux peuvent scaler indépendamment
2. **Coûts** : Report Generator léger (pas besoin EC2)
3. **Robustesse** : Si traitement échoue, rapport peut être régénéré
4. **Flexibilité** : Peut générer plusieurs rapports (dates différentes)
5. **Isolation** : Échec d'un processus n'affecte pas l'autre

