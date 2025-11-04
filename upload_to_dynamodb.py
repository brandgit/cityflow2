#!/usr/bin/env python3
"""
Script simple pour uploader les fichiers JSON locaux vers DynamoDB
"""

import json
import sys
from pathlib import Path
from decimal import Decimal

# Ajouter le projet au path
sys.path.insert(0, str(Path(__file__).parent))

from utils.aws_services import save_metrics_to_dynamodb, save_report_to_dynamodb


def upload_metrics(date="2025-11-04"):
    """Upload tous les fichiers métriques vers DynamoDB"""
    
    metrics_dir = Path("output/metrics")
    
    if not metrics_dir.exists():
        print(f"❌ Répertoire {metrics_dir} n'existe pas")
        return 0
    
    # Types de métriques
    metric_types = ["bikes", "traffic", "weather", "comptages", "chantiers", "referentiel"]
    
    uploaded = 0
    
    for metric_type in metric_types:
        filename = f"{metric_type}_metrics_{date}.json"
        file_path = metrics_dir / filename
        
        if not file_path.exists():
            print(f"⚠️  Fichier ignoré (non trouvé): {filename}")
            continue
        
        try:
            print(f"📥 Chargement {filename}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            print(f"📤 Upload vers DynamoDB (table: cityflow-metrics)...")
            success = save_metrics_to_dynamodb(
                metrics=metrics,
                data_type=metric_type,
                date=date
            )
            
            if success:
                uploaded += 1
                print(f"✅ {metric_type} → DynamoDB OK\n")
            else:
                print(f"❌ Erreur upload {metric_type}\n")
        
        except Exception as e:
            print(f"❌ Erreur {filename}: {e}\n")
    
    return uploaded


def upload_report(date="2025-11-04"):
    """Upload le rapport quotidien vers DynamoDB"""
    
    report_path = Path(f"output/reports/daily_report_{date}.json")
    
    if not report_path.exists():
        print(f"⚠️  Rapport non trouvé: {report_path}")
        return False
    
    try:
        print(f"📥 Chargement rapport {date}...")
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"📤 Upload vers DynamoDB (table: cityflow-daily-reports)...")
        success = save_report_to_dynamodb(
            report=report,
            date=date
        )
        
        if success:
            print(f"✅ Rapport → DynamoDB OK")
            return True
        else:
            print(f"❌ Erreur upload rapport")
            return False
    
    except Exception as e:
        print(f"❌ Erreur rapport: {e}")
        return False


if __name__ == "__main__":
    # Date depuis argument ou par défaut
    date = sys.argv[1] if len(sys.argv) > 1 else "2025-11-04"
    
    print("\n" + "="*60)
    print(f"📤 Upload fichiers JSON → DynamoDB")
    print(f"📅 Date: {date}")
    print("="*60 + "\n")
    
    # Upload métriques
    print("📊 MÉTRIQUES")
    print("-"*60)
    uploaded_metrics = upload_metrics(date=date)
    
    print("\n" + "="*60)
    print(f"✅ {uploaded_metrics} fichiers métriques uploadés")
    print("="*60 + "\n")
    
    # Upload rapport
    print("📄 RAPPORT QUOTIDIEN")
    print("-"*60)
    uploaded_report = upload_report(date=date)
    
    print("\n" + "="*60)
    print("🎉 Upload terminé !")
    print("="*60)

