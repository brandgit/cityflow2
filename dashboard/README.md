# 📊 CityFlow Analytics Dashboard

Dashboard interactif Streamlit pour visualiser les métriques et rapports de CityFlow Analytics.

## 🚀 Fonctionnalités

### Pages disponibles

1. **🏠 Vue d'ensemble**
   - KPIs principaux de toutes les sources
   - Graphiques de synthèse
   - Alertes principales

2. **🚴 Vélos Vélib'**
   - Distribution des vélos et places
   - Top stations utilisées
   - Alertes stations saturées/vides

3. **🚗 Trafic Routier**
   - État du trafic en temps réel
   - Top tronçons fréquentés/congestionnés
   - Alertes de congestion
   - Analyse par zones

4. **🚧 Chantiers**
   - Chantiers actifs
   - Répartition par arrondissement
   - Impact sur la circulation

5. **🌤️ Météo**
   - Conditions météorologiques
   - Impact sur la mobilité

6. **🚇 Perturbations RATP**
   - Perturbations actives
   - Lignes impactées
   - Alertes critiques

7. **📈 Rapport Quotidien**
   - Synthèse complète
   - Analyses détaillées
   - Recommandations

## 📋 Prérequis

```bash
# Installer les dépendances
pip install streamlit plotly pandas pymongo flask requests
```

Ou via requirements.txt :

```bash
pip install -r requirements.txt
```

## 🎯 Utilisation

### Lancer le dashboard

```bash
# Depuis le répertoire racine du projet
streamlit run dashboard/app.py
```

Ou :

```bash
# Depuis le répertoire dashboard
cd dashboard
streamlit run app.py
```

Le dashboard sera accessible à l'adresse : **http://localhost:8501**

### Configuration

Le dashboard peut charger les données depuis 3 sources :

1. **MongoDB Local** (par défaut)
   - Nécessite MongoDB en cours d'exécution
   - Configuration dans `.env` : `MONGODB_URL=mongodb://localhost:27017/`

2. **Fichiers JSON**
   - Charge depuis `output/metrics/*.json`
   - Pas besoin de MongoDB

3. **API**
   - Nécessite l'API en cours d'exécution sur le port 5001
   - Lance avec : `python3 api/local_server.py`

### Sélection de la date

Le dashboard permet de sélectionner la date des données à visualiser. Par défaut, il affiche les données du jour.

## 📂 Structure

```
dashboard/
├── __init__.py
├── app.py                      # Application principale
├── README.md                   # Ce fichier
├── pages/                      # Pages du dashboard
│   ├── __init__.py
│   ├── overview.py            # Vue d'ensemble
│   ├── bikes.py               # Page Vélib'
│   ├── traffic_routier.py     # Page Trafic routier
│   ├── chantiers.py           # Page Chantiers
│   ├── weather.py             # Page Météo
│   ├── traffic_ratp.py        # Page Perturbations RATP
│   └── rapport.py             # Page Rapport
└── utils/                      # Utilitaires
    ├── __init__.py
    ├── data_loader.py         # Chargement des données
    └── charts.py              # Graphiques réutilisables
```

## 🎨 Personnalisation

### Thème

Le dashboard utilise un thème personnalisé avec des couleurs cohérentes. Pour modifier le thème, éditez `app.py` :

```python
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;  # Modifier la couleur
    }
</style>
""", unsafe_allow_html=True)
```

### Ajouter une nouvelle page

1. Créer un nouveau fichier dans `dashboard/pages/`
2. Implémenter la fonction `show(date, data_source)`
3. Ajouter l'import dans `dashboard/pages/__init__.py`
4. Ajouter l'option dans la navigation de `app.py`

Exemple :

```python
# dashboard/pages/ma_page.py
import streamlit as st

def show(date: str, data_source: str):
    st.title("Ma Nouvelle Page")
    st.write(f"Date: {date}")
    # ... votre code ...
```

## 📊 Graphiques

Le dashboard utilise **Plotly** pour créer des graphiques interactifs :

- **Graphiques en barres** : Comparaison de valeurs
- **Camemberts** : Répartitions
- **Jauges** : Indicateurs de performance
- **Cartes** : Visualisation géographique (à venir)

## 🔧 Dépannage

### Le dashboard ne démarre pas

```bash
# Vérifier que streamlit est installé
pip install streamlit

# Vérifier la version
streamlit --version
```

### Pas de données affichées

1. Vérifier que les données ont été traitées :
   ```bash
   python3 main.py
   ```

2. Vérifier que les fichiers existent :
   ```bash
   ls output/metrics/
   ```

3. Essayer une autre source de données (Fichiers JSON au lieu de MongoDB)

### Erreurs MongoDB

Si MongoDB n'est pas disponible, le dashboard bascule automatiquement vers les fichiers JSON.

Pour forcer l'utilisation des fichiers JSON, sélectionner **"Fichiers JSON"** dans la barre latérale.

## 🚀 Déploiement

### Déploiement local

Le dashboard est conçu pour fonctionner en local. Il suffit de lancer :

```bash
streamlit run dashboard/app.py
```

### Déploiement Streamlit Cloud

1. Pousser le code sur GitHub
2. Créer un compte sur [streamlit.io](https://streamlit.io/)
3. Connecter le repository
4. Déployer automatiquement

### Configuration pour le déploiement

Créer un fichier `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
enableCORS = false
```

## 📈 Améliorations futures

- [ ] Ajout de cartes interactives (Folium/Pydeck)
- [ ] Comparaison multi-dates
- [ ] Export des graphiques en PDF
- [ ] Alertes en temps réel
- [ ] Prédictions ML
- [ ] Mode sombre
- [ ] Support multi-langues

## 📞 Support

Pour toute question ou problème, consulter la documentation principale du projet dans `README.md`.

---

**CityFlow Analytics Dashboard** © 2025 | Visualisations interactives pour données urbaines

