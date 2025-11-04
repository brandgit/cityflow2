# 🔄 Comparaison Déploiement Local vs AWS

## 📊 Tableau comparatif

| Aspect | 💻 Local | ☁️ AWS EC2 |
|--------|---------|-----------|
| **Base de données** | MongoDB | DynamoDB |
| **Stockage rapports** | `output/reports/` | S3 Bucket |
| **Stockage métriques** | Fichiers JSON locaux | DynamoDB + S3 |
| **Découpage fichiers** | Optionnel | Automatique (chunks) |
| **API** | Flask dev server | Flask ou Lambda |
| **Dashboard** | Streamlit local | Streamlit sur EC2 |
| **Automatisation** | Manuel | Cron / EventBridge |
| **Coût** | Gratuit | ~$40-75/mois |
| **Disponibilité** | Pendant que PC allumé | 24/7 |
| **Scalabilité** | Limitée par PC | Élastique |

---

## 🔧 Différences de configuration

### Fichier .env

#### 💻 Local
```bash
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=cityflow

# Chemins locaux relatifs
DATA_DIR_RAW=bucket-cityflow-paris-s3-raw/cityflow-raw/raw
OUTPUT_DIR=output
```

#### ☁️ AWS EC2
```bash
AWS_EXECUTION_ENV=AWS_EC2
AWS_REGION=eu-west-3
DATABASE_TYPE=dynamodb
USE_DYNAMODB=true
USE_S3=true

# Tables et buckets AWS
DYNAMODB_TABLE_METRICS=cityflow-metrics
DYNAMODB_TABLE_REPORTS=cityflow-reports
S3_BUCKET_REPORTS=cityflow-reports-paris

# Chemins EC2
DATA_DIR_RAW=/home/ubuntu/cityflow/data/raw
OUTPUT_DIR=/home/ubuntu/cityflow/output
```

---

## 🔀 Comportement automatique du code

Le code **détecte automatiquement** l'environnement et s'adapte :

### Détection de l'environnement

```python
# Dans utils/database_factory.py
import os

def get_database_service():
    # Si AWS_EXECUTION_ENV est défini → DynamoDB
    if os.getenv("AWS_EXECUTION_ENV"):
        return DynamoDBServiceAdapter()
    
    # Si USE_DYNAMODB=true → DynamoDB
    if os.getenv("USE_DYNAMODB", "false").lower() == "true":
        return DynamoDBServiceAdapter()
    
    # Sinon → MongoDB
    return MongoDBService()
```

### Export des rapports

```python
# Dans report_generator/daily_report_generator.py
def export_report(self, report):
    is_aws = os.getenv("AWS_EXECUTION_ENV") or os.getenv("USE_S3") == "true"
    
    if is_aws:
        # AWS : CSV → S3, JSON → DynamoDB
        save_csv_to_s3(csv_data, bucket, key)
        save_json_to_dynamodb(json_data, table)
    else:
        # Local : CSV → output/reports/, JSON → MongoDB
        save_csv_locally(csv_data, "output/reports/")
        save_json_to_mongodb(json_data)
```

### Découpage des fichiers

```python
# Dans processors/comptages_processor.py
def process_large_file(self, file_path):
    # AWS ou fichier > 500 MB → chunks
    if os.getenv("AWS_EXECUTION_ENV") or file_size > MAX_FILE_SIZE_MB:
        chunks = chunk_file(file_path, EC2_CHUNK_SIZE)
        # Traiter par chunks
    else:
        # Fichier normal
        return self.process(data)
```

---

## 📈 Flux de données

### 💻 En local

```
Données brutes (local)
    ↓
Processors (Python)
    ↓
MongoDB (local) + Fichiers JSON
    ↓
Dashboard Streamlit (local)
```

### ☁️ Sur AWS

```
Données brutes (S3 ou local EC2)
    ↓
Processors sur EC2 (Python)
    ↓
DynamoDB + S3 (CSV)
    ↓
API Flask sur EC2
    ↓
Dashboard Streamlit sur EC2
```

---

## 🚀 Migration Local → AWS

### Étape 1 : Préparer les données

```bash
# Local : Exporter MongoDB vers JSON
python3 -c "
from utils.mongodb_service import MongoDBService
import json

db = MongoDBService()
for metric_type in ['bikes', 'traffic', 'comptages', 'chantiers']:
    data = db.load_metrics(metric_type, '2025-11-04')
    if data:
        with open(f'{metric_type}_export.json', 'w') as f:
            json.dump(data, f)
"

# Uploader vers S3
aws s3 cp *.json s3://cityflow-migration/
```

### Étape 2 : Sur EC2, importer vers DynamoDB

```bash
# Sur EC2
python3 -c "
from utils.dynamodb_service_adapter import DynamoDBServiceAdapter
import json

db = DynamoDBServiceAdapter()
for metric_type in ['bikes', 'traffic', 'comptages', 'chantiers']:
    with open(f'{metric_type}_export.json', 'r') as f:
        data = json.load(f)
        db.save_metrics(data, metric_type, '2025-11-04')
"
```

### Étape 3 : Modifier .env

```bash
# Passer de MongoDB à DynamoDB
sed -i 's/DATABASE_TYPE=mongodb/DATABASE_TYPE=dynamodb/' .env
sed -i 's/USE_DYNAMODB=false/USE_DYNAMODB=true/' .env
```

### Étape 4 : Tester

```bash
python3 test_database_connection.py
```

---

## 💰 Optimisation des coûts

### Option 1 : Instance Spot (jusqu'à 90% moins cher)

```bash
# Lancer une instance spot
aws ec2 request-spot-instances \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification file://spot-config.json
```

⚠️ **Attention :** L'instance peut être interrompue

### Option 2 : Arrêt automatique la nuit

```bash
# Arrêter l'instance à 22h
0 22 * * * aws ec2 stop-instances --instance-ids i-xxxxx

# Démarrer à 6h
0 6 * * * aws ec2 start-instances --instance-ids i-xxxxx
```

**Économie :** ~50% si arrêt 16h/jour

### Option 3 : Lambda au lieu d'EC2 (pour processors uniquement)

- Pas de coût quand inactif
- Facturation à la seconde
- Limite : 15 min d'exécution max
- Idéal pour : traitement quotidien rapide

---

## 🎯 Recommandations par usage

### Développement / Test
- **Local** : MongoDB + fichiers JSON
- Gratuit, rapide à itérer

### Production légère (< 10 utilisateurs)
- **EC2 t3.medium** + DynamoDB + S3
- ~$40/mois
- Dashboard accessible 24/7

### Production intensive (> 10 utilisateurs)
- **EC2 t3.large/xlarge** + DynamoDB + S3 + CloudFront
- ~$100-200/mois
- Haute disponibilité

### Serverless (traitement uniquement)
- **Lambda** + DynamoDB + S3 + EventBridge
- ~$5-20/mois (usage modéré)
- Pas de maintenance de serveur

---

## ✅ Checklist de migration

- [ ] Créer instance EC2
- [ ] Créer table DynamoDB
- [ ] Créer bucket S3
- [ ] Configurer rôle IAM
- [ ] Déployer le code
- [ ] Configurer .env pour AWS
- [ ] Tester la connexion DynamoDB
- [ ] Exécuter un traitement test
- [ ] Vérifier DynamoDB et S3
- [ ] Configurer cron/systemd
- [ ] Lancer API et Dashboard
- [ ] Tester l'accès externe
- [ ] Configurer monitoring
- [ ] Configurer backups

---

**Bon déploiement !** 🚀

