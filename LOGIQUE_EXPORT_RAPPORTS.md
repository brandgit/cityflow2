# 📊 Logique d'Export des Rapports CityFlow

## Vue d'ensemble

Le système d'export des rapports s'adapte automatiquement selon l'environnement d'exécution.

---

## 🎯 Logique de décision

```
┌─────────────────────────────────────────────────────────────┐
│          Génération du Rapport Quotidien                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────────┐
            │ Environnement AWS? │
            │ (AWS_EXECUTION_ENV)│
            └────┬──────────┬────┘
                 │          │
         OUI ☁️  │          │  NON 🏠
                 │          │
                 ▼          ▼
    ┌────────────────┐  ┌──────────────────┐
    │  AWS PRODUCTION│  │ LOCAL DÉVELOPPEMENT│
    └────────────────┘  └──────────────────┘
         │                    │
         │                    │
    CSV  │  JSON         CSV  │  JSON
         │                    │
         ▼                    ▼
    ┌─────────┐          ┌──────────────┐
    │   S3    │          │ output/      │
    │  Bucket │          │ reports/     │
    └─────────┘          └──────────────┘
         │                    │
         ▼                    ▼
    ┌──────────┐         ┌─────────┐
    │ DynamoDB │         │ MongoDB │
    └──────────┘         └─────────┘
```

---

## 🏠 Mode LOCAL (Développement)

### Configuration
```bash
# .env
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=cityflow
```

### Stockage
| Type | Destination | Format |
|------|-------------|--------|
| **Rapport JSON** | MongoDB (collection `reports`) | Document JSON |
| **Rapport CSV** | `output/reports/daily_report_YYYY-MM-DD.csv` | Fichier CSV local |

### Exemple de sortie
```
[Export CSV] → Répertoire local (output/reports/)
✓ Rapport CSV: output/reports/daily_report_2025-11-03.csv

[Export JSON] → MONGODB
✓ Rapport JSON exporté vers MONGODB

============================================================
🏠 Rapport exporté en mode LOCAL DÉVELOPPEMENT
   - CSV : Répertoire local (output/reports/)
   - JSON : MONGODB
============================================================
```

### Avantages
✅ Pas besoin de connexion AWS  
✅ Fichiers accessibles immédiatement  
✅ Visualisation dans MongoDB Compass  
✅ Développement rapide

---

## ☁️ Mode AWS (Production)

### Configuration
Aucune configuration nécessaire ! AWS Lambda définit automatiquement :
```bash
AWS_EXECUTION_ENV=AWS_Lambda_python3.10  # Défini par AWS
```

### Stockage
| Type | Destination | Format |
|------|-------------|--------|
| **Rapport JSON** | DynamoDB (table `cityflow-daily-reports`) | Document DynamoDB |
| **Rapport CSV** | S3 (bucket `cityflow-reports`) | Objet S3 |

### Exemple de sortie
```
[Export CSV] → S3 Bucket
✓ Rapport CSV exporté vers S3: s3://cityflow-reports/reports/daily_report_2025-11-03.csv

[Export JSON] → DynamoDB
✓ Rapport JSON exporté vers DYNAMODB

============================================================
☁️  Rapport exporté en mode AWS PRODUCTION
   - CSV : S3 Bucket
   - JSON : DynamoDB
============================================================
```

### Avantages
✅ Scalable automatiquement  
✅ Haute disponibilité  
✅ Backup automatique  
✅ Accès via API Gateway

---

## 🔧 Code de détection

### Dans `report_generator/daily_report_generator.py`

```python
def export_report(self, report: DailyReport):
    """
    Exporte le rapport selon l'environnement
    """
    # Détection automatique de l'environnement
    is_aws = os.getenv("AWS_EXECUTION_ENV") is not None
    
    # ====== EXPORT CSV ======
    if is_aws:
        # ☁️ AWS : Export vers S3
        save_report_to_s3_csv(
            csv_content=csv_content,
            bucket_name="cityflow-reports",
            s3_prefix="reports"
        )
    else:
        # 🏠 Local : Export vers fichier local
        with open("output/reports/daily_report_2025-11-03.csv", 'w') as f:
            f.write(csv_content)
    
    # ====== EXPORT JSON ======
    # La factory choisit automatiquement MongoDB ou DynamoDB
    db_service = get_database_service()  # MongoDB en local, DynamoDB en AWS
    db_service.save_report(report_dict, date)
```

---

## 📋 Variables d'environnement

### Détection automatique

| Variable | Défini par | Valeur | Action |
|----------|-----------|--------|--------|
| `AWS_EXECUTION_ENV` | AWS Lambda/EC2 | `AWS_Lambda_python3.10` | Force mode AWS |
| `DATABASE_TYPE` | Utilisateur (.env) | `mongodb` ou `dynamodb` | Choisit la BDD |
| `USE_S3` | Utilisateur (.env) | `true` ou `false` | Force S3 en local (test) |

### Configuration manuelle (pour tester AWS en local)

```bash
# .env
USE_S3=true                      # Force l'export CSV vers S3
DATABASE_TYPE=dynamodb           # Force DynamoDB
AWS_REGION=us-east-1
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports
S3_REPORTS_BUCKET=cityflow-reports
```

---

## 🎨 Diagramme de flux complet

```
┌────────────────────────────────────────────────────────────┐
│  python3 report_generator/main.py                          │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ DailyReportGenerator         │
        │  - load_metrics()             │
        │  - generate_report()          │
        │  - export_report()            │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ Détection environnement      │
        │ is_aws = AWS_EXECUTION_ENV?  │
        └──────┬───────────────┬───────┘
               │               │
         OUI   │               │   NON
               │               │
               ▼               ▼
    ┌──────────────────┐  ┌────────────────────┐
    │  Mode AWS        │  │  Mode Local        │
    └──────────────────┘  └────────────────────┘
               │               │
               │               │
    ┌──────────┴─────┐    ┌───┴──────────┐
    │                │    │              │
    ▼                ▼    ▼              ▼
┌────────┐   ┌──────────┐ ┌──────────┐ ┌─────────┐
│   S3   │   │ DynamoDB │ │  Local   │ │ MongoDB │
│ (CSV)  │   │  (JSON)  │ │  (CSV)   │ │ (JSON)  │
└────────┘   └──────────┘ └──────────┘ └─────────┘
```

---

## 🧪 Tester les deux modes

### Test mode LOCAL (actuel)
```bash
# S'assurer que DATABASE_TYPE=mongodb dans .env
python3 report_generator/main.py

# Vérifier les fichiers
ls -lh output/reports/
mongosh cityflow --eval "db.reports.find().pretty()"
```

### Test mode AWS (simulation)
```bash
# Modifier .env
DATABASE_TYPE=dynamodb
USE_S3=true

# S'assurer que boto3 est configuré
aws configure

# Exécuter
python3 report_generator/main.py

# Vérifier dans AWS Console
aws dynamodb scan --table-name cityflow-daily-reports
aws s3 ls s3://cityflow-reports/reports/
```

---

## 📊 Exemple de rapport généré

### Structure MongoDB (Local)
```json
{
  "_id": ObjectId("..."),
  "report_id": "daily_report_2025-11-03",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T20:00:00",
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

### Structure DynamoDB (AWS)
```json
{
  "report_id": "daily_report_2025-11-03",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T20:00:00",
  "report": {
    "date": "2025-11-03",
    "summary": {...},
    "top_10_troncons_frequentes": [...]
  },
  "ttl": 1735689600
}
```

### Fichier CSV (Local)
```
output/reports/daily_report_2025-11-03.csv

Résumé;Valeur
Total véhicules Paris;1234567
Temps perdu total (min);89456
Tronçons saturés;45
...
```

### Fichier S3 (AWS)
```
s3://cityflow-reports/reports/daily_report_2025-11-03.csv
```

---

## ✅ Résumé

| Aspect | Local 🏠 | AWS ☁️ |
|--------|---------|--------|
| **Détection** | Pas de `AWS_EXECUTION_ENV` | `AWS_EXECUTION_ENV` présent |
| **CSV** | `output/reports/*.csv` | S3 Bucket |
| **JSON** | MongoDB | DynamoDB |
| **Coût** | Gratuit | Pay-per-use |
| **Scalabilité** | Limitée | Infinie |
| **Accès** | Local uniquement | Via API/Console |

---

## 🎓 Commandes utiles

```bash
# Générer rapport en local
python3 report_generator/main.py

# Voir les rapports MongoDB
mongosh cityflow --eval "db.reports.find().limit(1).pretty()"

# Voir les fichiers CSV locaux
cat output/reports/daily_report_2025-11-03.csv

# Tester avec AWS (si configuré)
DATABASE_TYPE=dynamodb USE_S3=true python3 report_generator/main.py
```

---

**La logique s'adapte automatiquement ! Aucune modification de code nécessaire lors du déploiement !** 🚀

