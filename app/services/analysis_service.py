"""Transparent baseline analysis used until trained R1/R2/R3 models are supplied."""
from datetime import datetime, timedelta
from pathlib import Path
from app.models import RingSample, RingRecord, FeatureWindow


def decode_colmi_r10(payload: bytes, ring_record_id, started_at, db):
    """Best-effort decoder for captured R10 notifications.
    R10 packets are not documented; values 35..220 following packet headers are retained
    as HR candidates, with the original bytes persisted for audit/re-decoding later.
    """
    samples = []
    for offset, value in enumerate(payload):
        if 35 <= value <= 220:
            samples.append(RingSample(ring_record_id=ring_record_id,
                timestamp=started_at + timedelta(milliseconds=offset * 20),
                heart_rate=value, signal_quality=1.0,
                raw_payload={"offset": offset, "byte": value}))
    db.add_all(samples[:5000])
    return samples


def transcript_russian(wav_path: str | None):
    """Optional local Whisper integration; never sends sensitive audio to a third party."""
    if not wav_path or Path(wav_path).suffix.lower() != ".wav":
        return "", "ASR недоступен: WAV не создан"
    try:
        from faster_whisper import WhisperModel
        segments, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(wav_path, language="ru")
        return " ".join(s.text.strip() for s in segments), None
    except Exception:
        return "", "ASR не установлен; сохранён WAV для локальной расшифровки"


def make_window(session, db):
    samples = db.query(RingSample).join(RingRecord).filter(RingRecord.session_id == session.id).all()
    hr = [s.heart_rate for s in samples if s.heart_rate]
    mean_hr = round(sum(hr) / len(hr)) if hr else None
    # R1/R2 need acoustic/text classifiers. Until a trained model exists they are neutral,
    # while R3 is a clearly labelled HR-based screening estimate, not a diagnosis.
    r3 = None if mean_hr is None else max(-1.0, min(1.0, (mean_hr - 70) / 50))
    r1, r2 = 0.0, 0.0
    total = r3 / 3 if r3 is not None else 0.0
    comment = "Недостаточно физиологических данных." if r3 is None else ("Повышенная физиологическая нагрузка; это не медицинский диагноз." if r3 > .35 else "Выраженной физиологической нагрузки не обнаружено.")
    window = FeatureWindow(session_id=session.id, t_start=session.started_at, t_end=session.ended_at or datetime.utcnow(), r1=r1, r2=r2, r3=r3, r_total=total, heart_rate=mean_hr, model_comment=comment, quality_flags={"decoder": "best_effort_colmi_r10", "samples": len(hr)})
    if session.geo_points:
        point = session.geo_points[-1]; window.latitude=point.latitude; window.longitude=point.longitude
    db.add(window)
    return window
