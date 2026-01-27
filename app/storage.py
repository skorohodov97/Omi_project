from pathlib import Path
from datetime import datetime
from app.config import BASE_DATA_DIR

def save_wav(
    device_id: str,
    wav_bytes: bytes,
    timestamp: datetime
):
    date_dir = timestamp.strftime("%Y-%m-%d")
    time_name = timestamp.strftime("%H-%M-%S-%f")

    device_path = BASE_DATA_DIR / device_id / date_dir
    device_path.mkdir(parents=True, exist_ok=True)

    file_path = device_path / f"{time_name}.wav"
    with open(file_path, "wb") as f:
        f.write(wav_bytes)

    return file_path
