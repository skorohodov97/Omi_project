import io
import wave

def pcm_to_wav(
    pcm_bytes: bytes,
    sample_rate: int,
    channels: int = 1,
    sample_width: int = 2
) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buffer.getvalue()
