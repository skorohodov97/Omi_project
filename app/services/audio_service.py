from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AudioRecord
from app.config import BASE_AUDIO_DIR
from app.omi_audio import convert_ogg_opus_to_wav, opus_frames_to_ogg, parse_omi_opus_dump
from app.wav_utils import pcm_to_wav


def save_pcm_audio(
    device_id,
    pcm_bytes: bytes,
    sample_rate: int,
    channels: int,
    sample_width: int,
    db: Session
):
    timestamp = datetime.utcnow()

    wav_bytes = pcm_to_wav(pcm_bytes, sample_rate, channels, sample_width)

    device_folder = BASE_AUDIO_DIR / str(device_id)
    device_folder.mkdir(parents=True, exist_ok=True)

    file_name = f"{timestamp.timestamp()}.wav"
    file_path = device_folder / file_name

    with open(file_path, "wb") as f:
        f.write(wav_bytes)

    record = AudioRecord(
        device_id=device_id,
        file_path=str(file_path),
        sample_rate=sample_rate,
        channels=channels,
        sample_width=sample_width,
        duration_ms=int(len(pcm_bytes) / (sample_rate * channels * sample_width) * 1000)
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def save_omi_opus_audio(device_id, dump_bytes: bytes, sample_rate: int, db: Session):
    timestamp = datetime.utcnow()

    device_folder = BASE_AUDIO_DIR / str(device_id)
    device_folder.mkdir(parents=True, exist_ok=True)

    stem = str(timestamp.timestamp())
    bin_path = device_folder / f"{stem}.bin"
    opus_path = device_folder / f"{stem}.opus"
    wav_path = device_folder / f"{stem}.wav"

    with open(bin_path, "wb") as f:
        f.write(dump_bytes)

    frames = parse_omi_opus_dump(dump_bytes)
    opus_bytes = opus_frames_to_ogg(frames, sample_rate)
    with open(opus_path, "wb") as f:
        f.write(opus_bytes)

    wav_created = convert_ogg_opus_to_wav(opus_path, wav_path)
    file_path = wav_path if wav_created else opus_path

    record = AudioRecord(
        device_id=device_id,
        file_path=str(file_path),
        sample_rate=sample_rate,
        channels=1,
        sample_width=2 if wav_created else None,
        duration_ms=int(len(frames) * 160 / sample_rate * 1000)
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record, {
        "raw_path": str(bin_path),
        "opus_path": str(opus_path),
        "wav_path": str(wav_path) if wav_created else None,
        "wav_created": wav_created,
    }


save_audio = save_pcm_audio
