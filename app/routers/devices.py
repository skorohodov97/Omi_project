from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import BASE_AUDIO_DIR, BASE_RING_DIR
from app.db import get_db
from app.models import AudioRecord, Device, RingRecord
from app.schemas import DeviceCreate
from datetime import datetime

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register")
def register_device(data: DeviceCreate, db: Session = Depends(get_db)):
    device = Device(
        name=data.name,
        created_at=datetime.utcnow()
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return {
        "id": device.id,
        "name": device.name,
        "created_at": device.created_at
    }

@router.get("/")
def get_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()

    return [
        {
            "id": d.id,
            "name": d.name,
            "created_at": d.created_at
        }
        for d in devices
    ]


@router.get("/by-name/{name}")
def get_device_ids_by_name(name: str, db: Session = Depends(get_db)):
    devices = db.query(Device).filter(Device.name == name).all()

    return {
        "name": name,
        "ids": [device.id for device in devices]
    }


@router.delete("/{device_id}")
def delete_device(device_id: UUID, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(404, "Device not found")

    db.delete(device)
    db.commit()

    return {
        "deleted": True,
        "device_id": device_id
    }


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _delete_record_file(file_path: str, allowed_root: Path) -> bool:
    path = Path(file_path)
    resolved_path = path.resolve()
    resolved_root = allowed_root.resolve()

    if not _is_relative_to(resolved_path, resolved_root):
        return False

    if not resolved_path.is_file():
        return False

    resolved_path.unlink()
    return True


def _delete_audio_record_files(file_path: str) -> tuple[list[str], list[str]]:
    path = Path(file_path)
    candidates = [path]

    if path.suffix in {".bin", ".opus", ".wav"}:
        candidates = [path.with_suffix(suffix) for suffix in (".bin", ".opus", ".wav")]

    deleted_files = []
    skipped_files = []

    for candidate in candidates:
        if _delete_record_file(str(candidate), BASE_AUDIO_DIR):
            deleted_files.append(str(candidate))
        else:
            skipped_files.append(str(candidate))

    return deleted_files, skipped_files


@router.delete("/{device_id}/with-files")
def delete_device_with_files(device_id: UUID, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(404, "Device not found")

    audio_records = db.query(AudioRecord).filter(AudioRecord.device_id == device_id).all()
    ring_records = db.query(RingRecord).filter(RingRecord.device_id == device_id).all()
    audio_file_paths = [record.file_path for record in audio_records]
    ring_file_paths = [record.file_path for record in ring_records]

    db.delete(device)
    db.commit()

    deleted_files = []
    skipped_files = []

    for file_path in audio_file_paths:
        deleted_audio_files, skipped_audio_files = _delete_audio_record_files(file_path)
        deleted_files.extend(deleted_audio_files)
        skipped_files.extend(skipped_audio_files)

    for file_path in ring_file_paths:
        if _delete_record_file(file_path, BASE_RING_DIR):
            deleted_files.append(file_path)
        else:
            skipped_files.append(file_path)

    return {
        "deleted": True,
        "device_id": device_id,
        "deleted_files": deleted_files,
        "skipped_files": skipped_files
    }
