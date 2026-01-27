from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from app.wav_utils import pcm_to_wav
from app.storage import save_wav

router = APIRouter()

@router.post("/audio/stream")
async def receive_audio(
    request: Request,
    uid: str,
    sample_rate: int = 16000
):
    device_id = uid
    if not device_id:
        raise HTTPException(400, "device_id missing")

    pcm_bytes = await request.body()
    print("AUDIO CHUNK:", len(pcm_bytes), "bytes; query=", dict(request.query_params))
    if not pcm_bytes:
        raise HTTPException(400, "empty audio chunk")

    timestamp = datetime.utcnow()

    wav_bytes = pcm_to_wav(
        pcm_bytes,
        sample_rate=sample_rate
    )

    save_wav(
        device_id=device_id,
        wav_bytes=wav_bytes,
        timestamp=timestamp
    )

    return {"status": "ok"}


@router.get("/health")
def health():
    return {"ok": True}
