# 📦 Configuration MongoDB pour CityFlow Analytics

## Vue d'ensemble

Ce projet utilise une **architecture hybride** pour le stockage des métriques :

- **Développement local** : MongoDB (via MongoDB Compass)
- **Production AWS** : DynamoDB

La migration entre les deux est transparente grâce à une couche d'abstraction.

---

## 🎯 Pourquoi MongoDB en local ?

✅ **Plus simple** : Pas besoin de configurer AWS en local  
✅ **Interface visuelle** : MongoDB Compass pour visualiser les données  
✅ **Plus rapide** : Pas de latence réseau  
✅ **Gratuit** : MongoDB Community Edition  
✅ **Migration facile** : Changer `DATABASE_TYPE=dynamodb` pour passer à AWS

---

## 📥 Installation MongoDB

### Option 1 : MongoDB Community Edition (Recommandé)

#### macOS
```bash
# Installer via Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Démarrer MongoDB
brew services start mongodb-community

# Vérifier que MongoDB fonctionne
mongosh --eval "db.version()"
```

#### Windows
1. Télécharger MongoDB Community : https://www.mongodb.com/try/download/community
2. Installer avec les options par défaut
3. MongoDB démarre automatiquement comme service Windows

#### Linux (Ubuntu/Debian)
```bash
# Importer la clé GPG
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Ajouter le dépôt
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Installer
sudo apt-get update
sudo apt-get install -y mongodb-org

# Démarrer
sudo systemctl start mongod
sudo systemctl enable mongod
```

---

## 🖥️ MongoDB Compass (Interface Graphique)

### Installation

1. Télécharger : https://www.mongodb.com/try/download/compass
2. Installer et lancer MongoDB Compass
3. Se connecter à : `mongodb://localhost:27017/`

### Visualiser les données CityFlow

Une fois connecté :
1. Cliquer sur la base de données **`cityflow`**
2. Collections disponibles :
   - **`metrics`** : Métriques des processeurs (bikes, traffic, weather, etc.)
   - **`reports`** : Rapports quotidiens générés

### Requêtes utiles dans Compass

#### Voir toutes les métriques d'une date
```javascript
{
  "date": "2025-11-03"
}
```

#### Voir les métriques d'un type spécifique
```javascript
{
  "metric_type": "bikes",
  "date": "2025-11-03"
}
```

#### Voir le dernier rapport généré
```javascript
// Trier par date décroissante
{
  "date": {"$exists": true}
}
// Sort: { "date": -1 }
// Limit: 1
```

---

## ⚙️ Configuration dans CityFlow

### Fichier `.env`

```bash
# Type de base de données
DATABASE_TYPE=mongodb

# URL MongoDB (par défaut: local)
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=cityflow
```

### Installer les dépendances Python

```bash
pip install pymongo
```

Ou via requirements.txt :
```bash
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### 1. Traiter les données (sauvegarde dans MongoDB)

```bash
python3 processors/main.py
```

**Sortie attendue :**
```
============================================================
📦 Base de données: MongoDB (développement local)
============================================================
✓ Connecté à MongoDB: mongodb://localhost:27017/ / cityflow
...
✓ Métriques bikes exportées vers MONGODB
  ✓ Nouvelles métriques bikes insérées (ID: ...)
```

### 2. Générer le rapport (lecture depuis MongoDB)

```bash
python3 report_generator/main.py
```

**Sortie attendue :**
```
============================================================
📦 Base de données: MongoDB (développement local)
============================================================
✓ Connecté à MongoDB: mongodb://localhost:27017/ / cityflow
...
✓ Métriques bikes chargées depuis MONGODB
✓ Rapport JSON exporté vers MONGODB
```

---

## 🔄 Migration vers DynamoDB (Production)

Quand vous êtes prêt à déployer sur AWS :

### 1. Modifier `.env`

```bash
# Changer de MongoDB à DynamoDB
DATABASE_TYPE=dynamodb

# Configurer AWS
AWS_REGION=us-east-1
DYNAMODB_METRICS_TABLE=cityflow-metrics
DYNAMODB_REPORTS_TABLE=cityflow-daily-reports
```

### 2. Configurer AWS CLI

```bash
aws configure
# AWS Access Key ID: [votre clé]
# AWS Secret Access Key: [votre secret]
# Default region name: us-east-1
```

### 3. Exécuter normalement

```bash
python3 processors/main.py
```

**Le code bascule automatiquement vers DynamoDB !**

---

## 🐛 Dépannage

### Erreur : "Connection refused"

**Problème** : MongoDB n'est pas démarré

**Solution macOS** :
```bash
brew services start mongodb-community
```

**Solution Linux** :
```bash
sudo systemctl start mongod
```

**Solution Windows** : Démarrer le service "MongoDB" dans les Services Windows

---

### Erreur : "pymongo non disponible"

**Problème** : Librairie pymongo non installée

**Solution** :
```bash
pip install pymongo
```

---

### MongoDB Compass ne se connecte pas

**Vérifier que MongoDB fonctionne** :
```bash
mongosh --eval "db.version()"
```

**Si erreur**, redémarrer MongoDB :
```bash
# macOS
brew services restart mongodb-community

# Linux
sudo systemctl restart mongod
```

---

## 📊 Structure des données dans MongoDB

### Collection `metrics`

```javascript
{
  "_id": ObjectId("..."),
  "metric_type": "bikes",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T14:30:00",
  "metrics": {
    // Métriques calculées
    "total_passages": 15234,
    "moyenne_passages_par_compteur": 127.8,
    // ...
  },
  "created_at": ISODate("2025-11-03T14:30:00Z"),
  "updated_at": ISODate("2025-11-03T14:30:00Z")
}
```

### Collection `reports`

```javascript
{
  "_id": ObjectId("..."),
  "report_id": "daily_report_2025-11-03",
  "date": "2025-11-03",
  "timestamp": "2025-11-03T14:35:00",
  "report": {
    "date": "2025-11-03",
    "summary": {
      "total_vehicules_paris": 1234567,
      // ...
    },
    "top_10_troncons_frequentes": [...],
    // ...
  },
  "created_at": ISODate("2025-11-03T14:35:00Z"),
  "updated_at": ISODate("2025-11-03T14:35:00Z")
}
```

---

## 🎓 Résumé

| Aspect | MongoDB (local) | DynamoDB (AWS) |
|--------|-----------------|----------------|
| **Installation** | Manuelle | Managé AWS |
| **Configuration** | `DATABASE_TYPE=mongodb` | `DATABASE_TYPE=dynamodb` |
| **Interface** | MongoDB Compass | AWS Console |
| **Coût** | Gratuit | Pay-per-use |
| **Performance** | Local (rapide) | Réseau AWS |
| **Production** | Non recommandé | Recommandé |

**Conseil** : Développez en local avec MongoDB, déployez en production avec DynamoDB ! 🚀

