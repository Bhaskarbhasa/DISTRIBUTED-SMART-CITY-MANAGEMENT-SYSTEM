from minio import Minio
from minio.error import S3Error
from config import settings
import io
import json
from structlog import get_logger

logger = get_logger()

client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

def export_daily_summary(date_str: str, data: dict, bucket: str = "smartcity-analytics"):
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            
        json_data = json.dumps(data).encode("utf-8")
        client.put_object(
            bucket,
            f"daily_summary_{date_str}.json",
            data=io.BytesIO(json_data),
            length=len(json_data),
            content_type="application/json"
        )
        logger.info("Exported daily summary", date=date_str)
    except S3Error as e:
        logger.error("MinIO error", error=str(e))

def list_datasets(bucket: str = "smartcity-analytics"):
    try:
        objects = client.list_objects(bucket)
        return [{"name": obj.object_name, "size": obj.size, "last_modified": obj.last_modified} for obj in objects]
    except S3Error as e:
        logger.error("MinIO error", error=str(e))
        return []

def get_dataset_url(object_name: str, bucket: str = "smartcity-analytics"):
    try:
        return client.presigned_get_object(bucket, object_name)
    except S3Error as e:
        logger.error("MinIO error", error=str(e))
        return None
