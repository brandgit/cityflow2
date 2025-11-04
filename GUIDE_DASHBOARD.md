# 📊 Guide du Dashboard CityFlow Analytics

## 🚀 Lancement

```bash
streamlit run dashboard/app.py
```

Accès : **http://localhost:8501**

---

## 📋 Pages Disponibles

### 🏠 Vue d'ensemble

**Indicateurs clés :**
- 🚴 **Compteurs Vélo** : Nombre de compteurs actifs + total passages
- 🚇 **Perturbations RATP** : Nombre de perturbations actives/totales
- 🚗 **Tronçons** : Nombre de tronçons surveillés + débit total
- 🚧 **Chantiers** : Nombre de chantiers actifs

**Graphiques :**
- Perturbations RATP par sévérité (camembert)
- État du trafic routier (jauge ou camembert)

**Statistiques détaillées :**
- Onglet Vélos : Répartition par arrondissement + Top 5
- Onglet RATP : Lignes impactées + Alertes
- Onglet Trafic : Top tronçons + Alertes congestion

---

### 🚴 Vélos

**Métriques :**
- Nombre de compteurs actifs
- Total de passages journaliers
- Moyenne horaire
- Anomalies détectées

**Visualisations :**
- **Graphique en barres** : Top 10 compteurs les plus fréquentés
- **Tableau détaillé** : Liste complète avec arrondissement
- **Treemap** : Répartition des passages par arrondissement

**Interactions :**
- Cliquer sur les barres pour voir les détails
- Expander pour voir le tableau complet
- Survol pour voir les valeurs exactes

---

### 🚇 RATP

**Métriques :**
- Total de perturbations
- Perturbations actives
- Indice de fiabilité (%)

**Visualisations :**
- **Camembert** : Perturbations par sévérité (Critique, Élevée, Moyenne, Faible)
- **Graphique en barres** : Top 10 lignes les plus impactées (1-14)

**Alertes critiques :**
- Liste des 10 alertes les plus importantes
- Détails : durée, priorité, lignes impactées
- Format : Expanders cliquables

---

### 🚗 Trafic Routier

**Métriques :**
- Tronçons actifs
- Débit total journalier
- Taux d'occupation moyen
- Temps perdu total (en heures)

**Visualisations :**
- **Tableau** : Top 10 tronçons par débit avec zone, taux d'occupation, état
- **Expanders** : Top 5 zones les plus congestionnées avec détails complets
- **Graphique en barres** : Top 10 zones par affluence

**Alertes de congestion :**
- Zones avec congestion détectée
- Temps perdu par zone
- État du trafic dominant

---

### 🚧 Chantiers

**Métriques :**
- Nombre de chantiers actifs
- Surface totale impactée (m²)

**Visualisations :**
- **Graphique en barres** : Impact cumulé par arrondissement (top 10)
- **Tableau** : Zones critiques (>3 chantiers simultanés)

**Informations :**
- Répartition géographique
- Niveau d'impact par zone

---

## 🎨 Fonctionnalités

### 📅 Sélection de date

Dans la barre latérale, utilisez le sélecteur de date pour changer la date analysée.

**Note :** Seules les dates avec des données traitées sont disponibles.

### 🔄 Rafraîchissement automatique

Streamlit met en cache les données avec `@st.cache_data` :
- Les données sont rechargées uniquement si la date change
- Pour forcer le rechargement : appuyez sur **C** puis **Entrée**

### 📊 Interactions avec les graphiques

Les graphiques Plotly sont interactifs :
- **Zoom** : Cliquer-glisser sur le graphique
- **Survol** : Affiche les valeurs exactes
- **Téléchargement** : Icône caméra en haut à droite
- **Réinitialiser** : Double-clic sur le graphique

---

## 📈 Données Affichées

### Vélos (95 compteurs)
- Passages journaliers par compteur
- Moyennes horaires
- Pics de fréquentation
- Répartition géographique

### RATP (94 perturbations)
- Perturbations actives (86)
- Sévérité : Critique (6), Élevée (58), Faible (30)
- Lignes impactées : 1-14
- Durée des perturbations

### Trafic Routier
- Tronçons surveillés
- Débit : millions de véhicules
- Taux d'occupation : 0-100%
- Temps perdu : en heures
- Zones de congestion

### Chantiers
- Chantiers actifs
- Impact par arrondissement
- Zones critiques (>3 chantiers)
- Surface impactée

---

## 🎯 Cas d'usage

### 1. Analyser la mobilité vélo
1. Aller sur la page **Vélos**
2. Consulter le **treemap** pour voir les arrondissements les plus actifs
3. Identifier les **compteurs les plus fréquentés**

### 2. Suivre les perturbations RATP
1. Aller sur la page **RATP**
2. Consulter le **camembert** des sévérités
3. Voir les **lignes les plus impactées**
4. Lire les **alertes critiques**

### 3. Identifier les zones de congestion
1. Aller sur la page **Trafic Routier**
2. Consulter le **tableau des top tronçons**
3. Ouvrir les **expanders** des zones congestionnées
4. Analyser le **graphique par zones**

### 4. Localiser les travaux
1. Aller sur la page **Chantiers**
2. Voir le **graphique par arrondissement**
3. Consulter les **zones critiques**

---

## 🔧 Dépannage

### Dashboard vide ou zéros partout

**Cause :** Données non traitées pour la date sélectionnée

**Solution :**
```bash
# Traiter les données d'abord
python3 main.py 2025-11-04

# Puis lancer le dashboard
streamlit run dashboard/app.py
```

### Erreur "ModuleNotFoundError"

**Solution :** Les anciennes pages ont été déplacées dans `pages_backup/`. Utilisez le nouveau `app.py`.

### Graphiques ne s'affichent pas

**Solution :** Vérifier que Plotly est installé :
```bash
pip install plotly
```

### Cache problématique

**Solution :** Effacer le cache dans Streamlit :
- Appuyer sur **C** dans le dashboard
- Ou relancer avec : `streamlit run dashboard/app.py --server.runOnSave true`

---

## 💡 Conseils

1. **Utilisez les expanders** pour voir plus de détails sans encombrer l'écran
2. **Survolez les graphiques** pour voir les valeurs exactes
3. **Téléchargez les graphiques** avec l'icône caméra (utile pour rapports)
4. **Changez de date** pour comparer les données sur plusieurs jours

---

## 🚀 Améliorations futures possibles

- 📍 Cartes interactives avec Folium/Pydeck
- 📅 Comparaison multi-dates
- 📊 Graphiques d'évolution temporelle
- 🔔 Alertes en temps réel
- 📥 Export PDF des rapports
- 🎨 Mode sombre

---

**Dashboard opérationnel !** Relancez avec `streamlit run dashboard/app.py` 🎉

