#!/bin/bash
# Script pour corriger le bug Float → Decimal sur EC2

echo "🔧 Correction du bug Float → Decimal dans aws_services.py"

# Aller dans le répertoire du projet
cd ~/cityflow2/utils

# Créer un backup
cp aws_services.py aws_services.py.backup
echo "✓ Backup créé: aws_services.py.backup"

# Ajouter la fonction convert_floats_to_decimal après les imports
# Chercher la ligne après "from typing import" et insérer la fonction

cat > /tmp/convert_function.txt << 'EOF'

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

EOF

# Chercher si la fonction existe déjà
if grep -q "def convert_floats_to_decimal" aws_services.py; then
    echo "✓ La fonction convert_floats_to_decimal existe déjà"
else
    echo "📝 Ajout de la fonction convert_floats_to_decimal..."
    
    # Trouver la ligne après les imports et insérer la fonction
    # On va l'insérer après la ligne qui contient "from typing import"
    
    awk '
    /^from typing import/ {
        print;
        getline;
        print;
        system("cat /tmp/convert_function.txt");
        next;
    }
    {print}
    ' aws_services.py > aws_services.py.new
    
    mv aws_services.py.new aws_services.py
    echo "✓ Fonction ajoutée"
fi

# Vérifier si convert_floats_to_decimal est appelé dans save_metrics_to_dynamodb
if grep -q "metrics_converted = convert_floats_to_decimal(metrics)" aws_services.py; then
    echo "✓ L'appel à convert_floats_to_decimal existe déjà dans save_metrics_to_dynamodb"
else
    echo "📝 Ajout de l'appel à convert_floats_to_decimal dans save_metrics_to_dynamodb..."
    
    # Modifier la fonction save_metrics_to_dynamodb pour convertir les floats
    sed -i '/service = DynamoDBService(table_name)/a\    \n    # Convertir tous les floats en Decimal pour DynamoDB\n    metrics_converted = convert_floats_to_decimal(metrics)' aws_services.py
    
    # Remplacer "metrics" par "metrics_converted" dans l'item
    sed -i 's/"metrics": metrics/"metrics": metrics_converted/g' aws_services.py
    
    echo "✓ Appel ajouté"
fi

# Vérifier si convert_floats_to_decimal est appelé dans save_report_to_dynamodb
if grep -q "report_converted = convert_floats_to_decimal(report)" aws_services.py; then
    echo "✓ L'appel à convert_floats_to_decimal existe déjà dans save_report_to_dynamodb"
else
    echo "📝 Ajout de l'appel à convert_floats_to_decimal dans save_report_to_dynamodb..."
    
    # Modifier la fonction save_report_to_dynamodb pour convertir les floats
    sed -i '/def save_report_to_dynamodb/,/service = DynamoDBService(table_name)/ {
        /service = DynamoDBService(table_name)/a\    \n    # Convertir tous les floats en Decimal pour DynamoDB\n    report_converted = convert_floats_to_decimal(report)
    }' aws_services.py
    
    # Remplacer "report" par "report_converted" dans l'item
    sed -i 's/"report": report/"report": report_converted/g' aws_services.py
    
    echo "✓ Appel ajouté"
fi

echo ""
echo "✅ Correction terminée !"
echo ""
echo "🧪 Pour tester :"
echo "   cd ~/cityflow2"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "📋 En cas de problème, restaurer le backup :"
echo "   cp ~/cityflow2/utils/aws_services.py.backup ~/cityflow2/utils/aws_services.py"

