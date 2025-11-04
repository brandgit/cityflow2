# 📊 Commandes Dashboard Streamlit

## 🚀 Lancement du Dashboard

### Option 1 : Depuis le répertoire racine

```bash
# Lancer le dashboard Streamlit
streamlit run dashboard/app.py
```

### Option 2 : Depuis le répertoire dashboard

```bash
# Se placer dans le répertoire dashboard
cd dashboard

# Lancer le dashboard
streamlit run app.py
```

Le dashboard sera accessible à : **http://localhost:8501**

---

## 📋 Installation des dépendances

### Installation complète

```bash
# Installer toutes les dépendances (incluant Streamlit)
pip install -r requirements.txt
```

### Installation manuelle des dépendances Streamlit

```bash
# Installer uniquement les dépendances du dashboard
pip install streamlit plotly pandas
```

---

## 🎯 Utilisation

### 1. Préparer les données

Avant de lancer le dashboard, assurez-vous d'avoir des données à visualiser :

```bash
# Traiter les données pour aujourd'hui
python3 main.py

# Ou pour une date spécifique
python3 main.py 2025-11-03
```

### 2. Lancer le dashboard

```bash
streamlit run dashboard/app.py
```

### 3. Naviguer dans le dashboard

- **Sélectionner une date** dans la barre latérale
- **Choisir une source de données** :
  - MongoDB Local (par défaut)
  - Fichiers JSON
  - API
- **Explorer les pages** :
  - 🏠 Vue d'ensemble
  - 🚴 Vélos Vélib'
  - 🚗 Trafic Routier
  - 🚧 Chantiers
  - 🌤️ Météo
  - 🚇 Perturbations RATP
  - 📈 Rapport Quotidien

---

## ⚙️ Configuration

### Sources de données

#### MongoDB Local (recommandé)

```bash
# Démarrer MongoDB
brew services start mongodb-community
# ou
sudo systemctl start mongod

# Lancer le dashboard
streamlit run dashboard/app.py
```

Le dashboard se connecte automatiquement à MongoDB si disponible.

#### Fichiers JSON

Pas besoin de MongoDB, le dashboard charge directement depuis `output/metrics/*.json`.

Dans le dashboard, sélectionner **"Fichiers JSON"** dans la barre latérale.

#### API

```bash
# Terminal 1 : Lancer l'API
python3 api/local_server.py

# Terminal 2 : Lancer le dashboard
streamlit run dashboard/app.py
```

Dans le dashboard, sélectionner **"API"** dans la barre latérale.

---

## 🎨 Personnalisation

### Modifier le port du dashboard

```bash
# Lancer sur un port personnalisé (ex: 8502)
streamlit run dashboard/app.py --server.port 8502
```

### Mode développement (rechargement automatique)

```bash
# Lancer en mode développement
streamlit run dashboard/app.py --server.runOnSave true
```

### Configuration avancée

Créer un fichier `.streamlit/config.toml` :

```toml
[server]
port = 8501
enableCORS = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

---

## 🔧 Dépannage

### Erreur : "ModuleNotFoundError: No module named 'streamlit'"

```bash
# Installer Streamlit
pip install streamlit

# Vérifier l'installation
streamlit --version
```

### Erreur : "No data available"

1. Vérifier que les données ont été traitées :
   ```bash
   python3 main.py
   ```

2. Vérifier que les fichiers existent :
   ```bash
   ls output/metrics/
   ```

3. Essayer une autre source de données (Fichiers JSON au lieu de MongoDB)

### Le dashboard est lent

1. **Utiliser les fichiers JSON** au lieu de MongoDB pour de meilleures performances
2. **Réduire la quantité de données** affichées
3. **Utiliser l'API** qui met en cache les données

### Erreur MongoDB

Si MongoDB n'est pas disponible, le dashboard bascule automatiquement vers les fichiers JSON.

---

## 📊 Workflow complet

### Scénario 1 : Analyse quotidienne

```bash
# 1. Traiter les données du jour
python3 main.py

# 2. Lancer le dashboard
streamlit run dashboard/app.py

# 3. Ouvrir http://localhost:8501 dans le navigateur
```

### Scénario 2 : Analyse historique

```bash
# 1. Traiter les données pour plusieurs dates
python3 main.py 2025-11-01
python3 main.py 2025-11-02
python3 main.py 2025-11-03

# 2. Lancer le dashboard
streamlit run dashboard/app.py

# 3. Sélectionner les dates dans le dashboard
```

### Scénario 3 : Dashboard avec API

```bash
# Terminal 1 : Lancer l'API
python3 api/local_server.py

# Terminal 2 : Lancer le dashboard
streamlit run dashboard/app.py

# Terminal 3 : Traiter les données
python3 main.py
```

---

## 🚀 Commandes rapides

```bash
# Traiter les données et lancer le dashboard
python3 main.py && streamlit run dashboard/app.py

# Lancer tous les services (API + Dashboard)
# Terminal 1
python3 api/local_server.py

# Terminal 2
streamlit run dashboard/app.py
```

---

## 📈 Fonctionnalités disponibles

### Vue d'ensemble (🏠)
- KPIs principaux de toutes les sources
- Graphiques de synthèse
- Top alertes

### Vélos Vélib' (🚴)
- Distribution des vélos (mécaniques/électriques)
- Top stations utilisées
- Alertes stations saturées/vides
- Taux de disponibilité

### Trafic Routier (🚗)
- État du trafic en temps réel
- Top tronçons fréquentés/congestionnés
- Alertes de congestion
- Analyse par zones géographiques
- Jauge de congestion

### Chantiers (🚧)
- Chantiers actifs
- Répartition par arrondissement
- Impact sur la circulation
- Top chantiers les plus impactants

### Météo (🌤️)
- Conditions météorologiques
- Impact sur la mobilité

### Perturbations RATP (🚇)
- Perturbations actives
- Lignes de métro impactées (1-14)
- Alertes critiques
- Répartition par sévérité

### Rapport Quotidien (📈)
- Synthèse complète de la journée
- Analyses détaillées par source
- Alertes et recommandations

---

## 💡 Astuces

### 1. Utiliser les raccourcis clavier

- `R` : Recharger le dashboard
- `C` : Effacer le cache
- `M` : Afficher/masquer la barre latérale

### 2. Partager un lien

Streamlit génère automatiquement des liens partageables :

```
http://localhost:8501/?date=2025-11-03
```

### 3. Exporter les graphiques

Cliquer sur l'icône de caméra dans les graphiques Plotly pour télécharger au format PNG.

### 4. Comparaison de dates

Ouvrir plusieurs onglets du navigateur avec différentes dates pour comparer.

---

## 🎯 Cas d'usage

### Analyse de performance du réseau Vélib'

1. Lancer le dashboard
2. Aller sur la page **Vélos Vélib'**
3. Observer les taux de disponibilité
4. Identifier les stations problématiques

### Identification des zones de congestion

1. Aller sur la page **Trafic Routier**
2. Consulter la carte de congestion
3. Analyser les top 10 tronçons congestionnés
4. Vérifier les alertes

### Suivi des perturbations RATP

1. Aller sur la page **Perturbations RATP**
2. Consulter les lignes impactées
3. Analyser les alertes critiques
4. Vérifier l'indice de fiabilité

---

## 📝 Notes

- Le dashboard se met à jour automatiquement si vous modifiez les fichiers
- Les données sont mises en cache pour de meilleures performances
- Le dashboard fonctionne hors ligne avec les fichiers JSON

---

**CityFlow Analytics Dashboard** © 2025 | Visualisations interactives pour données urbaines

