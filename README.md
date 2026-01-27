# geraremessa
Copiar o arquivo .env.exemplo para o .env
```shell
cp .env.exemplo .env

```
# Ajuste de caminhos
```shell
BASE_DIR = "opt/gps-remessa"
```
mudar para novo caminho
```shell
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = f"{BASE_DIR}/input"
OUTPUT_DIR = f"{BASE_DIR}/output"
PROCESSED_DIR = f"{BASE_DIR}/processed"
NSA_FILE = f"{BASE_DIR}/nsa.txt"

```
# INSTALL.md:
# Instruções de Instalação
1. Criar venv
```shell
python3 -m venv venv
```
2. Ativar venv
```shell
source venv/bin/activate

```
3. Instalar
```shell
pip install -r requirements.txt

```