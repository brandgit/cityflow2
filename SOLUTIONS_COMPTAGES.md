# 🎯 Solutions pour Comptages > 16 MB MongoDB

## 📊 Problème

Les métriques **comptages** dépassent la limite MongoDB de **16 MB par document** car elles contiennent :
- **3348 tronçons** routiers avec métriques détaillées
- **~7.4 millions de lignes** dans le JSON
- **> 16 MB** de données

---

## ✅ Solution Implémentée : Version Summary (Optimisée)

### 🎯 Principe

**Stockage hybride :**
- ✅ **MongoDB** : Version **summary** (métriques agrégées seulement)
- ✅ **Fichier local** : Version **complète** (tous les tronçons)

### 📦 Structure Summary (pour MongoDB)

```json
{
  "global_metrics": {
    "total_vehicules_jour": 1234567,
    "temps_perdu_total_paris": 89456,
    "nombre_troncons_satures": 45
  },
  "top_10_troncons": [
    {"libelle": "SI_Passy", "debit": 717.9, ...},
    // ... seulement 10 tronçons
  ],
  "top_10_zones_congestionnees": [...],
  "alertes_congestion": [...],
  "total_troncons": 3348,  // Information de comptage
  "note": "Liste complète disponible en fichier local uniquement"
}
```

**Taille estimée** : ~50-100 KB (vs 16+ MB) ✅

### 📁 Structure Complète (fichier local)

```json
{
  "metrics": [
    // Tous les 3348 tronçons avec détails complets
    {"libelle": "SI_Passy", ...},
    {"libelle": "St_Antoine", ...},
    // ... 3348 entrées
  ],
  "top_10_troncons": [...],
  "top_10_zones_congestionnees": [...],
  "global_metrics": {...}
}
```

**Taille** : ~16+ MB (disponible en local)

---

## 🔄 Flux Automatique

```
┌─────────────────────────────────────────────────┐
│  Processeur Comptages                           │
│  Génère indicators complets (3348 tronçons)     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Export Results                                 │
│  1. Détecte: comptages > 16 MB ?               │
│  2. Crée version summary                        │
└──────┬──────────────────────┬───────────────────┘
       │                      │
       ▼                      ▼
┌─────────────┐      ┌──────────────────┐
│  MongoDB    │      │ Fichier Local    │
│  (Summary) │      │ (Version Complète)│
│  ~100 KB    │      │ ~16+ MB          │
│  ✅ OK      │      │ ✅ Backup        │
└─────────────┘      └──────────────────┘
       │                      │
       │                      │
       └──────────┬───────────┘
                  ▼
      ┌───────────────────────┐
      │ Génération Rapport    │
      │ 1. Charge summary     │
      │    depuis MongoDB     │
      │ 2. Si besoin complet: │
      │    Charge fichier     │
      └───────────────────────┘
```

---

## 💡 Avantages de cette Solution

| Aspect | Avantage |
|--------|----------|
| **✅ Compatible MongoDB** | Respecte limite 16 MB |
| **✅ Données complètes** | Version complète en local |
| **✅ Rapport fonctionne** | Summary suffit pour Top 10, global_metrics |
| **✅ Transparent** | Détection automatique |
| **✅ Fallback** | Si MongoDB échoue, fichier local toujours disponible |
| **✅ Pas de perte** | Aucune donnée perdue |

---

## 🔧 Autres Solutions Possibles (non implémentées)

### Solution B : Fragmenter en Documents Séparés

**Principe** : Un document MongoDB par tronçon

```python
# Collection: comptages_details
for troncon in metrics:
    db.comptages_details.insert_one({
        "troncon_id": troncon["identifiant_arc"],
        "date": "2025-11-03",
        "metrics": troncon
    })

# Collection: comptages_summary
db.comptages_summary.insert_one({
    "date": "2025-11-03",
    "global_metrics": {...},
    "top_10_troncons": [...]
})
```

**Avantages** :
- ✅ Pas de limite de taille
- ✅ Requêtes ciblées par tronçon

**Inconvénients** :
- ⚠️ Complexité accrue
- ⚠️ 3348 requêtes pour récupérer tous les tronçons
- ⚠️ Plus coûteux en opérations

---

### Solution C : MongoDB GridFS

**Principe** : Utiliser GridFS pour fichiers > 16 MB

```python
from gridfs import GridFS

# Stocker gros fichier
fs = GridFS(db)
file_id = fs.put(
    json.dumps(indicators).encode(),
    filename=f"comptages_{date}.json"
)

# Charger
data = fs.get(file_id).read()
indicators = json.loads(data)
```

**Avantages** :
- ✅ Pas de limite de taille
- ✅ Intégré MongoDB

**Inconvénients** :
- ⚠️ Requêtes plus lentes
- ⚠️ Pas de requêtes JSON natives
- ⚠️ Plus complexe à gérer

---

### Solution D : S3 pour Gros Fichiers

**Principe** : Stocker comptages complets dans S3 (même en local)

```python
# Local : Utiliser un dossier S3-like
# AWS : Utiliser S3 réellement

s3_path = f"s3://cityflow-data/comptages/{date}.json"
# Ou local: output/s3/comptages/{date}.json
```

**Avantages** :
- ✅ Pas de limite (S3)
- ✅ Bon pour gros fichiers
- ✅ Même logique local/AWS

**Inconvénients** :
- ⚠️ Nécessite boto3 même en local
- ⚠️ Plus complexe que fichiers locaux

---

## 📊 Comparaison des Solutions

| Solution | Taille max | Complexité | Performance | Recommandé |
|----------|-----------|------------|------------|------------|
| **A. Summary (implémentée)** ⭐ | 16 MB | ⭐ Simple | ⭐⭐⭐ Excellente | ✅ OUI |
| B. Fragmentation | Illimitée | ⭐⭐⭐ Complexe | ⭐⭐ Moyenne | Pour production avancée |
| C. GridFS | Illimitée | ⭐⭐ Moyenne | ⭐ Faible | Non recommandé |
| D. S3 | Illimitée | ⭐⭐ Moyenne | ⭐⭐⭐ Excellente | Pour AWS uniquement |

---

## 🎯 Pourquoi la Solution Summary est Optimale

### 1. **Pour les Rapports**

Les rapports n'ont besoin que de :
- ✅ `global_metrics` (totaux, moyennes)
- ✅ `top_10_troncons` (les plus fréquentés)
- ✅ `top_10_zones` (les plus congestionnées)
- ✅ `alertes_congestion` (alertes critiques)

**La liste complète des 3348 tronçons n'est PAS nécessaire pour les rapports !**

### 2. **Pour l'Analyse Détaillée**

Si vous avez besoin d'analyser un tronçon spécifique :
- ✅ Charger depuis fichier local : `output/metrics/comptages_metrics_2025-11-03.json`
- ✅ Ou utiliser l'API Python pour charger depuis le JSON

### 3. **Production AWS**

Quand vous déployez sur AWS :
- ✅ DynamoDB pour summary (rapide)
- ✅ S3 pour version complète (gros fichiers)

---

## 🧪 Tester la Solution

### Après exécution du pipeline :

```bash
python3 main.py
```

**Vous devriez voir :**
```
⚠ Métriques comptages optimisées pour stockage (taille réduite)
   → Version complète disponible en fichier local uniquement
✓ Métriques comptages (summary) exportées vers MONGODB
  → Sauvegarde locale (backup complet): output/metrics/comptages_metrics_2025-11-03.json
```

### Vérifier dans MongoDB :

```javascript
// MongoDB Compass
db.metrics.findOne({"metric_type": "comptages"})

// Devrait contenir :
{
  "metric_type": "comptages",
  "date": "2025-11-03",
  "metrics": {
    "global_metrics": {...},
    "top_10_troncons": [...],  // Seulement 10
    "top_10_zones": [...],     // Seulement 10
    "note": "Liste complète disponible dans fichier local uniquement"
  }
}
```

### Vérifier fichier local :

```bash
# Taille du fichier local (devrait être ~16+ MB)
ls -lh output/metrics/comptages_metrics_2025-11-03.json

# Contenu avec tous les tronçons
jq '.metrics | length' output/metrics/comptages_metrics_2025-11-03.json
# Devrait afficher: 3348
```

---

## ✅ Résumé

**Solution implémentée :** Version **summary optimisée** pour MongoDB

**Stockage :**
- ✅ **MongoDB** : Summary (~100 KB) avec métriques agrégées
- ✅ **Fichier local** : Version complète (~16+ MB) avec tous les tronçons

**Utilisation :**
- ✅ **Rapports** : Utilisent summary depuis MongoDB
- ✅ **Analyse détaillée** : Chargent version complète depuis fichier local

**Résultat :**
- ✅ Plus d'erreur MongoDB !
- ✅ Données complètes conservées
- ✅ Performances optimales

---

**La solution est automatique et transparente ! Relancez `python3 main.py` pour voir la différence !** 🚀

