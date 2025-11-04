# 🔧 Corrections Alertes de Congestion - Problèmes Identifiés et Résolus

## 📋 Problèmes Identifiés dans les Alertes

En analysant les alertes de congestion, plusieurs problèmes ont été détectés :

### ❌ Problème 1 : Alertes avec Débit = 0
**Exemple :**
```json
{
  "debit_horaire_moyen": 0.0,
  "debit_journalier_total": 0,
  "congestion_alerte": true,
  "taux_occupation_moyen": 83.17611,
  "etat_trafic_dominant": "BLOQUÉ"
}
```

**Cause :**
- Un tronçon peut avoir un taux d'occupation élevé (> 80%) mais un débit de 0
- Cela peut arriver si le capteur est défaillant ou si les données sont incohérentes
- Une alerte de congestion avec débit = 0 n'a pas de sens logique

**Solution :**
- ✅ **Filtrage automatique** : Exclusion des alertes avec `debit_journalier_total <= 0`
- ✅ Seules les alertes avec trafic réel sont conservées

---

### ❌ Problème 2 : `date = ""` (vide)
**Cause :**
- La date n'était pas remplie dans les alertes de congestion

**Solution :**
- ✅ La date est maintenant remplie dans `export_results()` pour toutes les alertes

---

### ❌ Problème 3 : `zone_fallback` manquant
**Exemple :**
```json
{
  "arrondissement": "75011",
  "zone_fallback": null  // ❌ Manquant
}
```

**Cause :**
- Les métriques avec arrondissement valide n'avaient pas toujours `zone_fallback`
- Incohérence dans les données

**Solution :**
- ✅ **Toujours ajouter `zone_fallback`** :
  - Si arrondissement connu : `"Arrondissement 75011"`
  - Sinon : utiliser zone depuis coordonnées ou quadrant
  - Dernier recours : `"Unknown"`

---

### ❌ Problème 4 : Doublons
**Exemple :**
- Plusieurs alertes pour le même `identifiant_arc: "1648"` avec des dates/heures différentes
- C'est normal car les données agrégeent plusieurs jours, mais il faudrait peut-être dédupliquer

**Note :** Ce n'est pas vraiment un problème, c'est normal d'avoir plusieurs alertes pour le même tronçon à des dates différentes. Mais on pourrait améliorer en regroupant par tronçon.

---

## ✅ Corrections Appliquées

### 1. Filtrage des Alertes Invalides

**Avant :**
```python
alertes = [
    m for m in metrics 
    if m.get("congestion_alerte", False)
]
# Incluait les alertes avec débit = 0
```

**Après :**
```python
# Filtrer : exclure les alertes avec débit = 0 (pas de sens logique)
alertes = [
    m for m in metrics 
    if m.get("congestion_alerte", False) 
    and m.get("debit_journalier_total", 0) > 0  # ✅ Ignorer débit = 0
]
```

**Résultat :**
- ✅ Plus d'alertes avec débit = 0
- ✅ Seules les alertes valides sont conservées

---

### 2. Garantie de `zone_fallback` Présent

**Avant :**
```python
# zone_fallback parfois absent
if zone_fallback:
    metric_dict["zone_fallback"] = zone_fallback
```

**Après :**
```python
# S'assurer que toutes les alertes ont zone_fallback
for alerte in alertes:
    if "zone_fallback" not in alerte:
        # Si arrondissement connu
        arr = alerte.get("arrondissement", "Unknown")
        if arr != "Unknown":
            alerte["zone_fallback"] = f"Arrondissement {arr}"
        else:
            # Détecter depuis coordonnées
            # ... logique de détection ...
            alerte["zone_fallback"] = zone or quadrant or "Unknown"
```

**Résultat :**
- ✅ `zone_fallback` est **toujours présent** dans toutes les alertes
- ✅ Format cohérent : `"Arrondissement 75011"` ou `"Nord"`, `"Sud-Est"`, etc.

---

### 3. Remplissage de la Date

**Avant :**
```python
# Date jamais remplie dans les alertes
```

**Après :**
```python
# Dans export_results()
if "alertes_congestion" in indicators:
    for alerte in indicators["alertes_congestion"]:
        if "date" in alerte and alerte["date"] == "":
            alerte["date"] = date  # ✅ Remplie automatiquement
```

**Résultat :**
- ✅ Toutes les alertes ont maintenant une date valide

---

### 4. Tri par Impact (Temps Perdu)

**Avant :**
```python
alertes = [m for m in metrics if m.get("congestion_alerte", False)]
# Ordre non défini
```

**Après :**
```python
# Trier par temps perdu total (zones les plus impactées en premier)
alertes = sorted(
    alertes,
    key=lambda x: x.get("temps_perdu_total_minutes", 0),
    reverse=True
)
```

**Résultat :**
- ✅ Les alertes sont triées par impact (temps perdu total)
- ✅ Les zones les plus congestionnées apparaissent en premier

---

## 📊 Résultats Attendus Après Correction

### Exemple d'Alerte Corrigée

**Avant :**
```json
{
  "arrondissement": "Unknown",
  "congestion_alerte": true,
  "date": "",
  "debit_journalier_total": 0,  // ❌ Débit = 0
  "temps_perdu_total_minutes": 0.0,
  "zone_fallback": null  // ❌ Manquant
}
```

**Après :**
```json
{
  "arrondissement": "Unknown",
  "congestion_alerte": true,
  "date": "2025-11-04",  // ✅ Date remplie
  "debit_journalier_total": 1996.0,  // ✅ Débit > 0 (filtré)
  "temps_perdu_total_minutes": 105.81,  // ✅ Calculé
  "zone_fallback": "Nord"  // ✅ Toujours présent
}
```

**Alerte avec arrondissement :**
```json
{
  "arrondissement": "75011",
  "congestion_alerte": true,
  "date": "2025-11-04",  // ✅ Date remplie
  "debit_journalier_total": 2318.0,
  "temps_perdu_total_minutes": 36.70,
  "zone_fallback": "Arrondissement 75011"  // ✅ Format cohérent
}
```

---

## 🎯 Analyse des Alertes Maintenant Possible

### 1. Identifier les Zones les Plus Impactées

```python
# Grouper alertes par zone
alertes_by_zone = {}
for alerte in alertes_congestion:
    zone = alerte.get("zone_fallback", "Unknown")
    if zone not in alertes_by_zone:
        alertes_by_zone[zone] = {
            "total_alertes": 0,
            "total_temps_perdu": 0,
            "troncons": set()
        }
    alertes_by_zone[zone]["total_alertes"] += 1
    alertes_by_zone[zone]["total_temps_perdu"] += alerte.get("temps_perdu_total_minutes", 0)
    alertes_by_zone[zone]["troncons"].add(alerte["libelle"])

# Trier par impact
for zone, stats in sorted(alertes_by_zone.items(), 
                         key=lambda x: x[1]["total_temps_perdu"], 
                         reverse=True):
    print(f"\nZone: {zone}")
    print(f"  Alertes: {stats['total_alertes']}")
    print(f"  Temps perdu total: {stats['total_temps_perdu']:,.0f} min")
    print(f"  Tronçons concernés: {len(stats['troncons'])}")
```

### 2. Analyser les Tronçons Récurrents

```python
# Tronçons avec le plus d'alertes
troncons_alertes = {}
for alerte in alertes_congestion:
    libelle = alerte["libelle"]
    if libelle not in troncons_alertes:
        troncons_alertes[libelle] = {
            "count": 0,
            "zone": alerte.get("zone_fallback"),
            "temps_perdu_total": 0
        }
    troncons_alertes[libelle]["count"] += 1
    troncons_alertes[libelle]["temps_perdu_total"] += alerte.get("temps_perdu_total_minutes", 0)

# Top 5 tronçons avec le plus d'alertes
top_troncons = sorted(
    troncons_alertes.items(),
    key=lambda x: x[1]["count"],
    reverse=True
)[:5]

for libelle, stats in top_troncons:
    print(f"{libelle} ({stats['zone']}): {stats['count']} alertes, "
          f"{stats['temps_perdu_total']:,.0f} min de temps perdu")
```

### 3. Détecter les Zones Critiques

```python
# Zones avec taux d'occupation très élevé (> 90%)
zones_critiques = [
    alerte for alerte in alertes_congestion
    if alerte.get("taux_occupation_moyen", 0) > 90
]

print(f"Zones critiques (taux > 90%): {len(zones_critiques)}")
for alerte in sorted(zones_critiques, 
                     key=lambda x: x.get("taux_occupation_moyen", 0), 
                     reverse=True)[:5]:
    print(f"  - {alerte['libelle']} ({alerte.get('zone_fallback')}): "
          f"{alerte.get('taux_occupation_moyen', 0):.1f}%")
```

---

## 📈 Statistiques sur les Alertes

### Exemple d'Analyse

```python
import json

# Charger les métriques
with open('output/metrics/comptages_metrics_2025-11-04.json', 'r') as f:
    data = json.load(f)

alertes = data.get('alertes_congestion', [])

print(f"Total alertes: {len(alertes)}")
print(f"Taux d'occupation moyen: {sum(a.get('taux_occupation_moyen', 0) for a in alertes) / len(alertes):.1f}%")
print(f"Temps perdu total: {sum(a.get('temps_perdu_total_minutes', 0) for a in alertes):,.0f} min")

# Par zone
by_zone = {}
for alerte in alertes:
    zone = alerte.get('zone_fallback', 'Unknown')
    by_zone[zone] = by_zone.get(zone, 0) + 1

print("\nAlertes par zone:")
for zone, count in sorted(by_zone.items(), key=lambda x: x[1], reverse=True):
    print(f"  {zone}: {count}")
```

---

## 🔍 Vérification des Corrections

### Test 1 : Vérifier que débit = 0 est exclu

```bash
python3 -c "
import json
with open('output/metrics/comptages_metrics_2025-11-04.json', 'r') as f:
    data = json.load(f)
    alertes = data.get('alertes_congestion', [])
    alertes_debit_zero = [a for a in alertes if a.get('debit_journalier_total', 0) == 0]
    print(f'Alertes avec débit = 0: {len(alertes_debit_zero)}')
    if len(alertes_debit_zero) > 0:
        print('❌ Il y a encore des alertes avec débit = 0')
    else:
        print('✅ Toutes les alertes ont un débit > 0')
"
```

### Test 2 : Vérifier que date est remplie

```bash
python3 -c "
import json
with open('output/metrics/comptages_metrics_2025-11-04.json', 'r') as f:
    data = json.load(f)
    alertes = data.get('alertes_congestion', [])
    alertes_sans_date = [a for a in alertes if not a.get('date') or a.get('date') == '']
    print(f'Alertes sans date: {len(alertes_sans_date)}')
    if len(alertes_sans_date) > 0:
        print('❌ Il y a encore des alertes sans date')
    else:
        print('✅ Toutes les alertes ont une date')
"
```

### Test 3 : Vérifier que zone_fallback est présent

```bash
python3 -c "
import json
with open('output/metrics/comptages_metrics_2025-11-04.json', 'r') as f:
    data = json.load(f)
    alertes = data.get('alertes_congestion', [])
    alertes_sans_zone = [a for a in alertes if 'zone_fallback' not in a]
    print(f'Alertes sans zone_fallback: {len(alertes_sans_zone)}')
    if len(alertes_sans_zone) > 0:
        print('❌ Il y a encore des alertes sans zone_fallback')
        for a in alertes_sans_zone[:3]:
            print(f'  - {a.get(\"libelle\")}: arrondissement={a.get(\"arrondissement\")}')
    else:
        print('✅ Toutes les alertes ont une zone_fallback')
"
```

---

## 📝 Résumé des Corrections

| Problème | Avant | Après | Impact |
|----------|-------|-------|--------|
| **Alertes débit = 0** | Incluses | Exclues | ✅ Alertes valides uniquement |
| **Date vide** | `date = ""` | Date remplie | ✅ Date présente |
| **zone_fallback manquant** | Parfois absent | Toujours présent | ✅ Analyse par zones possible |
| **Ordre non défini** | Aléatoire | Trié par impact | ✅ Zones critiques en premier |

---

## 🚀 Prochaines Étapes

1. **Relancer le traitement** :
   ```bash
   python3 main.py 2025-11-04
   ```

2. **Vérifier les alertes** :
   ```bash
   curl http://localhost:5001/metrics/comptages/2025-11-04 | jq '.data.alertes_congestion | length'
   ```

3. **Analyser les zones critiques** :
   ```bash
   curl http://localhost:5001/metrics/comptages/2025-11-04 | jq '.data.alertes_congestion | group_by(.zone_fallback) | map({zone: .[0].zone_fallback, count: length})'
   ```

---

## ✅ Conclusion

Tous les problèmes identifiés dans les alertes de congestion ont été corrigés :

1. ✅ **Filtrage** : Alertes avec débit = 0 exclues
2. ✅ **Date** : Remplie automatiquement
3. ✅ **zone_fallback** : Toujours présent avec format cohérent
4. ✅ **Tri** : Par temps perdu total (impact)

**Les alertes de congestion sont maintenant propres et analysables !** 🎉

