# 🚀 Déploiement CityFlow Analytics sur EC2 AWS

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Création de l'instance EC2](#création-de-linstance-ec2)
3. [Configuration initiale](#configuration-initiale)
4. [Installation des dépendances](#installation-des-dépendances)
5. [Configuration AWS (DynamoDB, S3)](#configuration-aws)
6. [Déploiement du code](#déploiement-du-code)
7. [Configuration de l'environnement](#configuration-de-lenvironnement)
8. [Automatisation](#automatisation)
9. [Monitoring et logs](#monitoring-et-logs)
10. [Sécurité](#sécurité)

---

## 1. Prérequis

### Sur votre machine locale

- [x] Compte AWS actif
- [x] AWS CLI installé et configuré
- [x] Clé SSH pour se connecter à EC2
- [x] Code CityFlow prêt à déployer

### Services AWS nécessaires

- [x] **EC2** : Instance pour exécuter le code
- [x] **S3** : Stockage des fichiers CSV et données brutes
- [x] **DynamoDB** : Base de données NoSQL pour métriques
- [x] **IAM** : Rôles et permissions
- [x] **CloudWatch** (optionnel) : Monitoring et logs

---

## 2. Création de l'instance EC2

### Étape 1 : Connexion à AWS Console

1. Aller sur https://console.aws.amazon.com
2. Se connecter avec vos identifiants
3. Sélectionner la région (ex: `eu-west-3` pour Paris)

### Étape 2 : Lancer une instance EC2

```bash
# Via AWS CLI (optionnel)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name ma-cle-ssh \
    --security-group-ids sg-xxxxx \
    --subnet-id subnet-xxxxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=CityFlow-Analytics}]'
```

**Ou via la console web :**

1. **Services** → **EC2** → **Launch Instance**
2. **Nom** : `CityFlow-Analytics`
3. **AMI** : `Ubuntu Server 22.04 LTS` (ou Amazon Linux 2023)
4. **Type d'instance** : 
   - `t3.medium` (2 vCPU, 4 GB RAM) - minimum recommandé
   - `t3.large` (2 vCPU, 8 GB RAM) - pour gros fichiers
   - `t3.xlarge` (4 vCPU, 16 GB RAM) - pour traitement rapide
5. **Paire de clés** : Créer ou sélectionner une clé SSH
6. **Réseau** : VPC par défaut
7. **Stockage** : 
   - Minimum : **30 GB** (SSD gp3)
   - Recommandé : **50-100 GB** (pour données + logs)
8. **Groupe de sécurité** :
   - SSH (port 22) : Votre IP uniquement
   - HTTP (port 80) : Optionnel pour API
   - HTTPS (port 443) : Optionnel pour API
   - Custom TCP (port 5001) : Pour API (si besoin d'accès externe)
   - Custom TCP (port 8501) : Pour dashboard Streamlit (si besoin d'accès externe)

9. **Lancer l'instance**

### Étape 3 : Récupérer l'IP publique

```bash
# Via AWS CLI
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=CityFlow-Analytics" \
    --query "Reservations[*].Instances[*].[PublicIpAddress]" \
    --output text
```

Notez l'adresse IP : `3.XX.XXX.XXX`

---

## 3. Configuration initiale

### Connexion SSH

```bash
# Se connecter à l'instance
ssh -i ~/.ssh/ma-cle-ssh.pem ubuntu@3.XX.XXX.XXX

# Si erreur de permissions
chmod 400 ~/.ssh/ma-cle-ssh.pem
ssh -i ~/.ssh/ma-cle-ssh.pem ubuntu@3.XX.XXX.XXX
```

### Mise à jour du système

```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# Amazon Linux
sudo yum update -y
```

---

## 4. Installation des dépendances

### Python 3.10+

```bash
# Ubuntu
sudo apt install python3.10 python3.10-venv python3-pip -y

# Amazon Linux
sudo yum install python3.10 python3-pip -y
```

### Git

```bash
# Ubuntu
sudo apt install git -y

# Amazon Linux
sudo yum install git -y
```

### Autres outils utiles

```bash
# Installer des outils de monitoring
sudo apt install htop -y  # Monitoring CPU/RAM
sudo apt install ncdu -y  # Analyse d'espace disque
```

---

## 5. Configuration AWS

### Créer un rôle IAM pour EC2

1. **IAM** → **Roles** → **Create Role**
2. **Type** : `AWS Service` → `EC2`
3. **Permissions** :
   - `AmazonDynamoDBFullAccess` (pour DynamoDB)
   - `AmazonS3FullAccess` (pour S3)
   - `CloudWatchLogsFullAccess` (pour logs)
4. **Nom** : `CityFlow-EC2-Role`
5. **Créer**

### Attacher le rôle à l'instance EC2

```bash
# Via AWS CLI
aws ec2 associate-iam-instance-profile \
    --instance-id i-xxxxx \
    --iam-instance-profile Name=CityFlow-EC2-Role
```

**Ou via console :**
- EC2 → Instance → **Actions** → **Security** → **Modify IAM role**
- Sélectionner `CityFlow-EC2-Role`

### Créer les ressources AWS

#### Table DynamoDB

```bash
# Créer la table pour les métriques
aws dynamodb create-table \
    --table-name cityflow-metrics \
    --attribute-definitions \
        AttributeName=metric_type,AttributeType=S \
        AttributeName=date,AttributeType=S \
    --key-schema \
        AttributeName=metric_type,KeyType=HASH \
        AttributeName=date,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region eu-west-3

# Créer la table pour les rapports
aws dynamodb create-table \
    --table-name cityflow-reports \
    --attribute-definitions \
        AttributeName=date,AttributeType=S \
    --key-schema \
        AttributeName=date,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region eu-west-3
```

#### Bucket S3

```bash
# Créer le bucket pour les rapports CSV
aws s3 mb s3://cityflow-reports-paris --region eu-west-3

# Créer le bucket pour les données brutes (si nécessaire)
aws s3 mb s3://cityflow-raw-data-paris --region eu-west-3
```

---

## 6. Déploiement du code

### Option 1 : Cloner depuis Git (recommandé)

```bash
# Sur l'instance EC2
cd ~
git clone https://github.com/votre-username/cityflow.git
cd cityflow
```

### Option 2 : Transférer depuis local

```bash
# Depuis votre machine locale
scp -i ~/.ssh/ma-cle-ssh.pem -r /path/to/cityflow ubuntu@3.XX.XXX.XXX:~/
```

### Créer l'environnement virtuel

```bash
cd ~/cityflow

# Créer venv
python3 -m venv venv

# Activer venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## 7. Configuration de l'environnement

### Créer le fichier .env

```bash
cd ~/cityflow
nano .env
```

**Contenu du .env pour AWS :**

```bash
# === ENVIRONNEMENT ===
AWS_EXECUTION_ENV=AWS_EC2
AWS_REGION=eu-west-3

# === BASE DE DONNÉES ===
DATABASE_TYPE=dynamodb
USE_DYNAMODB=true

# Tables DynamoDB
DYNAMODB_TABLE_METRICS=cityflow-metrics
DYNAMODB_TABLE_REPORTS=cityflow-reports

# === S3 ===
USE_S3=true
S3_BUCKET_REPORTS=cityflow-reports-paris
S3_BUCKET_RAW=cityflow-raw-data-paris

# === CHEMINS DONNÉES (sur EC2) ===
DATA_DIR_RAW=/home/ubuntu/cityflow/data/raw
DATA_DIR_PROCESSED=/home/ubuntu/cityflow/data/processed
OUTPUT_DIR=/home/ubuntu/cityflow/output

# === API ===
API_PORT=5001

# === CHUNKING (pour gros fichiers) ===
# Force le mode EC2 pour découper en chunks
USE_EC2_MODE=true
MAX_FILE_SIZE_MB=500
EC2_CHUNK_SIZE=50000
```

**Sauvegarder :** `Ctrl+O`, `Entrée`, `Ctrl+X`

### Créer les répertoires

```bash
mkdir -p ~/cityflow/data/raw
mkdir -p ~/cityflow/data/processed
mkdir -p ~/cityflow/output/metrics
mkdir -p ~/cityflow/output/reports
mkdir -p ~/cityflow/logs
```

---

## 8. Upload des données brutes

### Option 1 : Depuis S3 vers EC2

```bash
# Télécharger les données depuis S3
aws s3 sync s3://votre-bucket-source/raw/ ~/cityflow/data/raw/

# Ou copier vos fichiers CSV
aws s3 cp s3://votre-bucket/comptages.csv ~/cityflow/data/raw/
```

### Option 2 : Depuis votre machine locale

```bash
# Depuis votre machine
scp -i ~/.ssh/ma-cle-ssh.pem \
    /path/to/local/data/*.csv \
    ubuntu@3.XX.XXX.XXX:~/cityflow/data/raw/
```

### Option 3 : Téléchargement direct (Open Data Paris)

```bash
# Sur l'instance EC2
cd ~/cityflow/data/raw

# Exemple : Télécharger les comptages routiers
wget "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/exports/csv" \
    -O comptages-routiers-permanents.csv
```

---

## 9. Tester le déploiement

### Test 1 : Vérifier la configuration

```bash
cd ~/cityflow
source venv/bin/activate

# Tester la connexion DynamoDB
python3 test_database_connection.py
```

**Résultat attendu :**
```
✅ Connexion DynamoDB réussie
```

### Test 2 : Lancer le traitement

```bash
# Traiter les données
python3 main.py

# Ou pour une date spécifique
python3 main.py 2025-11-04
```

### Test 3 : Vérifier DynamoDB

```bash
# Lister les éléments de la table
aws dynamodb scan \
    --table-name cityflow-metrics \
    --max-items 5 \
    --region eu-west-3
```

### Test 4 : Vérifier S3

```bash
# Lister les rapports uploadés
aws s3 ls s3://cityflow-reports-paris/
```

---

## 10. Automatisation

### Option 1 : Cron Job (Traitement quotidien)

```bash
# Éditer le crontab
crontab -e
```

**Ajouter :**

```bash
# Traiter les données tous les jours à 2h du matin
0 2 * * * cd /home/ubuntu/cityflow && /home/ubuntu/cityflow/venv/bin/python3 main.py >> /home/ubuntu/cityflow/logs/cron.log 2>&1

# Ou avec date dynamique
0 2 * * * cd /home/ubuntu/cityflow && /home/ubuntu/cityflow/venv/bin/python3 main.py $(date +\%Y-\%m-\%d) >> /home/ubuntu/cityflow/logs/cron_$(date +\%Y\%m\%d).log 2>&1
```

### Option 2 : Service systemd (Recommandé pour API)

#### Service pour l'API

```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/cityflow-api.service
```

**Contenu :**

```ini
[Unit]
Description=CityFlow Analytics API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cityflow
Environment="PATH=/home/ubuntu/cityflow/venv/bin"
ExecStart=/home/ubuntu/cityflow/venv/bin/python3 api/local_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Activer et démarrer :**

```bash
sudo systemctl daemon-reload
sudo systemctl enable cityflow-api
sudo systemctl start cityflow-api
sudo systemctl status cityflow-api
```

#### Service pour le Dashboard Streamlit

```bash
sudo nano /etc/systemd/system/cityflow-dashboard.service
```

**Contenu :**

```ini
[Unit]
Description=CityFlow Analytics Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cityflow
Environment="PATH=/home/ubuntu/cityflow/venv/bin"
ExecStart=/home/ubuntu/cityflow/venv/bin/streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Activer :**

```bash
sudo systemctl daemon-reload
sudo systemctl enable cityflow-dashboard
sudo systemctl start cityflow-dashboard
sudo systemctl status cityflow-dashboard
```

#### Service pour le traitement quotidien (Timer systemd)

```bash
# Créer le service
sudo nano /etc/systemd/system/cityflow-processor.service
```

**Contenu :**

```ini
[Unit]
Description=CityFlow Analytics Data Processor
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/cityflow
Environment="PATH=/home/ubuntu/cityflow/venv/bin"
ExecStart=/home/ubuntu/cityflow/venv/bin/python3 main.py
StandardOutput=append:/home/ubuntu/cityflow/logs/processor.log
StandardError=append:/home/ubuntu/cityflow/logs/processor-error.log
```

**Créer le timer :**

```bash
sudo nano /etc/systemd/system/cityflow-processor.timer
```

**Contenu :**

```ini
[Unit]
Description=CityFlow Analytics Daily Processing Timer
Requires=cityflow-processor.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Activer :**

```bash
sudo systemctl daemon-reload
sudo systemctl enable cityflow-processor.timer
sudo systemctl start cityflow-processor.timer
sudo systemctl list-timers
```

---

## 11. Configuration Nginx (Optionnel - Reverse Proxy)

### Installation

```bash
sudo apt install nginx -y
```

### Configuration

```bash
sudo nano /etc/nginx/sites-available/cityflow
```

**Contenu :**

```nginx
# API
server {
    listen 80;
    server_name api.cityflow.votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Dashboard
server {
    listen 80;
    server_name dashboard.cityflow.votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Activer :**

```bash
sudo ln -s /etc/nginx/sites-available/cityflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 12. Monitoring et Logs

### CloudWatch Logs (Optionnel)

#### Installer l'agent CloudWatch

```bash
# Télécharger
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

# Installer
sudo dpkg -i amazon-cloudwatch-agent.deb
```

#### Configuration

```bash
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/config.json
```

**Contenu :**

```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ubuntu/cityflow/logs/processor.log",
            "log_group_name": "/cityflow/processor",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/home/ubuntu/cityflow/logs/api.log",
            "log_group_name": "/cityflow/api",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

**Démarrer :**

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
    -s
```

### Logs locaux

```bash
# Voir les logs en temps réel
tail -f ~/cityflow/logs/processor.log
tail -f ~/cityflow/logs/api.log

# Voir les logs systemd
sudo journalctl -u cityflow-api -f
sudo journalctl -u cityflow-dashboard -f
```

---

## 13. Sécurité

### Groupe de sécurité EC2

**Règles entrantes (Inbound) :**

| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | Votre IP | Accès SSH sécurisé |
| HTTP | 80 | 0.0.0.0/0 | API publique (si nginx) |
| Custom TCP | 5001 | VPC uniquement | API interne |
| Custom TCP | 8501 | VPC uniquement | Dashboard interne |

**Règles sortantes (Outbound) :**
- Tout le trafic autorisé (par défaut)

### Firewall UFW

```bash
# Activer UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Sécuriser SSH

```bash
# Désactiver connexion par mot de passe
sudo nano /etc/ssh/sshd_config
```

**Modifier :**
```
PasswordAuthentication no
PermitRootLogin no
```

**Redémarrer SSH :**
```bash
sudo systemctl restart sshd
```

---

## 14. Commandes utiles

### Gestion des services

```bash
# API
sudo systemctl start cityflow-api
sudo systemctl stop cityflow-api
sudo systemctl restart cityflow-api
sudo systemctl status cityflow-api

# Dashboard
sudo systemctl start cityflow-dashboard
sudo systemctl stop cityflow-dashboard
sudo systemctl restart cityflow-dashboard

# Traitement
sudo systemctl start cityflow-processor  # Exécution manuelle
```

### Monitoring

```bash
# CPU et RAM
htop

# Espace disque
df -h
ncdu ~/cityflow

# Logs
tail -f ~/cityflow/logs/*.log
sudo journalctl -u cityflow-api -n 100
```

### Mise à jour du code

```bash
cd ~/cityflow
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cityflow-api
sudo systemctl restart cityflow-dashboard
```

---

## 15. Architecture déployée

```
┌─────────────────────────────────────────────────────────┐
│                    Instance EC2                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Services systemd:                               │   │
│  │  - cityflow-api (port 5001)                     │   │
│  │  - cityflow-dashboard (port 8501)               │   │
│  │  - cityflow-processor.timer (cron quotidien)    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Code:                                           │   │
│  │  - processors/  (traitement données)            │   │
│  │  - api/         (exposition REST)               │   │
│  │  - dashboard/   (visualisation Streamlit)       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ IAM Role
                          ↓
        ┌─────────────────────────────────┐
        │     Services AWS                 │
        │                                  │
        │  - DynamoDB (métriques/rapports)│
        │  - S3 (rapports CSV)            │
        │  - CloudWatch (logs)            │
        └─────────────────────────────────┘
```

---

## 16. Checklist de déploiement

### Avant le déploiement

- [ ] Instance EC2 créée et démarrée
- [ ] Rôle IAM créé et attaché
- [ ] Table DynamoDB créée
- [ ] Bucket S3 créé
- [ ] Groupe de sécurité configuré

### Pendant le déploiement

- [ ] Connexion SSH fonctionnelle
- [ ] Python 3.10+ installé
- [ ] Code déployé (git clone ou scp)
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] Fichier .env configuré
- [ ] Répertoires créés

### Après le déploiement

- [ ] Test de connexion DynamoDB OK
- [ ] Test de traitement OK
- [ ] Métriques dans DynamoDB
- [ ] Rapports dans S3
- [ ] API accessible
- [ ] Dashboard accessible
- [ ] Services systemd actifs
- [ ] Logs fonctionnels

---

## 17. Estimation des coûts AWS

### Instance EC2

| Type | Prix/heure | Prix/mois | Usage |
|------|-----------|-----------|-------|
| t3.medium | ~$0.04 | ~$30 | Développement |
| t3.large | ~$0.08 | ~$60 | Production légère |
| t3.xlarge | ~$0.17 | ~$125 | Production intensive |

### DynamoDB

- **Mode On-Demand** : ~$1.25 par million d'écritures
- **Stockage** : ~$0.25 par GB/mois
- **Estimation** : ~$5-10/mois pour usage modéré

### S3

- **Stockage** : ~$0.023 par GB/mois
- **Requêtes** : Négligeable pour usage modéré
- **Estimation** : ~$2-5/mois

### Total estimé

- **Minimum** : ~$40/mois (t3.medium + DynamoDB + S3)
- **Recommandé** : ~$75/mois (t3.large + services)

---

## 18. Dépannage

### Problème : Connexion DynamoDB échoue

```bash
# Vérifier le rôle IAM
aws sts get-caller-identity

# Vérifier les permissions
aws dynamodb list-tables --region eu-west-3
```

### Problème : Données ne s'uploadent pas sur S3

```bash
# Vérifier les permissions S3
aws s3 ls s3://cityflow-reports-paris/

# Tester l'upload manuel
echo "test" > test.txt
aws s3 cp test.txt s3://cityflow-reports-paris/
```

### Problème : Service ne démarre pas

```bash
# Voir les logs détaillés
sudo journalctl -u cityflow-api -n 50
sudo journalctl -u cityflow-dashboard -n 50

# Vérifier la syntaxe du service
sudo systemctl daemon-reload
```

### Problème : Manque de mémoire

```bash
# Vérifier la mémoire
free -h

# Augmenter le swap (temporaire)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 19. Script de déploiement automatique

Créer un script pour automatiser le déploiement :

```bash
nano ~/deploy_cityflow.sh
```

**Contenu :**

```bash
#!/bin/bash

echo "🚀 Déploiement CityFlow Analytics sur EC2"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
PROJECT_DIR=~/cityflow
VENV_DIR=$PROJECT_DIR/venv

# 1. Mise à jour du code
echo "📥 Mise à jour du code..."
cd $PROJECT_DIR
git pull origin main

# 2. Activation venv
echo "🔧 Activation environnement virtuel..."
source $VENV_DIR/bin/activate

# 3. Installation des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt --quiet

# 4. Test de connexion
echo "🔍 Test de connexion AWS..."
python3 test_database_connection.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Connexion AWS OK${NC}"
else
    echo -e "${RED}❌ Erreur de connexion AWS${NC}"
    exit 1
fi

# 5. Redémarrage des services
echo "🔄 Redémarrage des services..."
sudo systemctl restart cityflow-api
sudo systemctl restart cityflow-dashboard

# 6. Vérification
echo "✅ Vérification des services..."
sudo systemctl is-active cityflow-api
sudo systemctl is-active cityflow-dashboard

echo ""
echo "🎉 Déploiement terminé !"
echo "📊 Dashboard: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
echo "🔌 API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5001"
```

**Rendre exécutable :**

```bash
chmod +x ~/deploy_cityflow.sh
```

**Utiliser :**

```bash
~/deploy_cityflow.sh
```

---

## 20. Accès distant

### Via IP publique

```
Dashboard: http://3.XX.XXX.XXX:8501
API: http://3.XX.XXX.XXX:5001
```

⚠️ **Attention :** Nécessite d'ouvrir les ports dans le groupe de sécurité

### Via Nginx + Nom de domaine (Recommandé)

1. Acheter un nom de domaine (ex: Route53)
2. Configurer Nginx (voir section 11)
3. Installer un certificat SSL avec Let's Encrypt :

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d dashboard.votre-domaine.com
```

Accès sécurisé :
```
https://dashboard.votre-domaine.com
https://api.votre-domaine.com
```

---

## 21. Backup et Récupération

### Backup automatique DynamoDB

```bash
# Via AWS CLI (à mettre dans cron)
aws dynamodb create-backup \
    --table-name cityflow-metrics \
    --backup-name cityflow-metrics-backup-$(date +%Y%m%d) \
    --region eu-west-3
```

### Backup S3

```bash
# Activer le versioning
aws s3api put-bucket-versioning \
    --bucket cityflow-reports-paris \
    --versioning-configuration Status=Enabled
```

### Snapshot EC2

```bash
# Créer un snapshot de l'instance
aws ec2 create-snapshot \
    --volume-id vol-xxxxx \
    --description "CityFlow backup $(date +%Y%m%d)"
```

---

## 22. Résumé des commandes essentielles

```bash
# Connexion SSH
ssh -i ~/.ssh/ma-cle-ssh.pem ubuntu@3.XX.XXX.XXX

# Activer venv
cd ~/cityflow && source venv/bin/activate

# Traiter les données
python3 main.py

# Voir les logs
tail -f ~/cityflow/logs/*.log
sudo journalctl -u cityflow-api -f

# Redémarrer les services
sudo systemctl restart cityflow-api
sudo systemctl restart cityflow-dashboard

# Vérifier le statut
sudo systemctl status cityflow-api
sudo systemctl status cityflow-dashboard

# Déployer une mise à jour
~/deploy_cityflow.sh
```

---

## 🎯 Architecture finale

```
Internet
   │
   ↓
[Nginx Reverse Proxy] (Port 80/443)
   │
   ├──→ [Dashboard Streamlit] (Port 8501)
   │    └──→ Lit depuis DynamoDB ou fichiers JSON
   │
   ├──→ [API Flask] (Port 5001)
   │    └──→ Lit depuis DynamoDB
   │
   └──→ [Processor] (Cron quotidien)
        └──→ Traite les données
             └──→ Écrit dans DynamoDB + S3
```

---

## ✅ Déploiement réussi !

Une fois toutes ces étapes complétées, votre projet CityFlow Analytics sera :
- ✅ Déployé sur EC2
- ✅ Automatisé avec cron/systemd
- ✅ Connecté à DynamoDB et S3
- ✅ Accessible via IP publique ou nom de domaine
- ✅ Monitoré avec logs et CloudWatch

**Dashboard accessible 24/7 !** 🎉

