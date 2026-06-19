from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.omi_audio import OmiAudioError
from app.services.audio_service import save_omi_opus_audio, save_pcm_audio

router = APIRouter(prefix="/data", tags=["audio"])


@router.post("/audio")
async def receive_audio(
    request: Request,
    device_id: UUID,
    sample_rate: int = 16000,
    channels: int = 1,
    sample_width: int = 2,
    db: Session = Depends(get_db)
):
    pcm_bytes = await request.body()

    if not pcm_bytes:
        raise HTTPException(400, "Empty audio")

    if channels not in (1, 2):
        raise HTTPException(400, "channels must be 1 or 2")

    if sample_width != 2:
        raise HTTPException(400, "Only PCM16 sample_width=2 is supported")

    if len(pcm_bytes) % (channels * sample_width) != 0:
        raise HTTPException(400, "PCM byte length does not match channels/sample_width")

    record = save_pcm_audio(device_id, pcm_bytes, sample_rate, channels, sample_width, db)

    return {
        "id": record.id,
        "file_path": record.file_path
    }


@router.post("/audio/omi-opus")
async def receive_omi_opus_audio(
    request: Request,
    device_id: UUID,
    sample_rate: int = 16000,
    codec: int = 20,
    db: Session = Depends(get_db)
):
    dump_bytes = await request.body()

    if not dump_bytes:
        raise HTTPException(400, "Empty audio")

    if codec != 20:
        raise HTTPException(400, "Only Omi Opus codec=20 is supported")

    try:
        record, files = save_omi_opus_audio(device_id, dump_bytes, sample_rate, db)
    except OmiAudioError as exc:
        raise HTTPException(400, str(exc)) from exc

    return {
        "id": record.id,
        "file_path": record.file_path,
        **files
    }
