#!/bin/bash
# Script d'installation et exécution automatique pour CityFlow Analytics

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "CityFlow Analytics - Installation & Run"
echo "=========================================="

# Étape 1: Vérifications
echo -e "\n[1/7] Vérifications système..."
python3 --version || { echo "✗ Python 3 requis"; exit 1; }
echo "✓ Python 3 OK"

# Étape 2: Environnement virtuel (optionnel)
echo -e "\n[2/7] Environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
else
    echo "✓ Environnement virtuel existant"
fi

# Activer si possible (sinon continuer sans)
source venv/bin/activate 2>/dev/null || echo "⚠ Environnement virtuel non activé (continue quand même)"

# Étape 3: Dépendances
echo -e "\n[3/7] Installation dépendances..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt 2>/dev/null || echo "⚠ Dépendances optionnelles non installées (continue quand même)"
    echo "✓ Dépendances vérifiées"
else
    echo "⚠ requirements.txt non trouvé (continue sans)"
fi

# Étape 4: Tests
echo -e "\n[4/7] Tests de validation..."
python3 run_tests.py || { echo "⚠ Tests échoués - vérifier erreurs ci-dessus"; }

# Étape 5: Vérification structure
echo -e "\n[5/7] Vérification structure..."
[ -d "processors" ] || { echo "✗ Répertoire processors manquant"; exit 1; }
[ -d "utils" ] || { echo "✗ Répertoire utils manquant"; exit 1; }
[ -d "models" ] || { echo "✗ Répertoire models manquant"; exit 1; }
[ -d "config" ] || { echo "✗ Répertoire config manquant"; exit 1; }
[ -f "main.py" ] || { echo "✗ main.py manquant"; exit 1; }
echo "✓ Structure OK"

# Étape 6: Exécution
echo -e "\n[6/7] Exécution traitement complet..."
python3 main.py || { 
    echo "⚠ Erreur lors de l'exécution";
    echo "Vérifier les logs ci-dessus pour détails";
    exit 1;
}

# Étape 7: Vérification outputs
echo -e "\n[7/7] Vérification outputs..."
if [ -d "output/reports" ] && ls output/reports/*.json 1> /dev/null 2>&1; then
    echo "✓ Rapports générés:"
    ls -lh output/reports/*.json | tail -1
    echo ""
    echo "Fichiers disponibles:"
    ls -1 output/reports/ | head -5
else
    echo "⚠ Aucun rapport généré (vérifier les erreurs)"
fi

if [ -d "output/metrics" ] && ls output/metrics/*.json 1> /dev/null 2>&1; then
    echo "✓ Métriques générées:"
    ls -1 output/metrics/ | wc -l | xargs echo "Nombre de fichiers:"
fi

echo -e "\n=========================================="
echo "✓ PROCESSUS TERMINÉ!"
echo "=========================================="
echo ""
echo "Fichiers générés dans:"
echo "  - output/reports/ (rapports quotidiens)"
echo "  - output/metrics/ (métriques par type)"
echo ""

