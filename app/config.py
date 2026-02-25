from pathlib import Path

DATABASE_URL = "postgresql://danil:123456@localhost:5432/postgres"

BASE_AUDIO_DIR = Path("data/audio")
BASE_RING_DIR = Path("data/ring")

LOG_DIR = Path("logs")

BASE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
BASE_RING_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)