# ⚡ Déploiement Rapide EC2 - Guide Express

## 🚀 Déploiement en 10 minutes

### 1. Créer l'instance EC2 (5 min)

```bash
# Via console AWS ou CLI
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name ma-cle-ssh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=CityFlow}]'
```

**Configuration minimale :**
- Type : `t3.medium`
- Stockage : 30 GB
- Sécurité : SSH (22) + HTTP (80) + Custom (5001, 8501)

### 2. Connexion et setup (2 min)

```bash
# Se connecter
ssh -i ~/.ssh/ma-cle-ssh.pem ubuntu@VOTRE_IP_EC2

# Mise à jour
sudo apt update && sudo apt upgrade -y

# Installer Python et Git
sudo apt install python3.10 python3.10-venv python3-pip git -y
```

### 3. Déployer le code (2 min)

```bash
# Cloner le projet
git clone https://github.com/votre-repo/cityflow.git
cd cityflow

# Créer venv et installer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configuration AWS (3 min)

#### Créer les ressources AWS

```bash
# DynamoDB
aws dynamodb create-table \
    --table-name cityflow-metrics \
    --attribute-definitions AttributeName=metric_type,AttributeType=S AttributeName=date,AttributeType=S \
    --key-schema AttributeName=metric_type,KeyType=HASH AttributeName=date,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region eu-west-3

# S3
aws s3 mb s3://cityflow-reports-$(date +%s) --region eu-west-3
```

#### Configurer .env

```bash
cat > .env << 'EOF'
AWS_EXECUTION_ENV=AWS_EC2
AWS_REGION=eu-west-3
DATABASE_TYPE=dynamodb
USE_DYNAMODB=true
USE_S3=true
DYNAMODB_TABLE_METRICS=cityflow-metrics
DYNAMODB_TABLE_REPORTS=cityflow-reports
S3_BUCKET_REPORTS=cityflow-reports-XXXXX
EOF
```

### 5. Lancer les services (1 min)

```bash
# Test
python3 main.py

# Lancer API (background)
nohup python3 api/local_server.py > logs/api.log 2>&1 &

# Lancer Dashboard (background)
nohup streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > logs/dashboard.log 2>&1 &
```

### 6. Accéder au dashboard

```
http://VOTRE_IP_EC2:8501
```

---

## 🔄 Automatisation rapide (cron)

```bash
# Éditer crontab
crontab -e

# Ajouter (traitement quotidien à 2h)
0 2 * * * cd /home/ubuntu/cityflow && /home/ubuntu/cityflow/venv/bin/python3 main.py >> /home/ubuntu/cityflow/logs/cron.log 2>&1
```

---

## ✅ Vérifications rapides

```bash
# 1. DynamoDB
aws dynamodb scan --table-name cityflow-metrics --max-items 1

# 2. S3
aws s3 ls s3://votre-bucket/

# 3. Services actifs
ps aux | grep python

# 4. Logs
tail -f logs/*.log
```

---

## 🆘 Dépannage rapide

### API ne répond pas
```bash
kill $(ps aux | grep 'api/local_server.py' | awk '{print $2}')
nohup python3 api/local_server.py > logs/api.log 2>&1 &
```

### Dashboard ne charge pas
```bash
kill $(ps aux | grep 'streamlit' | awk '{print $2}')
nohup streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > logs/dashboard.log 2>&1 &
```

### Permissions DynamoDB
```bash
# Attacher le rôle IAM via console AWS
# EC2 → Instance → Actions → Security → Modify IAM role
```

---

## 📦 Un seul script pour tout déployer

Créer `quick_deploy.sh` :

```bash
#!/bin/bash
set -e

echo "🚀 Déploiement rapide CityFlow..."

# Setup
sudo apt update && sudo apt install python3.10 python3.10-venv git -y
git clone https://github.com/votre-repo/cityflow.git
cd cityflow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cat > .env << 'EOF'
AWS_EXECUTION_ENV=AWS_EC2
DATABASE_TYPE=dynamodb
USE_DYNAMODB=true
USE_S3=true
AWS_REGION=eu-west-3
EOF

# Créer répertoires
mkdir -p logs data/raw output

# Lancer services
nohup python3 api/local_server.py > logs/api.log 2>&1 &
nohup streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > logs/dashboard.log 2>&1 &

echo "✅ Déploiement terminé !"
echo "📊 Dashboard: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
```

**Utiliser :**
```bash
chmod +x quick_deploy.sh
./quick_deploy.sh
```

---

**Déploiement EC2 en 10 minutes chrono !** ⚡

