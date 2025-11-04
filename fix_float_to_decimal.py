#!/usr/bin/env python3
"""
Script pour corriger le bug Float → Decimal dans aws_services.py sur EC2
Exécuter avec: python3 fix_float_to_decimal.py
"""

import os
import sys
from pathlib import Path

def fix_aws_services():
    """Corrige le fichier aws_services.py pour ajouter la conversion Float → Decimal"""
    
    # Chemin du fichier
    file_path = Path("utils/aws_services.py")
    
    if not file_path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        print("💡 Assurez-vous d'être dans le répertoire ~/cityflow2")
        sys.exit(1)
    
    # Lire le contenu actuel
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la correction est déjà appliquée
    if 'def convert_floats_to_decimal' in content:
        print("✅ La fonction convert_floats_to_decimal existe déjà !")
        
        # Vérifier si elle est utilisée
        if 'metrics_converted = convert_floats_to_decimal(metrics)' in content:
            print("✅ La fonction est déjà appelée dans save_metrics_to_dynamodb")
            print("✅ Aucune correction nécessaire !")
            return
        else:
            print("⚠️  La fonction existe mais n'est pas utilisée, correction...")
    
    # Faire un backup
    backup_path = file_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup créé: {backup_path}")
    
    # Ajouter la fonction si elle n'existe pas
    if 'def convert_floats_to_decimal' not in content:
        print("📝 Ajout de la fonction convert_floats_to_decimal...")
        
        # Trouver où insérer (après les imports)
        function_code = '''

def convert_floats_to_decimal(obj):
    """
    Convertit récursivement tous les floats en Decimal pour DynamoDB
    
    Args:
        obj: Objet Python (dict, list, float, etc.)
    
    Returns:
        Objet avec floats convertis en Decimal
    """
    from decimal import Decimal
    
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

'''
        
        # Insérer après les imports (chercher la première classe ou fonction)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('class ') or (line.startswith('def ') and not line.startswith('def __')):
                insert_index = i
                break
        
        lines.insert(insert_index, function_code)
        content = '\n'.join(lines)
        print("✓ Fonction ajoutée")
    
    # Corriger save_metrics_to_dynamodb
    if 'metrics_converted = convert_floats_to_decimal(metrics)' not in content:
        print("📝 Correction de save_metrics_to_dynamodb...")
        
        # Remplacer dans la fonction save_metrics_to_dynamodb
        content = content.replace(
            '    service = DynamoDBService(table_name)\n    \n    # Préparer l\'item DynamoDB\n    item = {\n        "metric_type": data_type,\n        "date": date,\n        "timestamp": datetime.now().isoformat(),\n        "metrics": metrics,',
            '    service = DynamoDBService(table_name)\n    \n    # Convertir tous les floats en Decimal pour DynamoDB\n    metrics_converted = convert_floats_to_decimal(metrics)\n    \n    # Préparer l\'item DynamoDB\n    item = {\n        "metric_type": data_type,\n        "date": date,\n        "timestamp": datetime.now().isoformat(),\n        "metrics": metrics_converted,'
        )
        
        print("✓ save_metrics_to_dynamodb corrigé")
    
    # Corriger save_report_to_dynamodb
    if 'report_converted = convert_floats_to_decimal(report)' not in content:
        print("📝 Correction de save_report_to_dynamodb...")
        
        content = content.replace(
            '    service = DynamoDBService(table_name)\n    \n    # Préparer l\'item DynamoDB\n    item = {\n        "date": date,\n        "timestamp": datetime.now().isoformat(),\n        "report": report,',
            '    service = DynamoDBService(table_name)\n    \n    # Convertir tous les floats en Decimal pour DynamoDB\n    report_converted = convert_floats_to_decimal(report)\n    \n    # Préparer l\'item DynamoDB\n    item = {\n        "date": date,\n        "timestamp": datetime.now().isoformat(),\n        "report": report_converted,'
        )
        
        print("✓ save_report_to_dynamodb corrigé")
    
    # Écrire le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("")
    print("✅ Correction appliquée avec succès !")
    print("")
    print("🧪 Pour tester :")
    print("   python3 main.py")
    print("")
    print("📋 En cas de problème, restaurer le backup :")
    print(f"   cp {backup_path} {file_path}")


if __name__ == "__main__":
    print("🔧 Correction du bug Float → Decimal pour DynamoDB")
    print("=" * 60)
    print("")
    
    fix_aws_services()

