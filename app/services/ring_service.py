from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import RingRecord
from app.config import BASE_RING_DIR


def save_ring_file(device_id, file_bytes: bytes, db: Session):

    timestamp = datetime.utcnow()

    # создаём папку device/date
    device_folder = BASE_RING_DIR / str(device_id)
    device_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{timestamp.timestamp()}.bin"
    file_path = device_folder / filename

    # сохраняем файл
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    record = RingRecord(
        device_id=device_id,
        file_path=str(file_path),
        file_size=len(file_bytes),
        created_at=timestamp
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record