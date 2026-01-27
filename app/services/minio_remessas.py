from minio import Minio
from datetime import datetime
import os

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET = "remessas-cnab"

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

def garantir_bucket():
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)

def salvar_cnab(conteudo: str, banco: str) -> str:
    garantir_bucket()

    agora = datetime.now()
    ano = agora.strftime("%Y")
    mes = agora.strftime("%m")
    data = agora.strftime("%Y%m%d")
    seq = "000001"  # futuramente incremental

    nome_arquivo = f"{banco}_{data}_{seq}.REM"
    caminho = f"{banco}/{ano}/{mes}/{nome_arquivo}"

    arquivo_local = f"/tmp/{nome_arquivo}"
    with open(arquivo_local, "w", encoding="ascii", newline="\r\n") as f:
        f.write(conteudo)

    client.fput_object(
        BUCKET,
        caminho,
        arquivo_local,
        content_type="text/plain"
    )

    return caminho
