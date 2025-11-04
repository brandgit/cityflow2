# Résumé Visuel des Traitements par Type de Données

## 📊 Vue d'Ensemble - Matrice des Traitements

| Type de Données | Volume | Traitement Principal | Agrégations Clés | Indicateurs Calculés |
|----------------|--------|---------------------|------------------|---------------------|
| **API Bikes** | 881K compteurs | Validation GPS + Détection défaillances | Total/jour, Pic horaire, Par arrondissement | Indice fréquentation, Anomalies |
| **API Traffic (RATP)** | 841 disruptions | Parsing dates + Extraction lignes | Disruptions actives, Lignes impactées | Taux fiabilité, Alertes critiques |
| **API Weather** | Quotidien | Validation cohérence | Temp moy, Pluviométrie, Vent | Impact mobilité, Corrélation trafic |
| **Batch Comptages** | 20M lignes | **EC2** → Découpe chunks → Lambda | Débit/jour, Taux occupation, Par tronçon | **Temps perdu**, **Congestion**, **Top 10** |
| **Batch Chantiers** | 100 chantiers | Validation dates + Géolocalisation | Chantiers actifs, Par arrondissement | Impact estimé, Alertes zones |
| **Référentiel Geo** | 3,740 tronçons | Validation + Calcul longueurs | Table de référence (lookup) | Enrichissement données |

---

## 🎯 Traitements Prioritaires par Objectif Métier

### 1. FLUX TOTAL VÉHICULES PAR AXE
**Données Sources :** Batch Comptages Routiers
**Traitements :**
- ✅ Agrégation : `Débit journalier total` par `Identifiant arc`
- ✅ Jointure avec Référentiel : Ajouter `Libelle` (nom de la voie)
- ✅ Filtrage : Uniquement tronçons actifs (Etat arc = "Ouvert")
- ✅ Export : Top 10 axes les plus fréquentés

### 2. TEMPS PERDU ESTIMÉ
**Données Sources :** Batch Comptages Routiers + Référentiel Geo
**Traitements :**
- ✅ Calcul longueur tronçon (depuis geo_shape LineString)
- ✅ Vitesse observée = f(taux_occupation)
- ✅ Temps normal = longueur / vitesse_référence (50km/h)
- ✅ Temps observé = longueur / vitesse_observée
- ✅ **Temps perdu = temps_observé - temps_normal** (minutes)
- ✅ Total paris = somme temps_perdu × nombre_véhicules

### 3. ALERTES CONGESTION
**Données Sources :** Batch Comptages Routiers
**Traitements :**
- ✅ Détection : Taux occupation > 80% pendant > 2h
- ✅ Détection : Débit > percentile 95
- ✅ Agrégation : Zones avec > 5 tronçons saturés
- ✅ Enrichissement : Ajouter libelle voie + arrondissement
- ✅ Export : Liste alertes avec coordonnées GPS

---

## 📋 Checklist des Traitements par Type

### ✅ API BIKES
- [ ] Validation coordonnées GPS
- [ ] Détection compteurs défaillants (inactifs > 24h)
- [ ] Agrégation : Total/jour, Moyenne horaire, Pic horaire
- [ ] Agrégation : Par arrondissement
- [ ] Calcul : Indice fréquentation cyclable
- [ ] Détection anomalies (> 300% variation)

### ✅ API TRAFFIC (RATP)
- [ ] Parsing dates ISO 8601
- [ ] Détection disruptions expirées
- [ ] Extraction lignes impactées depuis messages
- [ ] Agrégation : Disruptions actives/jour
- [ ] Calcul : Taux fiabilité transport
- [ ] Alertes : Disruptions critiques (> 2h, priority > 50)

### ✅ API WEATHER
- [ ] Validation cohérence (tempmin ≤ temp ≤ tempmax)
- [ ] Normalisation conditions météo
- [ ] Agrégation : Temp moy, Pluviométrie, Vent
- [ ] Catégorisation : Jour pluvieux/venteux/froid
- [ ] Calcul : Impact estimé sur mobilité
- [ ] Corrélation : Météo ↔ Trafic routier

### ✅ BATCH COMPTAGES ROUTIERS (CRITIQUE)
- [ ] **EC2** : Décompression + Validation format CSV
- [ ] **EC2** : Découpe en chunks (1000-10000 lignes)
- [ ] **Lambda** : Parsing dates avec timezone
- [ ] **Lambda** : Parsing geo_shape (GeoJSON)
- [ ] **Lambda** : Nettoyage valeurs nulles
- [ ] **Lambda** : Calcul débit horaire/journalier par tronçon
- [ ] **Lambda** : Calcul taux occupation moyen
- [ ] **Lambda** : **Calcul temps perdu** (formule complexe)
- [ ] **Lambda** : Détection capteurs défaillants
- [ ] **Lambda** : Génération Top 10 tronçons
- [ ] **Lambda** : Génération Top 10 zones congestionnées
- [ ] **Lambda** : Profils "jour type" (Lundi, Mardi, etc.)

### ✅ BATCH CHANTIERS
- [ ] Parsing dates (format français)
- [ ] Validation geo_shape (Polygon/MultiPolygon)
- [ ] Détection chantiers actifs
- [ ] Catégorisation impacts (BARRAGE_TOTAL = 100%, etc.)
- [ ] Agrégation : Chantiers actifs/jour
- [ ] Agrégation : Par arrondissement
- [ ] Calcul : Impact estimé sur trafic
- [ ] Alertes : Zones avec > 3 chantiers simultanés

### ✅ RÉFÉRENTIEL GÉOGRAPHIQUE
- [ ] Validation période disponibilité
- [ ] Parsing geo_shape (LineString)
- [ ] Calcul longueur tronçons
- [ ] Détection tronçons actifs
- [ ] Création table de mapping (lookup)
- [ ] Index par arrondissement
- [ ] Enrichissement données trafic (jointure)

---

## 🔄 Flux de Traitement Quotidien

```
00:00 EventBridge → Déclenche Lambda Quotidienne
│
├─→ 1. INGESTION BATCH (si nouveaux fichiers S3)
│   ├─→ EC2 : Traite gros fichiers CSV (6.2 GB)
│   ├─→ EC2 : Découpe en chunks → S3 (prefix: processed/)
│   └─→ Lambda : Traite chunks → DynamoDB
│
├─→ 2. TRAITEMENT DONNÉES API (depuis DynamoDB temps réel)
│   ├─→ API Bikes : Agrégations quotidiennes
│   ├─→ API Traffic : Disruptions actives
│   └─→ API Weather : Conditions du jour
│
├─→ 3. CALCULS AVANCÉS
│   ├─→ Temps perdu par tronçon
│   ├─→ Alertes congestion
│   ├─→ Top 10 tronçons/zones
│   ├─→ Détection capteurs défaillants
│   └─→ Profils "jour type"
│
├─→ 4. JOINTURES MULTI-SOURCES
│   ├─→ Trafic + Chantiers (impact géographique)
│   ├─→ Trafic + Météo (corrélation)
│   └─→ Trafic + Perturbations transport
│
├─→ 5. GÉNÉRATION RAPPORT
│   ├─→ Format JSON complet
│   ├─→ Format CSV (Top 10, Alertes)
│   └─→ Upload S3 (reports/YYYY-MM-DD/)
│
└─→ 6. STOCKAGE DYNAMODB
    ├─→ Table TrafficMetrics (par tronçon)
    ├─→ Table TrafficGlobal (agrégé Paris)
    └─→ Tables autres données (Bikes, Weather, etc.)
```

---

## 📊 Structure des Agrégations DynamoDB

### Table: `TrafficMetrics`
```
PK: date (YYYY-MM-DD)
SK: identifiant_arc
Attributes:
  - libelle (nom voie)
  - debit_horaire_moyen
  - debit_journalier_total
  - debit_max
  - taux_occupation_moyen
  - etat_trafic_dominant
  - heure_pic
  - temps_perdu_minutes ⭐
  - temps_perdu_total_minutes ⭐
  - congestion_alerte (bool)
  - arrondissement
  - geo_point_2d
```

### Table: `TrafficGlobal`
```
PK: date (YYYY-MM-DD)
Attributes:
  - total_vehicules_paris
  - moyenne_debit_par_troncon
  - nombre_troncons_satures
  - taux_disponibilite_capteurs
  - temps_perdu_total_paris (minutes) ⭐
```

### Table: `DailyReport`
```
PK: date (YYYY-MM-DD)
Attributes:
  - top_10_troncons_frequentes (list)
  - top_10_zones_congestionnees (list)
  - capteurs_defaillants (list)
  - alertes_congestion (list)
  - s3_report_json_path
  - s3_report_csv_path
```

---

## ⚡ Points Critiques de Performance

### 🚨 Fichier Comptages Routiers (6.2 GB)
- **OBLIGATOIRE EC2** : Lambda timeout 15 min max
- Stratégie : 
  1. EC2 télécharge fichier S3
  2. EC2 lit par chunks (streaming)
  3. EC2 écrit chunks traités → S3 (`processed/chunk_001.csv`)
  4. Lambda déclenchée par événement S3 → traite chaque chunk
  5. Lambda agrège résultats → DynamoDB

### ⚡ Lambda Timeout
- Traitement batch : Max 15 min
- Solution : Chunks < 10,000 lignes
- Utiliser `BatchWriteItem` DynamoDB (25 items/batch max)

### 💾 DynamoDB Limites
- Item max 400 KB
- BatchWriteItem : 25 items max, 16 MB max
- Solution : Split gros items, utiliser plusieurs tables

---

## 🎯 Indicateurs Clés Calculés (API Response)

### GET `/traffic-metrics?date=2025-11-03`

```json
{
  "date": "2025-11-03",
  "flux_total_vehicules": 1234567,
  "axes_principaux": [
    {
      "identifiant_arc": "1067",
      "libelle": "Quai_d'Issy",
      "flux_total": 45678,
      "temps_perdu_minutes": 234
    },
    ...
  ],
  "temps_perdu_total_minutes": 89456,
  "alertes_congestion": [
    {
      "troncon": "Quai_d'Issy",
      "heure": "08:00",
      "severite": "Critique",
      "taux_occupation": 92.5,
      "coordinates": [2.2702, 48.8397]
    },
    ...
  ]
}
```

---

## 📝 Notes Importantes

### Calcul Temps Perdu (Formule Détail)
```
Pour chaque tronçon avec comptage :
1. Longueur = distance(geo_shape LineString) en mètres
2. Vitesse référence = 50 km/h (ou 30 km/h zone urbaine)
3. Vitesse observée = f(taux_occupation):
   - taux < 30% → vitesse = vitesse_référence
   - taux 30-50% → vitesse = vitesse_référence × 0.8
   - taux 50-70% → vitesse = vitesse_référence × 0.6
   - taux > 70% → vitesse = 20 km/h
4. Temps normal = (longueur / 1000) / vitesse_référence × 60 (minutes)
5. Temps observé = (longueur / 1000) / vitesse_observée × 60 (minutes)
6. Temps perdu = temps_observé - temps_normal
7. Temps perdu total = temps_perdu × nombre_véhicules (débit journalier)
```

### Détection Capteurs Défaillants
```
Critères :
- Pas de données > 6h consécutives
- Valeur constante (> 12h même valeur)
- Données incohérentes (débit > seuil_max)

Action :
- Marquer dans DynamoDB : capteur_defaillant = true
- Exclure des calculs agrégés
- Rapporter dans rapport quotidien
```

### Profils "Jour Type"
```
Pour chaque jour de semaine (Lundi-Dimanche) :
- Calculer moyenne historique par heure (00h-23h)
- Stocker dans DynamoDB (PK: jour_semaine, SK: heure)
- Comparer jour actuel vs jour type → écart normalisé
- Détecter anomalies si écart > 2 écarts-types
```

