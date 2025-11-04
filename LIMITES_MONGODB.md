# ⚠️ Limites MongoDB et Solutions - CityFlow Analytics

## 🚨 Problème identifié

Lors de l'exécution du pipeline, vous avez rencontré cette erreur :

```
✗ Erreur MongoDB save_metrics: 'update' command document too large
✗ Erreur export métriques comptages vers MONGODB
```

---

## 📏 Limite MongoDB

**MongoDB a une limite stricte de 16 MB par document.**

Vos métriques **comptages** font :
- **7.4 millions de lignes** dans le fichier JSON
- Bien au-delà de la limite de 16 MB !

---

## 🔍 Pourquoi les comptages sont si gros ?

Le fichier `comptages_metrics_2025-11-03.json` contient :
- **~3348 tronçons** routiers
- Chaque tronçon a des métriques détaillées (débit horaire, taux occupation, temps perdu, etc.)
- **204 chunks** traités avec agrégations

**Exemple de structure :**
```json
{
  "metrics": [
    {
      "libelle": "SI_Passy",
      "debit_horaire_moyen": 717.9,
      "debit_journalier_total": 33661014.65,
      "taux_occupation_moyen": 9.34,
      "temps_perdu_minutes": 0.0,
      // ... beaucoup de données
    },
    // ... × 3348 tronçons
  ],
  "top_10_troncons": [...],
  "top_10_zones": [...],
  "global_metrics": {...}
}
```

---

## ✅ Solutions implémentées

### Solution 1 : Fallback automatique vers fichiers locaux ⭐

**Le code détecte automatiquement** que les comptages sont trop gros et utilise les fichiers locaux :

```python
# report_generator/daily_report_generator.py
try:
    # Essayer de charger depuis MongoDB
    metric_data = db_service.load_metrics(data_type="comptages", date=date)
except Exception:
    # ✅ FALLBACK : Charger depuis fichier local
    with open("output/metrics/comptages_metrics_2025-11-03.json") as f:
        metric_data = json.load(f)
        print("→ Fallback: métriques comptages chargées depuis fichier local")
```

**Résultat :**
```
⚠ Erreur chargement métriques comptages depuis MONGODB: ...
→ Fallback: métriques comptages chargées depuis fichier local
```

### Solution 2 : Backup local systématique

**Toutes les métriques** sont sauvegardées en local en plus de la base de données :

```python
# processors/main.py (ligne 206-211)
# Fallback: sauvegarder aussi en local si en développement
if not os.getenv("AWS_EXECUTION_ENV"):
    save_json(indicators, f"output/metrics/{data_type}_metrics_{date}.json")
    print(f"  → Sauvegarde locale (backup): ...")
```

**Avantage** : Même si MongoDB/DynamoDB échoue, les données sont accessibles !

---

## 🎯 Solutions alternatives (pour plus tard)

### Option A : Fragmenter les métriques comptages

Au lieu de stocker tous les tronçons dans un seul document, créer un document par tronçon :

```javascript
// MongoDB - Collection: comptages_details
{
  "troncon_id": "SI_Passy",
  "date": "2025-11-03",
  "metrics": {
    "debit_horaire_moyen": 717.9,
    // ...
  }
}

// MongoDB - Collection: comptages_summary
{
  "date": "2025-11-03",
  "global_metrics": {...},
  "top_10_troncons": [...],
  "top_10_zones": [...]
}
```

**Avantages** :
- ✅ Respecte la limite 16 MB
- ✅ Requêtes plus rapides
- ✅ Scalable

**Inconvénient** :
- ⚠️ Plus complexe à implémenter

### Option B : Utiliser MongoDB GridFS

Pour les gros documents > 16 MB, MongoDB propose GridFS :

```python
from pymongo import MongoClient
from gridfs import GridFS

# Stocker gros document dans GridFS
fs = GridFS(db)
file_id = fs.put(json.dumps(comptages_metrics).encode(), filename="comptages_2025-11-03.json")

# Charger
data = fs.get(file_id).read()
comptages_metrics = json.loads(data)
```

**Avantages** :
- ✅ Pas de limite de taille
- ✅ Intégré à MongoDB

**Inconvénient** :
- ⚠️ Moins performant pour requêtes

### Option C : Basculer vers DynamoDB pour les gros datasets

DynamoDB a une limite de **400 KB par item**, mais on peut fragmenter différemment :

```javascript
// DynamoDB - Table: comptages-details
{
  "troncon_id": "SI_Passy",      // Partition Key
  "date": "2025-11-03",          // Sort Key
  "metrics": {...}
}
```

---

## 🎨 Architecture hybride actuelle

```
┌─────────────────────────────────────────────────┐
│           Métriques par type                    │
└───┬───────────┬──────────┬──────────┬───────────┘
    │           │          │          │
    ▼           ▼          ▼          ▼
┌────────┐ ┌─────────┐ ┌──────┐ ┌──────────┐
│ Bikes  │ │ Traffic │ │Weather│ │Chantiers │
│ (1482) │ │  (613)  │ │ (14)  │ │  (469)   │
│  < 1MB │ │  < 1MB  │ │ < 1KB │ │  < 1MB   │
└───┬────┘ └────┬────┘ └───┬───┘ └────┬─────┘
    │           │          │          │
    ▼           ▼          ▼          ▼
  ┌───────────────────────────────────┐
  │         MongoDB ✅                 │
  └───────────────────────────────────┘

┌──────────┐
│ Comptages│
│(7.4M)    │
│  > 16MB  │  ❌ Trop gros pour MongoDB
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Fichier local ✅ │
│ (backup)         │
└──────────────────┘
```

---

## ✅ Comportement actuel (OPTIMAL)

| Métrique | Taille | MongoDB | Fichier local |
|----------|--------|---------|---------------|
| **Bikes** | < 1 MB | ✅ OK | ✅ Backup |
| **Traffic** | < 1 MB | ✅ OK | ✅ Backup |
| **Weather** | < 1 KB | ✅ OK | ✅ Backup |
| **Chantiers** | < 1 MB | ✅ OK (corrigé) | ✅ Backup |
| **Référentiel** | ~1 MB | ✅ OK | ✅ Backup |
| **Comptages** | **> 16 MB** | ❌ Trop gros | ✅ **Source principale** |

---

## 🎯 Solution actuelle (déjà implémentée)

Le générateur de rapport **utilise automatiquement le fallback** :

1. **Essayer MongoDB** : bikes, traffic, weather, chantiers ✅
2. **Comptages échoue** : Trop gros ❌
3. **Fallback automatique** : Charge depuis `output/metrics/comptages_metrics_2025-11-03.json` ✅
4. **Rapport généré** : Avec toutes les données ! ✅

**C'est transparent pour l'utilisateur !**

---

## 🚀 Migration vers DynamoDB (Production)

En production AWS, **DynamoDB gère mieux les gros datasets** :

### Stratégie recommandée :

1. **Petites métriques** (bikes, traffic, weather) → Un seul item DynamoDB
2. **Grosses métriques** (comptages) → Fragmenter par tronçon

**Exemple DynamoDB :**
```javascript
// Table: cityflow-comptages-details
{
  "troncon_id": "SI_Passy",  // Partition Key
  "date": "2025-11-03",      // Sort Key
  "metrics": {
    "debit_horaire_moyen": 717.9,
    // ...
  }
}

// Table: cityflow-comptages-summary
{
  "date": "2025-11-03",
  "summary_type": "global",
  "top_10_troncons": [...],
  "global_metrics": {...}
}
```

**Avantages** :
- ✅ Pas de limite 16 MB
- ✅ Requêtes rapides par tronçon
- ✅ Scalable

---

## 💡 Recommandations

### Pour le développement local (actuel) :

✅ **Garder l'architecture actuelle** : Fallback automatique vers fichiers locaux  
✅ **MongoDB pour petites métriques** : bikes, traffic, weather, chantiers  
✅ **Fichiers locaux pour comptages** : Pas de limite de taille  

**C'est la solution optimale pour le développement !**

### Pour la production AWS :

Quand vous déployez sur AWS :

1. ✅ **Option simple** : Utiliser S3 pour stocker les comptages en JSON
   ```python
   s3.put_object(Bucket="cityflow-data", Key=f"comptages/{date}.json", Body=json.dumps(comptages))
   ```

2. ✅ **Option optimale** : Fragmenter en DynamoDB (table séparée par tronçon)

---

## 🧪 Tester le comportement actuel

```bash
# Relancer le pipeline
python3 main.py
```

**Vous devriez voir** :
```
[Export métriques]
✓ Métriques bikes exportées vers MONGODB
✓ Métriques traffic exportées vers MONGODB
✓ Métriques weather exportées vers MONGODB
✓ Métriques chantiers exportées vers MONGODB
✗ Erreur export comptages (trop gros)
  → Sauvegarde locale: output/metrics/comptages_metrics_2025-11-03.json

[Génération rapport]
✓ Métriques bikes chargées depuis MONGODB
✓ Métriques traffic chargées depuis MONGODB
✓ Métriques weather chargées depuis MONGODB
✓ Métriques chantiers chargées depuis MONGODB
→ Fallback: métriques comptages chargées depuis fichier local  ← ✅
✓ Rapport généré avec succès
```

---

## 📊 Résumé

| Problème | Solution | Status |
|----------|----------|--------|
| Comptages > 16 MB | Fallback fichiers locaux | ✅ Implémenté |
| Clé `None` dans chantiers | Convertir en "Unknown" | ✅ Corrigé |
| Rapport échoue | Gestion comptages None + fallback | ✅ Corrigé |
| Chunks temporaires | Nettoyage automatique | ✅ Fonctionne |

**Tout fonctionne maintenant ! Le système s'adapte intelligemment aux limitations.** 🎉

---

## 🎓 Pour aller plus loin

- **MongoDB GridFS** : https://docs.mongodb.com/manual/core/gridfs/
- **DynamoDB Item Size** : https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html
- **Design Patterns** : Fallback Pattern, Circuit Breaker

