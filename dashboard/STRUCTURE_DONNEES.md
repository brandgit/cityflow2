# 📊 Structure des données des métriques

## Structure réelle des fichiers JSON

Les fichiers `output/metrics/*_metrics_YYYY-MM-DD.json` contiennent **directement** les "indicators" retournés par chaque processeur.

### 🚴 Bikes (bikes_metrics_*.json)

```json
{
  "metrics": [
    {
      "date": "2025-11-01T22:00:00+00:00",
      "id_compteur": "100007049-101007049",
      "nom_compteur": "28 boulevard Diderot O-E",
      "total_jour": 57.0,
      "moyenne_horaire": 2.375,
      "pic_horaire": 21,
      "arrondissement": "75012",
      "coordinates": {"lon": 2.37559, "lat": 48.84613},
      "anomalie_detectee": false
    }
  ],
  "failing_sensors": [],
  "anomalies": [],
  "top_counters": [...],
  "frequentation_index": 0.0
}
```

**Clés principales :**
- `metrics` : Liste de toutes les métriques par compteur
- `top_counters` : Top compteurs les plus utilisés
- `failing_sensors` : Capteurs défaillants
- `anomalies` : Anomalies détectées
- `frequentation_index` : Indice de fréquentation

### 🚇 Traffic RATP (traffic_metrics_*.json)

```json
{
  "reliability_index": 0.0,
  "active_disruptions_count": 86,
  "total_disruptions_count": 94,
  "top_lignes_impactees": [
    {"ligne": "1", "count": 3},
    {"ligne": "8", "count": 2}
  ],
  "alerts": [
    {
      "id": "63d7c136-...",
      "priority": 30,
      "duration_hours": 3004.65,
      "lignes": ["8"]
    }
  ],
  "disruptions_by_severity": {
    "CRITIQUE": 6,
    "ELEVEE": 58,
    "MOYENNE": 0,
    "FAIBLE": 30
  }
}
```

**Clés principales :**
- `reliability_index` : Indice de fiabilité (0-1)
- `active_disruptions_count` : Nombre de perturbations actives
- `total_disruptions_count` : Total de perturbations
- `top_lignes_impactees` : Lignes les plus impactées
- `alerts` : Alertes critiques
- `disruptions_by_severity` : Répartition par sévérité

### 🚗 Comptages routiers (comptages_metrics_*.json)

```json
{
  "metrics": [...],  // Très volumineux (peut être résumé)
  "top_10_troncons": [
    {
      "identifiant_arc": "5286",
      "libelle": "PI_Jena",
      "debit_journalier_total": 313479.0,
      "taux_occupation_moyen": 32.74,
      "etat_trafic_dominant": "Pré-saturé",
      "zone_fallback": "Sud-Ouest",
      "date": "2025-11-04"
    }
  ],
  "top_10_zones_congestionnees": [...],
  "top_zones_affluence": [...],
  "alertes_congestion": [...],
  "global_metrics": {
    "date": "2025-11-04",
    "nombre_troncons_actifs": 203,
    "debit_journalier_total": 7379104.0,
    "taux_occupation_moyen": 32.85,
    "temps_perdu_total_heures": 13793.22
  }
}
```

**Clés principales :**
- `metrics` : Liste complète (ou résumé si trop volumineux)
- `top_10_troncons` : Top tronçons par débit
- `top_10_zones_congestionnees` : Zones les plus congestionnées
- `top_zones_affluence` : Analyse par zones géographiques
- `alertes_congestion` : Alertes de congestion
- `global_metrics` : Métriques globales agrégées

### 🚧 Chantiers (chantiers_metrics_*.json)

```json
{
  "chantiers_actifs": [...],
  "top_10_chantiers_impact": [...],
  "statistiques_arrondissement": {
    "75001": 5,
    "75002": 3
  },
  "statistiques_impact": {
    "chantiers_impact_eleve": 10,
    "chantiers_impact_moyen": 25,
    "chantiers_impact_faible": 15
  },
  "global_metrics": {
    "nombre_chantiers_actifs": 50,
    "duree_moyenne_jours": 180,
    "surface_totale_impactee_m2": 15000
  }
}
```

**Clés principales :**
- `chantiers_actifs` : Liste des chantiers
- `top_10_chantiers_impact` : Chantiers les plus impactants
- `statistiques_arrondissement` : Répartition par arrondissement
- `statistiques_impact` : Répartition par niveau d'impact
- `global_metrics` : Métriques globales

### 🗺️ Référentiel (referentiel_metrics_*.json)

```json
{
  "mapping": {
    "arc_id_1": {
      "libelle": "...",
      "longueur_metres": 500,
      "arrondissement": "75001"
    }
  },
  "statistiques": {
    "nombre_troncons": 1234,
    "longueur_totale_metres": 567890,
    "longueur_moyenne_metres": 460
  }
}
```

**Clés principales :**
- `mapping` : Mapping arc_id → infos géographiques
- `statistiques` : Statistiques sur le réseau

### 🌤️ Weather (weather_metrics_*.json)

```json
{
  "temperature": 15.5,
  "conditions": "Ensoleillé",
  "precipitation": 0
}
```

## Adaptation du dashboard

### ❌ NE PAS supposer :
- Structure avec `metric_type`, `date`, `metrics` imbriqués
- Présence de `global_metrics` si le processeur ne le retourne pas
- Noms de clés différents de ceux retournés par les processeurs

### ✅ TOUJOURS :
- Charger directement depuis le fichier JSON
- Vérifier que les clés existent avec `.get()`
- Gérer les cas où les données sont vides ou None
- Utiliser les noms de clés exacts retournés par les processeurs

## Exemple de chargement

```python
import json

# Charger bikes
with open('output/metrics/bikes_metrics_2025-11-04.json') as f:
    bikes_data = json.load(f)
    
# Accéder aux données
metrics_list = bikes_data.get("metrics", [])
top_counters = bikes_data.get("top_counters", [])

# Calculer des agrégations
total_passages = sum(m.get("total_jour", 0) for m in metrics_list)
```

## Mise à jour du dashboard

Pour que le dashboard fonctionne correctement :

1. **Vérifier la structure** des fichiers JSON
2. **Adapter les pages** pour utiliser les bonnes clés
3. **Gérer les cas None** pour éviter les erreurs
4. **Ajouter des logs** pour debug si nécessaire

