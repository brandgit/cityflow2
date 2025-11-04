#!/usr/bin/env python3
"""
Script de test automatique pour CityFlow Analytics
"""

import sys
from pathlib import Path

def test_imports():
    """Test 1: Imports"""
    print("\n[TEST 1] Vérification imports...")
    try:
        from processors import BikesProcessor, TrafficProcessor
        from utils import validators, aggregators
        from models import TrafficMetrics
        from config import settings
        print("  ✓ Tous les imports réussis")
        return True
    except Exception as e:
        print(f"  ✗ Erreur import: {e}")
        return False

def test_configuration():
    """Test 2: Configuration"""
    print("\n[TEST 2] Vérification configuration...")
    try:
        from config import settings
        assert settings.CHUNK_SIZE > 0
        assert settings.OUTPUT_DIR is not None
        print(f"  ✓ Configuration valide (CHUNK_SIZE={settings.CHUNK_SIZE})")
        return True
    except Exception as e:
        print(f"  ✗ Erreur config: {e}")
        return False

def test_validators():
    """Test 3: Validators"""
    print("\n[TEST 3] Test validators...")
    try:
        from utils.validators import validate_coordinates, validate_date_iso
        
        assert validate_coordinates(2.3522, 48.8566) == True
        assert validate_coordinates(200, 100) == False
        
        date = validate_date_iso("2025-11-03T02:00:00+01:00")
        assert date is not None
        
        print("  ✓ Validators fonctionnent")
        return True
    except Exception as e:
        print(f"  ✗ Erreur validators: {e}")
        return False

def test_aggregators():
    """Test 4: Aggregators"""
    print("\n[TEST 4] Test aggregators...")
    try:
        from utils.aggregators import calculate_daily_total
        
        test_data = [{"count": 10}, {"count": 20}]
        total = calculate_daily_total(test_data, "count")
        assert total == 30.0
        
        print("  ✓ Aggregators fonctionnent")
        return True
    except Exception as e:
        print(f"  ✗ Erreur aggregators: {e}")
        return False

def test_traffic_calculations():
    """Test 5: Calculs trafic"""
    print("\n[TEST 5] Test calculs trafic...")
    try:
        from utils.traffic_calculations import calculate_lost_time
        
        temps_perdu, temps_total = calculate_lost_time(
            debit_horaire=1000,
            taux_occupation=50,
            longueur_metres=1000
        )
        
        assert temps_perdu >= 0
        assert temps_total >= 0
        
        print(f"  ✓ Calcul temps perdu: {temps_perdu:.2f} min")
        return True
    except Exception as e:
        print(f"  ✗ Erreur calculs trafic: {e}")
        return False

def test_processors():
    """Test 6: Processeurs"""
    print("\n[TEST 6] Test processeurs...")
    try:
        from processors import WeatherProcessor
        
        # Test données minimales
        weather_data = {
            "days": [{
                "datetime": "2025-11-03",
                "tempmax": 15.0,
                "tempmin": 10.0,
                "temp": 12.5,
                "precip": 0.0,
                "windspeed": 10.0,
                "conditions": "Clear"
            }]
        }
        
        processor = WeatherProcessor()
        result = processor.process(weather_data)
        
        assert result.get("success") == True
        
        print("  ✓ Processeur Weather fonctionne")
        return True
    except Exception as e:
        print(f"  ✗ Erreur processeurs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_output_directories():
    """Test 7: Répertoires output"""
    print("\n[TEST 7] Vérification répertoires output...")
    try:
        from config import settings
        
        # Vérifier création automatique
        assert settings.OUTPUT_DIR.exists()
        assert settings.METRICS_DIR.exists()
        assert settings.REPORTS_DIR.exists()
        
        print("  ✓ Répertoires output créés")
        return True
    except Exception as e:
        print(f"  ✗ Erreur répertoires: {e}")
        return False

def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("CityFlow Analytics - Suite de Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_validators,
        test_aggregators,
        test_traffic_calculations,
        test_processors,
        test_output_directories
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("✓ TOUS LES TESTS RÉUSSIS!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) échoué(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())

