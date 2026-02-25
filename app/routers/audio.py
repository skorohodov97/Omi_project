from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.services.audio_service import save_audio

router = APIRouter(prefix="/data", tags=["audio"])


@router.post("/audio")
async def receive_audio(
    request: Request,
    device_id: UUID,
    sample_rate: int = 16000,
    db: Session = Depends(get_db)
):
    pcm_bytes = await request.body()

    if not pcm_bytes:
        raise HTTPException(400, "Empty audio")

    record = save_audio(device_id, pcm_bytes, sample_rate, db)

    return {
        "id": record.id,
        "file_path": record.file_path
    }