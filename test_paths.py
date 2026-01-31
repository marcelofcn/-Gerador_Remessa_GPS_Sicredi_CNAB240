from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
print(f"Onde estou: {BASE_DIR}")
print(f"Input: {BASE_DIR / 'input'}")
print(f"Existe input? {(BASE_DIR / 'input').exists()}")
