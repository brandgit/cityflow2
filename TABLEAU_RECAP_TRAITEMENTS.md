# 📋 Tableau Récapitulatif des Traitements par Données

## 🚴 API BIKES (Compteurs Vélos)

| Étape | Traitement | Détails |
|-------|-----------|---------|
| **Validation** | Coordonnées GPS | lon ∈ [-180,180], lat ∈ [-90,90] |
| **Validation** | Détection défaillances | sum_counts = 0 ou null > 24h |
| **Agrégation** | Total/jour par compteur | Somme sum_counts |
| **Agrégation** | Pic horaire | Heure avec max passages |
| **Agrégation** | Par arrondissement | Total passages/arrondissement |
| **Calcul** | Indice fréquentation | Score 0-100 |
| **Détection** | Anomalies | Variation > 300% vs historique |

**Stockage DynamoDB :**
- PK: `date`, SK: `id_compteur`
- Attributes: total_jour, moyenne_horaire, pic_horaire, arrondissement

---

## �� API TRAFFIC (Perturbations RATP)

| Étape | Traitement | Détails |
|-------|-----------|---------|
| **Parsing** | Dates ISO 8601 | application_periods.begin/end |
| **Validation** | Disruptions expirées | end < now → exclure |
| **Extraction** | Lignes impactées | Parse messages.text |
| **Agrégation** | Disruptions actives/jour | Status = "active" |
| **Agrégation** | Par sévérité | Nombre par niveau (priority) |
| **Calcul** | Taux fiabilité | % temps sans perturbation |
| **Alertes** | Disruptions critiques | Priority > 50 ou durée > 2h |

**Stockage DynamoDB :**
- PK: `date`, SK: `disruption_id`
- Attributes: status, severity_level, duree_heures, lignes_impactees

---

## 🌤️ API WEATHER (Météo)

| Étape | Traitement | Détails |
|-------|-----------|---------|
| **Validation** | Cohérence température | tempmin ≤ temp ≤ tempmax |
| **Normalisation** | Conditions météo | Mapping vers catégories standards |
| **Agrégation** | Température moyenne | (tempmin + tempmax) / 2 |
| **Agrégation** | Pluviométrie totale | Somme precip (mm) |
| **Catégorisation** | Jour type météo | Pluvieux (>5mm), Venteux (>30km/h) |
| **Calcul** | Impact mobilité | Corrélation météo ↔ trafic |
| **Corrélation** | Météo ↔ Vélos | Pluie → baisse vélos ? |

**Stockage DynamoDB :**
- PK: `date`
- Attributes: temp_moyenne, precip_totale, vent_moyen, impact_mobilite

---

## 🚗 BATCH COMPTAGES ROUTIERS (CRITIQUE - 20M lignes, 6.2 GB)

### Phase 1 : EC2 (Traitement Initial)
| Étape | Traitement | Détails |
|-------|-----------|---------|
| **EC2** | Décompression fichier | Si .gz ou .zip |
| **EC2** | Validation CSV | Séparateur `;`, UTF-8 |
| **EC2** | Découpe en chunks | 1000-10000 lignes/chunk |
| **EC2** | Upload chunks → S3 | Prefix: `processed/chunk_XXX.csv` |

### Phase 2 : Lambda (Traitement Chunks)
| Étape | Traitement | Détails |
|-------|-----------|---------|
| **Parsing** | Dates avec timezone | ISO format `2025-01-11T19:00:00+01:00` |
| **Parsing** | GeoJSON LineString | geo_shape validation |
| **Nettoyage** | Valeurs nulles | Débit vide → "donnée manquante" |
| **Filtrage** | Tronçons invalides | Etat arc = "Invalide" → exclure |
| **Agrégation** | Débit horaire moyen | Moyenne sur heures valides |
| **Agrégation** | Débit journalier total | Somme débits horaires |
| **Agrégation** | Taux occupation moyen | Moyenne taux_occupation |
| **Agrégation** | État trafic dominant | Mode (Fluide/Pré-saturé/Saturé) |
| **Agrégation** | Heure pic | Heure avec max débit |
| **Agrégation** | Par arrondissement | Via geo_point_2d |

### Phase 3 : Calculs Avancés (Lambda)
| Étape | Traitement | Détails |
|-------|-----------|---------|
| **⭐ CALCUL** | **Temps Perdu** | Formule complexe (voir détail) |
| **Détection** | Alertes congestion | Taux occupation > 80% > 2h |
| **Détection** | Capteurs défaillants | Pas données > 6h ou valeur constante |
| **Ranking** | Top 10 tronçons fréquentés | Par débit journalier total |
| **Ranking** | Top 10 zones congestionnées | Par temps perdu total |
| **Profils** | Jour type | Moyenne historique par jour semaine |

**Stockage DynamoDB :**
- Table `TrafficMetrics`: PK: `date`, SK: `identifiant_arc`
- Table `TrafficGlobal`: PK: `date` (agrégé Paris)

---

## 🚧 BATCH CHANTIERS PERTURBANTS

| Étape | Traitement | Détails |
|-------|-----------|---------|
| **Parsing** | Dates françaises | Format DD-MM-YYYY |
| **Validation** | GeoJSON Polygon | geo_shape validation |
| **Détection** | Chantiers actifs | date_debut ≤ today ≤ date_fin |
| **Catégorisation** | Impact circulation | BARRAGE=100%, IMPASSE=80%, RESTREINTE=50% |
| **Agrégation** | Chantiers actifs/jour | Nombre total |
| **Agrégation** | Par arrondissement | Nombre chantiers/arrondissement |
| **Calcul** | Impact estimé trafic | Coefficient selon type chantier |
| **Alertes** | Zones critiques | > 3 chantiers simultanés |
| **Jointure** | Trafic + Chantiers | Intersection géographique |

**Stockage DynamoDB :**
- PK: `date`, SK: `identifiant_chantier`
- Attributes: typologie, impact_circulation, arrondissement, actif

---

## 🗺️ RÉFÉRENTIEL GÉOGRAPHIQUE

| Étape | Traitement | Détails |
|-------|-----------|---------|
| **Validation** | Période disponibilité | date_debut ≤ date_fin |
| **Parsing** | GeoJSON LineString | geo_shape |
| **Calcul** | Longueur tronçons | Distance depuis coordonnées |
| **Détection** | Tronçons actifs | date_fin > today |
| **Création** | Table de mapping | Identifiant → Libelle, Arrondissement |
| **Index** | Par arrondissement | Pour jointures rapides |
| **Enrichissement** | Jointure avec comptages | Via Identifiant arc |

**Stockage DynamoDB :**
- PK: `identifiant_arc`
- Attributes: libelle, longueur_metres, arrondissement, geo_shape

---

## 📊 RAPPORT QUOTIDIEN

### Génération (Lambda déclenchée EventBridge 00:00)

| Section | Contenu | Format |
|---------|---------|--------|
| **Summary** | Total véhicules, Temps perdu, Tronçons saturés | JSON + CSV |
| **Top 10 Tronçons** | Les plus fréquentés (débit total) | JSON + CSV |
| **Top 10 Zones** | Les plus congestionnées (temps perdu) | JSON + CSV |
| **Capteurs Défaillants** | Liste avec durée indisponibilité | JSON + CSV |
| **Alertes Congestion** | Zones critiques avec coordonnées | JSON + CSV |
| **Chantiers Actifs** | Impact sur circulation | JSON + CSV |
| **Évolution** | vs Semaine précédente | JSON |

**Upload S3 :** `s3://bucket/reports/YYYY-MM-DD/report.json` + `.csv`

---

## 🔄 ORCHESTRATION (EventBridge)

| Heure | Action | Service |
|-------|--------|---------|
| **00:00 UTC** | Déclenchement quotidien | EventBridge → Lambda |
| **00:00-00:05** | Ingestion batch (si fichiers) | EC2 + Lambda |
| **00:05-00:15** | Traitement données API | Lambda |
| **00:15-00:20** | Calculs avancés | Lambda |
| **00:20-00:25** | Jointures multi-sources | Lambda |
| **00:25-00:30** | Génération rapport | Lambda |
| **00:30** | Upload S3 + DynamoDB | Lambda |

---

## ⚡ FORMULE TEMPS PERDU (Détaillée)

```
Pour chaque tronçon :
1. Longueur = distance(geo_shape) mètres
2. Vitesse référence = 50 km/h (ou 30 km/h zone)
3. Vitesse observée = f(taux_occupation):
   - taux < 30%  → vitesse = vitesse_référence
   - taux 30-50% → vitesse = vitesse_référence × 0.8
   - taux 50-70% → vitesse = vitesse_référence × 0.6
   - taux > 70%  → vitesse = 20 km/h
4. Temps normal = (longueur/1000) / vitesse_réf × 60 (min)
5. Temps observé = (longueur/1000) / vitesse_obs × 60 (min)
6. Temps perdu = temps_observé - temps_normal
7. Temps perdu total = temps_perdu × nombre_véhicules
```

---

## 🎯 API REST - Endpoints Clés

### GET `/traffic-metrics?date=YYYY-MM-DD`
**Réponse :**
- Flux total véhicules par axe principal
- Temps perdu estimé total
- Alertes congestion (zones critiques)

### GET `/daily-report?date=YYYY-MM-DD`
**Réponse :**
- URL S3 rapport JSON
- URL S3 rapport CSV

### GET `/bike-metrics?date=YYYY-MM-DD&arrondissement=75001`
**Réponse :**
- Total passages vélos
- Top compteurs
- Évolution vs semaine précédente

---

## ✅ Checklist Traitements Obligatoires

- [x] Ingestion batch (S3 → EC2 → Lambda)
- [x] Ingestion temps réel (API Gateway → Lambda → DynamoDB)
- [x] Stockage DynamoDB (agrégats)
- [x] Traitement quotidien (EventBridge → Lambda)
- [x] Génération rapport (CSV + JSON → S3)
- [x] API REST (API Gateway → Lambda → DynamoDB)
- [x] Calcul temps perdu
- [x] Top 10 tronçons fréquentés
- [x] Top 10 zones congestionnées
- [x] Détection capteurs défaillants
- [x] Alertes congestion
