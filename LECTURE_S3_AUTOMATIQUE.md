# 📥 Lecture Automatique depuis S3

## 🎯 Fonctionnalité Ajoutée

Le code peut désormais **lire automatiquement** les données brutes depuis S3 en mode AWS, tout en conservant le mode local pour le développement.

## 🔄 Détection Automatique

Le système détecte automatiquement l'environnement et choisit la source de données appropriée :

```python
# Détection dans processors/main.py
def load_raw_data(config):
    # 🏠 Mode Local → Lecture depuis fichiers locaux
    if not AWS_EXECUTION_ENV and not USE_S3:
        return load_raw_data_from_local(config)
    
    # ☁️ Mode AWS → Téléchargement depuis S3
    else:
        return load_raw_data_from_s3(config)
```

---

## ⚙️ Configuration

### 🏠 Mode Local (Développement)

**Fichier `.env` :**

```bash
# Base de données
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017/

# Pas besoin de S3
USE_S3=false

# Données lues depuis fichiers locaux
# bucket-cityflow-paris-s3-raw/cityflow-raw/raw/
```

**Résultat :**
- ✅ Lecture depuis fichiers locaux
- ✅ MongoDB pour stockage métriques
- ✅ Pas de connexion AWS nécessaire

---

### ☁️ Mode AWS EC2

**Fichier `.env` sur EC2 :**

```bash
# Environnement AWS
AWS_EXECUTION_ENV=AWS_EC2
AWS_REGION=eu-west-3

# Base de données
DATABASE_TYPE=dynamodb
USE_DYNAMODB=true

# S3 activé pour lecture données brutes
USE_S3=true
S3_RAW_BUCKET=cityflow-raw-data
S3_RAW_PREFIX=raw

# Tables DynamoDB
DYNAMODB_METRICS_TABLE=cityflow-metrics
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports

# Cache local pour fichiers S3
S3_CACHE_DIR=/home/ubuntu/cityflow/s3_cache
```

**Résultat :**
- ✅ Téléchargement automatique depuis S3
- ✅ Cache local pour éviter re-téléchargement
- ✅ DynamoDB pour stockage métriques
- ✅ Export rapports vers S3

---

## 📊 Structure S3 Attendue

Le code s'attend à trouver les données dans S3 selon cette structure :

```
s3://cityflow-raw-data/
└── raw/
    ├── api/
    │   ├── bikes/
    │   │   └── dt=2025-11-04/
    │   │       └── hour=02/
    │   │           └── bikes_data.json
    │   ├── traffic/
    │   │   └── dt=2025-11-04/
    │   │       └── hour=02/
    │   │           └── traffic_data.json
    │   └── weather/
    │       └── dt=2025-11-04/
    │           └── hour=02/
    │               └── weather_data.json
    └── batch/
        ├── comptages-routiers-permanents-2.csv
        ├── chantiers-perturbants-la-circulation.csv
        └── referentiel-geographique-pour-les-donnees-trafic-issues-des-capteurs-permanents.csv
```

---

## 🚀 Fonctions S3 Ajoutées

### Dans `utils/aws_services.py`

**1. Lister les fichiers S3**

```python
def list_s3_files(bucket_name: str, prefix: str, extension: str = None) -> List[str]:
    """Liste tous les fichiers dans un bucket/préfixe S3"""
    pass
```

**2. Télécharger un fichier S3**

```python
def download_s3_file_to_temp(bucket_name: str, s3_key: str, local_dir: str) -> str:
    """Télécharge un fichier S3 vers un répertoire local temporaire"""
    pass
```

**3. Télécharger un répertoire S3**

```python
def download_s3_directory(bucket_name: str, s3_prefix: str, local_dir: str, 
                         extensions: List[str] = None) -> List[str]:
    """Télécharge tous les fichiers d'un "répertoire" S3"""
    pass
```

**4. Charger JSON depuis S3**

```python
def load_json_from_s3(bucket_name: str, s3_key: str) -> Dict:
    """Charge un fichier JSON directement depuis S3 (sans téléchargement)"""
    pass
```

---

## 🔧 Flux de Traitement

### 🏠 Mode Local

```
1. Démarrage → Détection environnement (LOCAL)
2. load_raw_data() → load_raw_data_from_local()
3. Lecture fichiers depuis bucket-cityflow-paris-s3-raw/
4. Traitement données
5. Export vers MongoDB + fichiers locaux
```

### ☁️ Mode AWS EC2

```
1. Démarrage → Détection environnement (AWS)
2. load_raw_data() → load_raw_data_from_s3()
3. Téléchargement depuis S3 → Cache local (s3_cache/)
4. Traitement données
5. Export vers DynamoDB + S3
```

---

## 📝 Exemple d'Utilisation

### Test en Local (Mode Simulation)

```bash
# .env
USE_S3=true  # Force le mode S3 même en local (simulation)
S3_RAW_BUCKET=cityflow-raw-data
S3_RAW_PREFIX=raw

# Lancer le traitement
python3 main.py
```

**Résultat :**
```
☁️  Mode AWS détecté - Téléchargement depuis S3...
📥 Téléchargement bikes depuis S3://cityflow-raw-data/raw/api/bikes/dt=2025-11-04/hour=02/
[SIMULATION] S3.list_files(cityflow-raw-data/raw/api/bikes/dt=2025-11-04/hour=02/)
[SIMULATION] S3.download_file(cityflow-raw-data/...)
✓ 0 fichiers téléchargés depuis S3://cityflow-raw-data/raw/api/bikes/dt=2025-11-04/hour=02/
```

### Test sur EC2 (Réel)

```bash
# Sur EC2 avec rôle IAM configuré

# .env
AWS_EXECUTION_ENV=AWS_EC2
USE_S3=true
S3_RAW_BUCKET=cityflow-raw-data

# Lancer le traitement
python3 main.py
```

**Résultat :**
```
☁️  Mode AWS détecté - Téléchargement depuis S3...
📥 Téléchargement bikes depuis S3://cityflow-raw-data/raw/api/bikes/dt=2025-11-04/hour=02/
✓ Téléchargé depuis S3: raw/api/bikes/dt=2025-11-04/hour=02/bikes_data.json → s3_cache/bikes/bikes_data.json
✓ 3 fichiers téléchargés depuis S3://cityflow-raw-data/raw/api/bikes/dt=2025-11-04/hour=02/
📥 Téléchargement traffic depuis S3://...
...
✓ Téléchargement depuis S3 terminé
```

---

## 🎯 Avantages

### ✅ **Automatique**
- Détection environnement automatique
- Pas besoin de changer le code

### ✅ **Cache Local**
- Fichiers téléchargés une fois
- Réutilisés si déjà présents
- Économise bande passante

### ✅ **Fallback**
- Si S3 échoue → Tentative lecture locale
- Robuste et résilient

### ✅ **Transparent**
- Le reste du code ne change pas
- Même interface pour local et S3

---

## 🔐 Permissions IAM Requises (EC2)

Le rôle IAM attaché à l'instance EC2 doit avoir :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::cityflow-raw-data",
        "arn:aws:s3:::cityflow-raw-data/*"
      ]
    }
  ]
}
```

---

## 📦 Upload des Données vers S3

Pour uploader vos données locales vers S3 :

### Option 1 : AWS CLI

```bash
# Uploader un fichier
aws s3 cp bucket-cityflow-paris-s3-raw/cityflow-raw/raw/batch/comptages-routiers-permanents-2.csv \
    s3://cityflow-raw-data/raw/batch/

# Uploader un répertoire complet
aws s3 sync bucket-cityflow-paris-s3-raw/cityflow-raw/raw/ \
    s3://cityflow-raw-data/raw/ \
    --exclude "*.git/*"
```

### Option 2 : Script Python

```python
from utils.aws_services import S3Service

service = S3Service("cityflow-raw-data")

# Upload fichiers API
service.upload_file(
    "bucket-cityflow-paris-s3-raw/cityflow-raw/raw/api/bikes/dt=2025-11-04/hour=02/bikes_data.json",
    "raw/api/bikes/dt=2025-11-04/hour=02/bikes_data.json"
)

# Upload fichiers batch
service.upload_file(
    "bucket-cityflow-paris-s3-raw/cityflow-raw/raw/batch/comptages-routiers-permanents-2.csv",
    "raw/batch/comptages-routiers-permanents-2.csv"
)
```

---

## 🧪 Tests

### Test 1 : Vérifier Détection Environnement

```bash
# Local
python3 -c "
from processors.main import load_raw_data
from config import settings
import os

print('Environnement:', 'AWS' if os.getenv('AWS_EXECUTION_ENV') else 'Local')
print('USE_S3:', settings.USE_S3)
"
```

### Test 2 : Tester Téléchargement S3 (Simulation)

```bash
# En local, mode simulation
python3 -c "
from utils.aws_services import list_s3_files

files = list_s3_files('cityflow-raw-data', 'raw/batch/', extension='.csv')
print('Fichiers trouvés:', len(files))
for f in files:
    print('  -', f)
"
```

### Test 3 : Pipeline Complet

```bash
# Lancer le pipeline complet
python3 main.py

# Vérifier les logs
# Doit afficher : "☁️ Mode AWS détecté" ou "🏠 Mode Local détecté"
```

---

## 📚 Variables d'Environnement Complètes

| Variable | Mode Local | Mode AWS EC2 | Description |
|----------|-----------|--------------|-------------|
| `AWS_EXECUTION_ENV` | - | `AWS_EC2` | Détection auto AWS |
| `AWS_REGION` | - | `eu-west-3` | Région AWS |
| `DATABASE_TYPE` | `mongodb` | `dynamodb` | Type de BDD |
| `USE_S3` | `false` | `true` | Forcer lecture S3 |
| `S3_RAW_BUCKET` | - | `cityflow-raw-data` | Bucket données brutes |
| `S3_RAW_PREFIX` | - | `raw` | Préfixe S3 |
| `S3_CACHE_DIR` | - | `/home/ubuntu/cityflow/s3_cache` | Cache local |

---

## 🎉 Résumé

### Ce qui a été ajouté :

✅ **Fonctions de lecture S3** dans `utils/aws_services.py`  
✅ **Détection automatique environnement** dans `processors/main.py`  
✅ **Variables S3** dans `config/settings.py`  
✅ **Configuration** mise à jour dans `env.example`  
✅ **Cache local** pour performances  
✅ **Fallback automatique** si S3 échoue

### Résultat final :

**Le code fonctionne maintenant de manière totalement transparente :**

- 🏠 **En local** : Lit depuis fichiers locaux, écrit dans MongoDB
- ☁️ **Sur EC2** : Télécharge depuis S3, écrit dans DynamoDB
- 🔄 **Bascule automatique** selon l'environnement
- 🚀 **Zéro configuration manuelle** nécessaire

---

## 🆘 Dépannage

### Problème : "Erreur lors du téléchargement depuis S3"

**Solution :**
1. Vérifier les permissions IAM de l'instance EC2
2. Vérifier que le bucket S3 existe : `aws s3 ls s3://cityflow-raw-data/`
3. Vérifier la structure S3 : `aws s3 ls s3://cityflow-raw-data/raw/ --recursive`

### Problème : "Mode AWS détecté mais je suis en local"

**Solution :**
Vérifier la variable `USE_S3` dans `.env` :
```bash
USE_S3=false  # Forcer mode local
```

### Problème : "Fichiers non trouvés dans S3"

**Solution :**
Vérifier la structure S3 et les préfixes dans `.env` :
```bash
S3_RAW_PREFIX=raw  # Doit correspondre à la structure dans S3
```

---

## 📞 Pour plus d'infos

- Architecture complète : `ARCHITECTURE_AWS.md`
- Déploiement EC2 : `DEPLOIEMENT_EC2_AWS.md`
- Comparaison Local/AWS : `COMPARAISON_LOCAL_AWS.md`

**Votre projet CityFlow Analytics est maintenant 100% cloud-ready ! ☁️🎉**

