import os
import shutil
import struct
import subprocess
from pathlib import Path


class OmiAudioError(ValueError):
    pass


def parse_omi_opus_dump(dump_bytes: bytes) -> list[bytes]:
    frames: list[bytes] = []
    offset = 0
    expected_packet = None

    while offset < len(dump_bytes):
        if offset + 2 > len(dump_bytes):
            raise OmiAudioError(f"Truncated length at offset {offset}")

        notification_length = int.from_bytes(dump_bytes[offset:offset + 2], "little")
        offset += 2

        if notification_length < 4:
            raise OmiAudioError(f"Invalid notification length {notification_length} at offset {offset - 2}")

        end = offset + notification_length
        if end > len(dump_bytes):
            raise OmiAudioError(f"Truncated notification at offset {offset}")

        notification = dump_bytes[offset:end]
        offset = end

        packet_number = int.from_bytes(notification[:2], "little")
        packet_index = notification[2]
        payload = notification[3:]

        if packet_index != 0:
            raise OmiAudioError("Multi-notification Opus packets are not supported yet")

        if expected_packet is not None and packet_number != expected_packet:
            raise OmiAudioError(f"Packet sequence gap: expected {expected_packet}, got {packet_number}")

        expected_packet = (packet_number + 1) & 0xFFFF
        frames.append(payload)

    if not frames:
        raise OmiAudioError("No Opus frames found")

    return frames


def _ogg_crc_table() -> list[int]:
    table = []
    for i in range(256):
        crc = i << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        table.append(crc)
    return table


_OGG_CRC_TABLE = _ogg_crc_table()


def _ogg_crc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ _OGG_CRC_TABLE[((crc >> 24) & 0xFF) ^ byte]
    return crc


def _ogg_page(packet: bytes, serial: int, sequence: int, granule: int, header_type: int) -> bytes:
    segments = []
    remaining = len(packet)
    while remaining >= 255:
        segments.append(255)
        remaining -= 255
    segments.append(remaining)

    if len(segments) > 255:
        raise OmiAudioError("Opus packet is too large for a single Ogg page")

    header = (
        b"OggS"
        + bytes([0])
        + bytes([header_type])
        + struct.pack("<QIIIB", granule, serial, sequence, 0, len(segments))
        + bytes(segments)
    )
    page = header + packet
    crc = _ogg_crc(page)
    return page[:22] + struct.pack("<I", crc) + page[26:]


def opus_frames_to_ogg(
    frames: list[bytes],
    sample_rate: int = 16000,
    channels: int = 1,
    frame_samples: int = 160
) -> bytes:
    serial = int.from_bytes(os.urandom(4), "little")
    sequence = 0
    pages = []

    opus_head = (
        b"OpusHead"
        + bytes([1, channels])
        + struct.pack("<H", 312)
        + struct.pack("<I", sample_rate)
        + struct.pack("<h", 0)
        + bytes([0])
    )
    pages.append(_ogg_page(opus_head, serial, sequence, 0, 0x02))
    sequence += 1

    vendor = b"omi-backend"
    opus_tags = b"OpusTags" + struct.pack("<I", len(vendor)) + vendor + struct.pack("<I", 0)
    pages.append(_ogg_page(opus_tags, serial, sequence, 0, 0x00))
    sequence += 1

    granule = 0
    granule_step = int(frame_samples * 48000 / sample_rate)

    for index, frame in enumerate(frames):
        granule += granule_step
        header_type = 0x04 if index == len(frames) - 1 else 0x00
        pages.append(_ogg_page(frame, serial, sequence, granule, header_type))
        sequence += 1

    return b"".join(pages)


def omi_opus_dump_to_ogg(dump_bytes: bytes, sample_rate: int = 16000) -> bytes:
    frames = parse_omi_opus_dump(dump_bytes)
    return opus_frames_to_ogg(frames, sample_rate=sample_rate)


def _find_ffmpeg() -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None

    winget_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
    if not winget_packages.exists():
        return None

    matches = sorted(winget_packages.glob("Gyan.FFmpeg_*/**/ffmpeg.exe"))
    if not matches:
        return None

    return str(matches[-1])


def convert_ogg_opus_to_wav(opus_path: Path, wav_path: Path) -> bool:
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        return False

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(opus_path),
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(wav_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return True
