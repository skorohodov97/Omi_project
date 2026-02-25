from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.services.ring_service import save_ring_file
from app import models

router = APIRouter(prefix="/data", tags=["ring"])


@router.post("/ring")
async def receive_ring(
    request: Request,
    device_id: UUID,
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

    record = save_ring_file(device_id, file_bytes, db)

    return {
        "id": record.id,
        "file_path": record.file_path,
        "file_size": record.file_size
    }