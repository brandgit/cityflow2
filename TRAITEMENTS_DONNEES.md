# Traitements à Effectuer sur les Données CityFlow Analytics

## Vue d'ensemble des Sources de Données

### Données API (Temps Réel)
1. **API Bikes** - Compteurs vélos (881,878 enregistrements)
2. **API Traffic** - Perturbations trafic RATP (841 disruptions)
3. **API Weather** - Conditions météo Paris

### Données Batch (Historiques)
4. **Comptages Routiers Permanents** - 20M+ lignes (6.2 GB)
5. **Chantiers Perturbants** - 100 chantiers actifs
6. **Référentiel Géographique** - 3,740 tronçons de voies

---

## 1. TRAITEMENTS API BIKES (Compteurs Vélos)

### Structure des Données
```json
{
  "id_compteur": "100007049-101007049",
  "nom_compteur": "28 boulevard Diderot O-E",
  "sum_counts": 25,
  "date": "2025-11-01T22:00:00+00:00",
  "coordinates": {"lon": 2.37559, "lat": 48.84613},
  "mois_annee_comptage": "2025-11"
}
```

### Traitements Spécifiques

#### A. Validation & Nettoyage
- ✅ **Validation des coordonnées GPS** (lon ∈ [-180, 180], lat ∈ [-90, 90])
- ✅ **Détection des compteurs défaillants** (sum_counts = 0 ou null pendant X jours)
- ✅ **Normalisation des noms de compteurs** (uniformisation des formats)
- ✅ **Gestion des doublons** (même id_compteur + date)
- ✅ **Vérification des dates** (dates futures rejetées, dates anciennes archivées)

#### B. Agrégations Quotidiennes
- 📊 **Par compteur** :
  - Total véhicules/jour
  - Moyenne horaire
  - Pic horaire (heure avec le plus de passage)
  - Heures creuses (< 5% du total quotidien)
  
- 📊 **Par zone géographique** (arrondissement) :
  - Total passages/arrondissement/jour
  - Top 10 compteurs par arrondissement
  - Moyenne de passages par compteur/arrondissement
  
- 📊 **Globale** :
  - Total vélos Paris/jour
  - Progression vs semaine précédente (%)
  - Évolution vs même jour année précédente (si données disponibles)

#### C. Calculs d'Indicateurs
- ⚡ **Détection d'anomalies** :
  - Compteurs avec variation > 300% vs moyenne historique
  - Compteurs inactifs > 24h (alerte défaillance)
  
- 📈 **Métriques de performance** :
  - Taux de disponibilité des compteurs (% actifs/jour)
  - Indice de fréquentation cyclable (0-100)
  
- 🎯 **Profils temporels** :
  - Profil "jour type" par jour de semaine (Lundi, Mardi, etc.)
  - Profil "weekend" vs "semaine"
  - Comparaison jour actuel vs jour type (écart normalisé)

#### D. Stockage DynamoDB
```
Partition Key: date (YYYY-MM-DD)
Sort Key: id_compteur
Attributes:
  - total_jour
  - moyenne_horaire
  - pic_horaire
  - arrondissement
  - coordinates
  - anomalie_detectee (bool)
```

---

## 2. TRAITEMENTS API TRAFFIC (Perturbations RATP)

### Structure des Données
```json
{
  "disruptions": [{
    "id": "...",
    "status": "active",
    "severity": {
      "effect": "SIGNIFICANT_DELAYS",
      "priority": 30
    },
    "application_periods": [{
      "begin": "20250828T182100",
      "end": "20251231T230000"
    }],
    "messages": [{"text": "..."}]
  }]
}
```

### Traitements Spécifiques

#### A. Validation & Nettoyage
- ✅ **Parsing des dates ISO 8601** (application_periods.begin/end)
- ✅ **Détection des disruptions expirées** (end < now)
- ✅ **Normalisation des niveaux de sévérité** (mapping priority → niveau critique)
- ✅ **Extraction des lignes impactées** depuis messages.text
- ✅ **Déduplication** (même disruption_id)

#### B. Agrégations Quotidiennes
- 📊 **Par sévérité** :
  - Nombre disruptions actives/jour par niveau
  - Temps total de perturbation/jour (heures)
  - Lignes les plus impactées (Top 10)
  
- 📊 **Par période** :
  - Disruptions en cours (status = active)
  - Disruptions résolues dans les 24h
  - Perturbations prévues (begin > now)
  
- 📊 **Impact estimé** :
  - Nombre d'usagers potentiellement impactés (si données disponibles)
  - Zones géographiques affectées (si géolocalisation disponible)

#### C. Calculs d'Indicateurs
- ⚡ **Alertes** :
  - Disruptions critiques (priority > 50)
  - Perturbations > 2h
  - Plus de 5 disruptions simultanées
  
- 📈 **Métriques** :
  - Taux de fiabilité transport (% temps sans perturbation)
  - Temps moyen de résolution
  - Fréquence disruptions par ligne
  
- 🎯 **Corrélation avec trafic routier** :
  - Si disruption transport → probable hausse trafic voiture
  - Calcul impact estimé sur congestion routière

#### D. Stockage DynamoDB
```
Partition Key: date (YYYY-MM-DD)
Sort Key: disruption_id
Attributes:
  - status
  - severity_level
  - duree_heures
  - lignes_impactees (list)
  - zones_impactees (list)
  - resolue (bool)
```

---

## 3. TRAITEMENTS API WEATHER (Météo)

### Structure des Données
```json
{
  "days": [{
    "datetime": "2025-11-03",
    "tempmax": 15.6,
    "tempmin": 7.3,
    "precip": 0.0,
    "windspeed": 15.5,
    "conditions": "Partially cloudy"
  }],
  "currentConditions": {...}
}
```

### Traitements Spécifiques

#### A. Validation & Nettoyage
- ✅ **Vérification cohérence temporelle** (tempmin ≤ temp ≤ tempmax)
- ✅ **Normalisation des conditions** (mapping vers catégories standards)
- ✅ **Détection valeurs aberrantes** (température < -20°C ou > 45°C à Paris)

#### B. Agrégations Quotidiennes
- 📊 **Métriques agrégées** :
  - Température moyenne journalière
  - Pluviométrie totale (mm)
  - Vent moyen (km/h)
  - Heures d'ensoleillement
  
- 📊 **Catégorisation** :
  - Jour "pluvieux" (precip > 5mm)
  - Jour "venteux" (windspeed > 30 km/h)
  - Jour "froid" (temp < 10°C) ou "chaud" (temp > 25°C)

#### C. Calculs d'Indicateurs
- ⚡ **Impact sur mobilité** :
  - Corrélation pluie → baisse vélos (à calculer)
  - Corrélation météo → évolution trafic (temps réel)
  - Indice météo favorable cyclable (0-100)
  
- 📈 **Prédictions** :
  - Météo prévue 7 jours (si données disponibles)
  - Estimation impact sur fréquentation prévue
  
- 🎯 **Jointure avec autres données** :
  - Corrélation météo + trafic routier
  - Impact météo sur perturbations transport

#### D. Stockage DynamoDB
```
Partition Key: date (YYYY-MM-DD)
Attributes:
  - temp_moyenne
  - precip_totale
  - vent_moyen
  - conditions
  - impact_mobilite (score 0-100)
```

---

## 4. TRAITEMENTS BATCH - COMPTAGES ROUTIERS PERMANENTS

### Structure des Données
```
Identifiant arc; Libelle; Date et heure de comptage; Débit horaire; 
Taux d'occupation; Etat trafic; Identifiant noeud amont; geo_shape
```

**Volume : 20,312,131 lignes (6.2 GB)**

### Traitements Spécifiques (CRITIQUES - Traitement sur EC2)

#### A. Validation & Nettoyage (EC2)
- ✅ **Décompression si nécessaire** (fichier volumineux)
- ✅ **Validation format CSV** (séparateur `;`, encoding UTF-8)
- ✅ **Parsing des dates ISO** avec timezone (`2025-01-11T19:00:00+01:00`)
- ✅ **Nettoyage des valeurs nulles** :
  - Débit horaire vide → marquer comme "donnée manquante"
  - Taux d'occupation vide → calculer si débit disponible
- ✅ **Validation géographique** :
  - Parser geo_shape (GeoJSON LineString)
  - Vérifier cohérence avec geo_point_2d
- ✅ **Détection des arcs invalides** (Etat arc = "Invalide")
- ✅ **Déduplication** (même Identifiant arc + Date/heure)

#### B. Agrégations Quotidiennes (Lambda déclenchée par S3)

**⚠️ IMPORTANT : Traiter par chunks (1000-10000 lignes) pour éviter timeout Lambda**

- 📊 **Par tronçon (Identifiant arc)** :
  - **Débit horaire moyen** (moyenne sur toutes les heures valides)
  - **Débit journalier total** (somme des débits horaires)
  - **Débit maximum** (pic horaire)
  - **Taux d'occupation moyen** (indicateur congestion)
  - **État trafic dominant** (Fluide/Pré-saturé/Saturé)
  - **Période de pointe** (heure avec max débit)
  
- 📊 **Par arrondissement** (via geo_point_2d ou geo_shape) :
  - Nombre de tronçons actifs/jour
  - Débit total arrondissement
  - Tronçons les plus chargés (Top 10)
  
- 📊 **Globale Paris** :
  - Total véhicules/jour
  - Moyenne débit horaire/tronçon
  - Nombre de tronçons saturés
  - Taux de disponibilité des capteurs

#### C. Calculs d'Indicateurs Avancés

- ⚡ **Temps Perdu Estimé** :
  ```
  Pour chaque tronçon :
  1. Vitesse de référence = 50 km/h (route normale) ou 30 km/h (zone urbaine)
  2. Vitesse observée = fonction(taux_occupation)
     - Taux < 30% → vitesse normale
     - Taux 30-70% → vitesse réduite progressivement
     - Taux > 70% → vitesse très réduite (15-20 km/h)
  3. Longueur tronçon = calcul depuis geo_shape (LineString)
  4. Temps normal = longueur / vitesse_référence
  5. Temps observé = longueur / vitesse_observée
  6. Temps perdu = temps_observé - temps_normal (en minutes)
  7. Temps perdu total = temps_perdu × nombre_véhicules
  ```

- 📈 **Alertes de Congestion** :
  - Tronçons avec taux_occupation > 80% pendant > 2h
  - Tronçons avec débit > seuil_critique (percentile 95)
  - Zones avec > 5 tronçons saturés simultanément
  
- 🎯 **Profils "Jour Type"** :
  - Moyenne débit par heure pour Lundi, Mardi, ..., Dimanche
  - Moyenne pour jours fériés
  - Moyenne pour vacances scolaires
  - Comparaison jour actuel vs jour type → écart normalisé

- 📊 **Top Rankings Quotidiens** :
  - Top 10 tronçons les plus fréquentés (débit total)
  - Top 10 tronçons les plus congestionnés (taux occupation)
  - Top 10 zones avec plus de temps perdu

#### D. Détection de Capteurs Défaillants

- 🔍 **Critères de défaillance** :
  - Pas de données pendant > 6h consécutives
  - Valeurs constantes (0 ou même valeur) pendant > 12h
  - Données incohérentes (débit > seuil_max_théorique)
  
- 📋 **Rapport quotidien** :
  - Liste des capteurs défaillants
  - Durée d'indisponibilité
  - Impact estimé (% données manquantes)

#### E. Stockage DynamoDB

```
Table: TrafficMetrics
Partition Key: date (YYYY-MM-DD)
Sort Key: identifiant_arc
Attributes:
  - libelle
  - debit_horaire_moyen
  - debit_journalier_total
  - debit_max
  - taux_occupation_moyen
  - etat_trafic_dominant
  - heure_pic
  - temps_perdu_minutes
  - temps_perdu_total_minutes
  - congestion_alerte (bool)
  - arrondissement
  - geo_point_2d
```

```
Table: TrafficGlobal
Partition Key: date (YYYY-MM-DD)
Attributes:
  - total_vehicules_jour
  - moyenne_debit_par_troncon
  - nombre_troncons_satures
  - taux_disponibilite_capteurs
  - temps_perdu_total_paris (minutes)
```

---

## 5. TRAITEMENTS BATCH - CHANTIERS PERTURBANTS

### Structure des Données
```
Identifiant; Typologie; Date de début; Date de fin; 
Impact sur la circulation; geo_shape; geo_point_2d
```

### Traitements Spécifiques

#### A. Validation & Nettoyage
- ✅ **Parsing des dates** (format français DD-MM-YYYY)
- ✅ **Validation geo_shape** (Polygon ou MultiPolygon GeoJSON)
- ✅ **Détection chantiers actifs** (date début ≤ today ≤ date fin)
- ✅ **Catégorisation des impacts** :
  - BARRAGE_TOTAL → impact = 100%
  - IMPASSE → impact = 80%
  - RESTREINTE → impact = 50%
  - SENS_UNIQUE → impact = 30%

#### B. Agrégations Quotidiennes
- 📊 **Chantiers actifs** :
  - Nombre de chantiers actifs/jour
  - Répartition par type d'impact
  - Surface totale impactée (calcul depuis geo_shape)
  
- 📊 **Par arrondissement** :
  - Nombre de chantiers/arrondissement
  - Impact total estimé par arrondissement
  
- 📊 **Top Zones Impactées** :
  - Arrondissements avec plus de chantiers
  - Zones avec chantiers > 30 jours

#### C. Calculs d'Indicateurs

- ⚡ **Corrélation avec Trafic** :
  - Pour chaque tronçon proche d'un chantier :
    - Calculer impact estimé sur débit routier
    - Ajuster temps perdu avec coefficient chantier
  
- 📈 **Alertes** :
  - Nouveaux chantiers démarrés (alerte début)
  - Chantiers se terminant (alerte fin - potentiel retour normal)
  - Zones avec > 3 chantiers simultanés
  
- 🎯 **Planification Travaux** :
  - Recommandations : éviter zones déjà congestionnées
  - Suggestions : coordonner chantiers proches géographiquement

#### D. Stockage DynamoDB
```
Partition Key: date (YYYY-MM-DD)
Sort Key: identifiant_chantier
Attributes:
  - typologie
  - date_debut
  - date_fin
  - impact_circulation
  - niveau_perturbation
  - arrondissement
  - geo_point_2d
  - actif (bool)
```

---

## 6. TRAITEMENTS BATCH - RÉFÉRENTIEL GÉOGRAPHIQUE

### Structure des Données
```
Identifiant arc; Libelle; Identifiant noeud aval/amont; 
geo_shape; Date debut/fin dispo data
```

### Traitements Spécifiques

#### A. Validation & Nettoyage
- ✅ **Validation période disponibilité** (date début ≤ date fin)
- ✅ **Parsing geo_shape** (LineString GeoJSON)
- ✅ **Calcul longueur tronçons** (depuis coordonnées LineString)
- ✅ **Détection tronçons actifs** (date fin > today)

#### B. Création de Tables de Référence

- 📊 **Table de Mapping** :
  - Identifiant arc → Libelle
  - Identifiant arc → Arrondissement (via geo_point_2d)
  - Identifiant arc → Longueur
  - Identifiant arc → Noeuds amont/aval
  
- 📊 **Index Géographique** :
  - Index par arrondissement
  - Index par proximité (pour jointures spatiales)

#### C. Utilisation

- 🔗 **Enrichissement des données** :
  - Joindre comptages routiers avec référentiel (via Identifiant arc)
  - Ajouter libelle et métadonnées géographiques
  
- 📍 **Calculs géographiques** :
  - Distance entre tronçons
  - Zones de proximité
  - Réseau routier (graphe noeuds/arcs)

#### D. Stockage DynamoDB
```
Table: ReferentielGeographique
Partition Key: identifiant_arc
Attributes:
  - libelle
  - date_debut_dispo
  - date_fin_dispo
  - longueur_metres
  - arrondissement
  - noeud_amont
  - noeud_aval
  - geo_point_2d
  - geo_shape
  - actif (bool)
```

---

## 7. TRAITEMENTS TRANSVERSAUX (Jointures Multi-Sources)

### A. Enrichissement Trafic + Chantiers
- Pour chaque tronçon avec comptage :
  - Vérifier s'il est dans zone chantier (geo_shape intersection)
  - Si oui : ajuster temps perdu avec coefficient chantier
  - Calculer impact estimé du chantier sur débit

### B. Enrichissement Trafic + Météo
- Corrélation conditions météo vs évolution trafic :
  - Pluie → baisse trafic ? (à valider avec données)
  - Météo favorable → hausse vélos ?
  - Vent fort → impact trafic ?

### C. Enrichissement Trafic + Perturbations Transport
- Si disruption RATP active :
  - Identifier zones géographiques impactées
  - Vérifier si hausse trafic routier corrélée
  - Calculer impact estimé sur congestion

---

## 8. RAPPORT QUOTIDIEN (CSV + JSON)

### Structure du Rapport

#### JSON Structure
```json
{
  "date": "2025-11-03",
  "generated_at": "2025-11-04T02:00:00Z",
  "summary": {
    "total_vehicules_paris": 1234567,
    "temps_perdu_total_minutes": 89456,
    "nombre_troncons_satures": 45,
    "taux_disponibilite_capteurs": 98.5
  },
  "top_10_troncons_frequentes": [...],
  "top_10_zones_congestionnees": [...],
  "chantiers_actifs": [...],
  "capteurs_defaillants": [...],
  "alertes_congestion": [...],
  "evolution_vs_semaine_precedente": {...},
  "meteo_impact": {...}
}
```

#### CSV Structure
- Top 10 tronçons fréquentés (Identifiant, Libelle, Débit total)
- Top 10 zones congestionnées (Arrondissement, Temps perdu)
- Capteurs défaillants (Identifiant, Durée indisponibilité)
- Alertes congestion (Tronçon, Heure, Sévérité)

---

## 9. ORCHESTRATION DES TRAITEMENTS

### Ordre d'Exécution (EventBridge Cron)

1. **00:00 UTC** - Déclenchement Lambda quotidien
2. **Ingestion Batch** (si nouveaux fichiers S3) :
   - EC2 traite gros fichiers CSV → découpe en chunks
   - Chunks déposés dans S3 (prefix: `processed/`)
3. **Lambda Traitement** :
   - Traite données batch (chunks)
   - Traite données API (temps réel depuis DynamoDB)
   - Calcule agrégations
   - Détecte anomalies
4. **Stockage** :
   - Enregistre agrégats dans DynamoDB
   - Génère rapport quotidien → S3 (`reports/YYYY-MM-DD/`)
5. **Nettoyage** (optionnel) :
   - Archive anciennes données brutes
   - Supprime données temporaires

---

## 10. OPTIMISATIONS & BONNES PRATIQUES

### Performance
- ✅ Traitement parallèle des chunks (batch)
- ✅ Utilisation DynamoDB BatchWriteItem (25 items max/batch)
- ✅ Compression des rapports JSON (gzip)
- ✅ Partition S3 optimale (prefix par date)

### Coûts
- ✅ Lambda avec timeout adapté (< 15 min)
- ✅ EC2 Spot Instances pour batch
- ✅ DynamoDB on-demand (si faible volume) ou provisioned (si volume important)
- ✅ S3 Intelligent-Tiering pour archive

### Sécurité
- ✅ Validation toutes les données d'entrée
- ✅ Chiffrement S3 (SSE-S3 ou SSE-KMS)
- ✅ DynamoDB encryption at rest
- ✅ IAM roles minimaux (principle of least privilege)

