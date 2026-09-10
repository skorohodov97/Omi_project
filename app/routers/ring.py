from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.services.ring_service import save_ring_file
from app import models
from app.services.analysis_service import decode_colmi_r10

router = APIRouter(prefix="/data", tags=["ring"])


@router.post("/ring")
async def receive_ring(
    request: Request,
    device_id: UUID,
    session_id: UUID | None = None,
    db: Session = Depends(get_db)
):
    # проверяем устройство
    device = db.query(models.Device).filter(
        models.Device.id == device_id
    ).first()

    if not device:
        raise HTTPException(404, "Device not found")

    # читаем бинарные данные
    file_bytes = await request.body()

    if not file_bytes:
        raise HTTPException(400, "Empty ring file")

    if session_id and not db.get(models.RecordingSession, session_id):
        raise HTTPException(404, "Session not found")
    record = save_ring_file(device_id, file_bytes, db, session_id)
    decode_colmi_r10(file_bytes, record.id, record.created_at, db)
    db.commit()

    return {
        "id": record.id,
        "file_path": record.file_path,
        "file_size": record.file_size
    }


@router.get("/ring/device/{device_id}/files")
def get_ring_files_by_device(device_id: UUID, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()

    if not device:
        raise HTTPException(404, "Device not found")

    records = db.query(models.RingRecord).filter(
        models.RingRecord.device_id == device_id
    ).order_by(models.RingRecord.created_at.desc()).all()

    return [
        {
            "id": record.id,
            "file_name": Path(record.file_path).name,
            "created_at": record.created_at
        }
        for record in records
    ]


@router.get("/ring/files/{record_id}/download", response_class=FileResponse)
def download_ring_file(record_id: UUID, db: Session = Depends(get_db)):
    record = db.query(models.RingRecord).filter(models.RingRecord.id == record_id).first()

    if not record:
        raise HTTPException(404, "Ring file not found")

    file_path = Path(record.file_path)

    if not file_path.is_file():
        raise HTTPException(404, "File is missing on disk")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )
