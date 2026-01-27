from io import BytesIO
from app.infra.minio_client import get_minio_client


def salvar_cnab_minio(
    bucket: str,
    nome_arquivo: str,
    conteudo: str
):
    client = get_minio_client()

    data = conteudo.encode("ascii")

    client.put_object(
        bucket_name=bucket,
        object_name=nome_arquivo,
        data=BytesIO(data),
        length=len(data),
        content_type="text/plain"
    )
