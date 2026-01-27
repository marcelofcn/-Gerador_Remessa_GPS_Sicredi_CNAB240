from minio import Minio
from minio.error import S3Error


def get_minio_client() -> Minio:
    return Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )


def garantir_bucket(bucket_name: str):
    client = get_minio_client()

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
