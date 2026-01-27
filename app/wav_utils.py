import io
import wave

def pcm_to_wav(
    pcm_bytes: bytes,
    sample_rate: int
) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)      # mono
        wf.setsampwidth(2)      # PCM16
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buffer.getvalue()
