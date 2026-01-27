from pathlib import Path

BASE_DATA_DIR = Path("data/raw_audio")
LOG_DIR = Path("logs")

BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
