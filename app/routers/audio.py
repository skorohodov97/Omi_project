from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app import models
from app.omi_audio import OmiAudioError
from app.services.audio_service import save_omi_opus_audio, save_pcm_audio
from app.services.analysis_service import transcript_russian

router = APIRouter(prefix="/data", tags=["audio"])


@router.post("/audio")
async def receive_audio(
    request: Request,
    device_id: UUID,
    session_id: UUID | None = None,
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

    record = save_pcm_audio(device_id, pcm_bytes, sample_rate, channels, sample_width, db, session_id)
    record.transcript_text, _ = transcript_russian(record.file_path)
    db.commit()

    return {
        "id": record.id,
        "file_path": record.file_path
    }


@router.post("/audio/omi-opus")
async def receive_omi_opus_audio(
    request: Request,
    device_id: UUID,
    session_id: UUID | None = None,
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
        record, files = save_omi_opus_audio(device_id, dump_bytes, sample_rate, db, session_id)
    except OmiAudioError as exc:
        raise HTTPException(400, str(exc)) from exc

    text, asr_note = transcript_russian(files.get("wav_path"))
    record.transcript_text = text
    if files.get("wav_path"):
        transcript_path = Path(files["wav_path"]).with_suffix(".txt")
        transcript_path.write_text(text or asr_note, encoding="utf-8")
        record.transcript_path = str(transcript_path)
    db.commit()

    return {
        "id": record.id,
        "file_path": record.file_path,
        **files
    }


@router.get("/audio/device/{device_id}/files")
def get_audio_files_by_device(device_id: UUID, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()

    if not device:
        raise HTTPException(404, "Device not found")

    records = db.query(models.AudioRecord).filter(
        models.AudioRecord.device_id == device_id
    ).order_by(models.AudioRecord.created_at.desc()).all()

    return [
        {
            "id": record.id,
            "file_name": Path(record.file_path).name,
            "created_at": record.created_at
        }
        for record in records
    ]


@router.get("/audio/files/{record_id}/download", response_class=FileResponse)
def download_audio_file(record_id: UUID, db: Session = Depends(get_db)):
    record = db.query(models.AudioRecord).filter(models.AudioRecord.id == record_id).first()

    if not record:
        raise HTTPException(404, "Audio file not found")

    file_path = Path(record.file_path)

    if file_path.suffix.lower() != ".wav":
        raise HTTPException(400, "Only .wav audio files can be downloaded")

    if not file_path.is_file():
        raise HTTPException(404, "File is missing on disk")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="audio/wav"
    )
