from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import AudioRecord
from app.config import BASE_AUDIO_DIR
from app.wav_utils import pcm_to_wav


def save_audio(device_id, pcm_bytes, sample_rate: int, db: Session):
    timestamp = datetime.utcnow()

    wav_bytes = pcm_to_wav(pcm_bytes, sample_rate)

    device_folder = BASE_DATA_DIR / str(device_id)
    device_folder.mkdir(parents=True, exist_ok=True)

    file_name = f"{timestamp.timestamp()}.wav"
    file_path = device_folder / file_name

    with open(file_path, "wb") as f:
        f.write(wav_bytes)

    record = AudioRecord(
        device_id=device_id,
        file_path=str(file_path),
        sample_rate=sample_rate
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record