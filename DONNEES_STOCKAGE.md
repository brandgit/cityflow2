# 📦 Stockage des Données - CityFlow Analytics

## 🎯 Architecture de Stockage

Les **données et résultats** ne sont **PAS stockés dans Git** (bonne pratique).  
Ils sont stockés dans **AWS S3 et DynamoDB**.

---

## 📍 Emplacements des Données

### 1. Données Brutes (Input)
**📦 S3 Bucket** : `bucket-cityflow-paris-s3-raw`

```
s3://bucket-cityflow-paris-s3-raw/
├── api/                        # Données API temps réel
│   ├── bikes/dt=YYYY-MM-DD/
│   ├── traffic_ratp/dt=YYYY-MM-DD/
│   └── weather/dt=YYYY-MM-DD/
└── batch/                      # Données batch historiques
    ├── comptages_routiers/
    ├── chantiers/
    └── referentiel_voies/
```

---

### 2. Métriques Traitées (Output)
**🗄️ DynamoDB Table** : `cityflow-metrics`

**Structure :**
```json
{
  "data_type": "bikes",
  "date": "2025-11-04",
  "metrics": { ... },
  "timestamp": "2025-11-04T12:00:00Z"
}
```

**Types disponibles :**
- `bikes` : Métriques Vélib'
- `traffic` : Trafic routier RATP
- `weather` : Météo
- `comptages` : Comptages routiers
- `chantiers` : Chantiers
- `referentiel` : Référentiel des voies

---

### 3. Rapports Quotidiens (Output)
**🗄️ DynamoDB Table** : `cityflow-reports`

**Structure :**
```json
{
  "date": "2025-11-04",
  "summary": { ... },
  "generated_at": "2025-11-04T23:59:59Z"
}
```

---

## 📁 Fichiers Locaux (Temporaires)

Les fichiers dans `output/` sont **générés localement** pour le développement :

```
output/
├── metrics/              # Métriques JSON (ignoré par Git)
│   ├── bikes_metrics_2025-11-04.json
│   ├── traffic_metrics_2025-11-04.json
│   └── ...
├── reports/              # Rapports (ignoré par Git)
│   └── daily_report_2025-11-04.json
└── processed/            # CSV traités (ignoré par Git)
```

⚠️ **Ces fichiers ne sont PAS pushés sur GitHub** (voir `.gitignore`).

---

## 🔄 Flux de Données

```
┌─────────────┐
│   S3 Raw    │  Données brutes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Processing  │  Traitement (EC2 ou Lambda)
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ DynamoDB │   │  S3 CSV  │   │  Local   │
│ Metrics  │   │ Reports  │   │  Cache   │
└──────────┘   └──────────┘   └──────────┘
       │              │              │
       └──────────────┴──────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  API Gateway  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   Dashboard   │
              └───────────────┘
```

---

## 📊 Tailles des Données (Exemple 2025-11-04)

| Type | Taille | Stockage |
|------|--------|----------|
| `bikes_metrics` | 40 KB | DynamoDB |
| `traffic_metrics` | 9.7 KB | DynamoDB |
| `weather_metrics` | 280 B | DynamoDB |
| `chantiers_metrics` | 9.8 KB | DynamoDB |
| `referentiel_metrics` | 1.0 MB | DynamoDB |
| `comptages_metrics` | 261 MB | S3 (trop gros pour DynamoDB) |
| `daily_report` | 34 KB | DynamoDB + S3 CSV |

---

## 🔑 Accès aux Données

### Via AWS CLI

```bash
# Lister les métriques
aws dynamodb scan --table-name cityflow-metrics --region eu-west-3

# Récupérer un rapport
aws dynamodb get-item \
  --table-name cityflow-reports \
  --key '{"date": {"S": "2025-11-04"}}' \
  --region eu-west-3
```

### Via l'API

```bash
# Métriques
curl https://your-api.execute-api.eu-west-3.amazonaws.com/prod/metrics/bikes/2025-11-04

# Rapport
curl https://your-api.execute-api.eu-west-3.amazonaws.com/prod/report/2025-11-04
```

### Via le Dashboard

```
http://your-ec2-ip:8501
```

---

## 🚫 Ce Qui N'est PAS dans Git

- ❌ Fichiers CSV (trop gros)
- ❌ Fichiers JSON de métriques (générés)
- ❌ Données brutes
- ❌ Fichiers de cache

✅ **Git contient uniquement le code source**.

---

## 📝 Pourquoi Cette Architecture ?

1. **Séparation Code/Données** : Bonne pratique
2. **Git Léger** : Pas de gros fichiers
3. **Scalabilité** : S3 et DynamoDB gèrent des volumes importants
4. **Coût** : Pas de limite de stockage Git
5. **Performance** : Données distribuées dans le cloud

---

## 🔄 Backup

Les données sont automatiquement **sauvegardées** dans AWS :
- **S3** : Versioning activé
- **DynamoDB** : Point-in-time recovery (optionnel)

---

## 📌 Note Importante

Si vous avez besoin de **partager des exemples de données** :
1. Créez des **échantillons réduits**
2. Placez-les dans `output/examples/`
3. Ajoutez une exception dans `.gitignore`

**Exemple :**
```bash
mkdir -p output/examples
head -n 100 output/reports/daily_report_2025-11-04.json > output/examples/sample_report.json
```

Puis dans `.gitignore`, ajoutez :
```gitignore
!output/examples/*.json
```

---

**📍 Les données sont dans le cloud, pas dans Git ! ☁️**

