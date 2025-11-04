"""
Services AWS : DynamoDB et S3
Utilisé pour stocker métriques et rapports
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("⚠ boto3 non disponible, utilisation mode simulation (local)")


class DynamoDBService:
    """Service pour interagir avec DynamoDB"""
    
    def __init__(self, table_name: str, region_name: Optional[str] = None):
        """
        Initialise le service DynamoDB
        
        Args:
            table_name: Nom de la table DynamoDB
            region_name: Région AWS (défaut: depuis env ou us-east-1)
        """
        self.table_name = table_name
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        
        if BOTO3_AVAILABLE:
            try:
                self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
                self.table = self.dynamodb.Table(table_name)
            except Exception as e:
                print(f"⚠ Erreur initialisation DynamoDB: {e}")
                self.table = None
        else:
            self.table = None
            print("⚠ Mode simulation DynamoDB (boto3 non disponible)")
    
    def put_item(self, item: Dict[str, Any]) -> bool:
        """
        Insère ou met à jour un élément dans DynamoDB
        
        Args:
            item: Élément à insérer (dict)
        
        Returns:
            True si succès
        """
        if not self.table:
            print(f"[SIMULATION] DynamoDB.put_item({self.table_name}): {json.dumps(item, default=str)[:100]}...")
            return True
        
        try:
            self.table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"✗ Erreur DynamoDB.put_item: {e}")
            return False
    
    def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Récupère un élément depuis DynamoDB
        
        Args:
            key: Clé primaire de l'élément
        
        Returns:
            Élément ou None
        """
        if not self.table:
            print(f"[SIMULATION] DynamoDB.get_item({self.table_name}, key={key})")
            return None
        
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            print(f"✗ Erreur DynamoDB.get_item: {e}")
            return None
    
    def query_by_date(self, date: str, date_field: str = "date") -> List[Dict[str, Any]]:
        """
        Interroge DynamoDB par date
        
        Args:
            date: Date au format YYYY-MM-DD
            date_field: Nom du champ date
        
        Returns:
            Liste des éléments
        """
        if not self.table:
            print(f"[SIMULATION] DynamoDB.query_by_date({self.table_name}, date={date})")
            return []
        
        try:
            from boto3.dynamodb.conditions import Key, Attr
            response = self.table.scan(
                FilterExpression=Attr(date_field).eq(date)
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"✗ Erreur DynamoDB.query_by_date: {e}")
            return []


class S3Service:
    """Service pour interagir avec S3"""
    
    def __init__(self, bucket_name: str, region_name: Optional[str] = None):
        """
        Initialise le service S3
        
        Args:
            bucket_name: Nom du bucket S3
            region_name: Région AWS (défaut: depuis env ou us-east-1)
        """
        self.bucket_name = bucket_name
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        
        if BOTO3_AVAILABLE:
            try:
                self.s3 = boto3.client("s3", region_name=self.region_name)
            except Exception as e:
                print(f"⚠ Erreur initialisation S3: {e}")
                self.s3 = None
        else:
            self.s3 = None
            print("⚠ Mode simulation S3 (boto3 non disponible)")
    
    def upload_file(self, local_path: str, s3_key: str, content_type: Optional[str] = None) -> bool:
        """
        Upload un fichier vers S3
        
        Args:
            local_path: Chemin local du fichier
            s3_key: Clé S3 (chemin dans le bucket)
            content_type: Type MIME (défaut: auto-détecté)
        
        Returns:
            True si succès
        """
        if not self.s3:
            print(f"[SIMULATION] S3.upload_file({self.bucket_name}/{s3_key})")
            return True
        
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            
            self.s3.upload_file(local_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            return True
        except ClientError as e:
            print(f"✗ Erreur S3.upload_file: {e}")
            return False
    
    def upload_bytes(self, data: bytes, s3_key: str, content_type: Optional[str] = None) -> bool:
        """
        Upload des données bytes vers S3
        
        Args:
            data: Données à uploader (bytes)
            s3_key: Clé S3 (chemin dans le bucket)
            content_type: Type MIME
        
        Returns:
            True si succès
        """
        if not self.s3:
            print(f"[SIMULATION] S3.upload_bytes({self.bucket_name}/{s3_key}, size={len(data)})")
            return True
        
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            
            self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=data, **extra_args)
            return True
        except ClientError as e:
            print(f"✗ Erreur S3.upload_bytes: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Télécharge un fichier depuis S3
        
        Args:
            s3_key: Clé S3
            local_path: Chemin local de destination
        
        Returns:
            True si succès
        """
        if not self.s3:
            print(f"[SIMULATION] S3.download_file({self.bucket_name}/{s3_key})")
            return False
        
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_path)
            return True
        except ClientError as e:
            print(f"✗ Erreur S3.download_file: {e}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Vérifie si un fichier existe dans S3
        
        Args:
            s3_key: Clé S3
        
        Returns:
            True si existe
        """
        if not self.s3:
            return False
        
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False


def save_metrics_to_dynamodb(metrics: Dict[str, Any], data_type: str, date: str, 
                             table_name: Optional[str] = None) -> bool:
    """
    Sauvegarde des métriques dans DynamoDB
    
    Args:
        metrics: Métriques à sauvegarder
        data_type: Type de données (bikes, traffic, etc.)
        date: Date au format YYYY-MM-DD
        table_name: Nom de la table (défaut: depuis env)
    
    Returns:
        True si succès
    """
    if not table_name:
        table_name = os.getenv("DYNAMODB_METRICS_TABLE", f"cityflow-{data_type}-metrics")
    
    service = DynamoDBService(table_name)
    
    # Préparer l'item DynamoDB
    item = {
        "metric_type": data_type,
        "date": date,
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "ttl": int((datetime.now().timestamp() + (365 * 24 * 3600)))  # TTL 1 an
    }
    
    return service.put_item(item)


def save_report_to_s3_csv(csv_content: str, date: str, bucket_name: Optional[str] = None,
                          s3_prefix: Optional[str] = None) -> bool:
    """
    Sauvegarde un rapport CSV dans S3
    
    Args:
        csv_content: Contenu CSV (string)
        date: Date au format YYYY-MM-DD
        bucket_name: Nom du bucket (défaut: depuis env)
        s3_prefix: Préfixe S3 (défaut: depuis env ou "reports/")
    
    Returns:
        True si succès
    """
    if not bucket_name:
        bucket_name = os.getenv("S3_REPORTS_BUCKET", "cityflow-reports")
    
    if not s3_prefix:
        s3_prefix = os.getenv("S3_REPORTS_PREFIX", "reports")
    
    s3_key = f"{s3_prefix}/daily_report_{date}.csv"
    service = S3Service(bucket_name)
    
    csv_bytes = csv_content.encode("utf-8")
    return service.upload_bytes(csv_bytes, s3_key, content_type="text/csv")


def save_report_to_dynamodb(report: Dict[str, Any], date: str,
                            table_name: Optional[str] = None) -> bool:
    """
    Sauvegarde un rapport dans DynamoDB
    
    Args:
        report: Rapport à sauvegarder (dict)
        date: Date au format YYYY-MM-DD
        table_name: Nom de la table (défaut: depuis env)
    
    Returns:
        True si succès
    """
    if not table_name:
        table_name = os.getenv("DYNAMODB_REPORTS_TABLE", "cityflow-daily-reports")
    
    service = DynamoDBService(table_name)
    
    # Préparer l'item DynamoDB
    item = {
        "report_id": f"daily_report_{date}",
        "date": date,
        "timestamp": datetime.now().isoformat(),
        "report": report,
        "ttl": int((datetime.now().timestamp() + (365 * 24 * 3600)))  # TTL 1 an
    }
    
    return service.put_item(item)


def load_metrics_from_dynamodb(data_type: str, date: str,
                               table_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Charge des métriques depuis DynamoDB
    
    Args:
        data_type: Type de données
        date: Date au format YYYY-MM-DD
        table_name: Nom de la table (défaut: depuis env)
    
    Returns:
        Métriques ou None
    """
    if not table_name:
        table_name = os.getenv("DYNAMODB_METRICS_TABLE", f"cityflow-{data_type}-metrics")
    
    service = DynamoDBService(table_name)
    item = service.get_item({"metric_type": data_type, "date": date})
    
    if item:
        return item.get("metrics")
    
    return None


def list_s3_files(bucket_name: str, prefix: str, extension: Optional[str] = None) -> List[str]:
    """
    Liste les fichiers dans un bucket S3 avec un préfixe donné
    
    Args:
        bucket_name: Nom du bucket S3
        prefix: Préfixe S3 (ex: "raw/api/bikes/")
        extension: Extension de fichier optionnelle (ex: ".json", ".csv")
    
    Returns:
        Liste des clés S3
    """
    service = S3Service(bucket_name)
    
    if not service.s3:
        print(f"[SIMULATION] S3.list_files({bucket_name}/{prefix})")
        return []
    
    try:
        response = service.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            return []
        
        files = [obj['Key'] for obj in response['Contents']]
        
        # Filtrer par extension si spécifiée
        if extension:
            files = [f for f in files if f.endswith(extension)]
        
        return files
    except ClientError as e:
        print(f"✗ Erreur S3.list_files: {e}")
        return []


def download_s3_file_to_temp(bucket_name: str, s3_key: str, local_dir: str) -> Optional[str]:
    """
    Télécharge un fichier depuis S3 vers un répertoire local temporaire
    
    Args:
        bucket_name: Nom du bucket S3
        s3_key: Clé S3 du fichier
        local_dir: Répertoire local de destination
    
    Returns:
        Chemin local du fichier téléchargé ou None si échec
    """
    service = S3Service(bucket_name)
    
    # Créer le répertoire local si nécessaire
    os.makedirs(local_dir, exist_ok=True)
    
    # Extraire le nom du fichier depuis la clé S3
    filename = os.path.basename(s3_key)
    local_path = os.path.join(local_dir, filename)
    
    # Télécharger le fichier
    if service.download_file(s3_key, local_path):
        print(f"✓ Téléchargé depuis S3: {s3_key} → {local_path}")
        return local_path
    else:
        print(f"✗ Échec téléchargement S3: {s3_key}")
        return None


def download_s3_directory(bucket_name: str, s3_prefix: str, local_dir: str, 
                          extensions: Optional[List[str]] = None) -> List[str]:
    """
    Télécharge tous les fichiers d'un "répertoire" S3 vers un répertoire local
    
    Args:
        bucket_name: Nom du bucket S3
        s3_prefix: Préfixe S3 (ex: "raw/api/bikes/dt=2025-11-04/")
        local_dir: Répertoire local de destination
        extensions: Liste des extensions à télécharger (ex: [".json", ".csv"])
    
    Returns:
        Liste des chemins locaux des fichiers téléchargés
    """
    # Lister les fichiers S3
    all_files = list_s3_files(bucket_name, s3_prefix)
    
    # Filtrer par extensions si spécifiées
    if extensions:
        files_to_download = [f for f in all_files if any(f.endswith(ext) for ext in extensions)]
    else:
        files_to_download = all_files
    
    # Télécharger chaque fichier
    downloaded_files = []
    for s3_key in files_to_download:
        local_path = download_s3_file_to_temp(bucket_name, s3_key, local_dir)
        if local_path:
            downloaded_files.append(local_path)
    
    print(f"✓ {len(downloaded_files)} fichiers téléchargés depuis S3://{bucket_name}/{s3_prefix}")
    
    return downloaded_files


def load_json_from_s3(bucket_name: str, s3_key: str) -> Optional[Dict[str, Any]]:
    """
    Charge un fichier JSON directement depuis S3 (sans téléchargement local)
    
    Args:
        bucket_name: Nom du bucket S3
        s3_key: Clé S3 du fichier JSON
    
    Returns:
        Données JSON ou None
    """
    service = S3Service(bucket_name)
    
    if not service.s3:
        print(f"[SIMULATION] S3.load_json({bucket_name}/{s3_key})")
        return None
    
    try:
        response = service.s3.get_object(Bucket=bucket_name, Key=s3_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except ClientError as e:
        print(f"✗ Erreur S3.load_json: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Erreur JSON decode: {e}")
        return None

