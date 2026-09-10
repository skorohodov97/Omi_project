import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    audio_records = relationship(
        "AudioRecord",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    ring_records = relationship(
        "RingRecord",
        back_populates="device",
        cascade="all, delete-orphan"
    )
    last_seen = Column(DateTime, nullable=True)
    sessions = relationship("RecordingSession", back_populates="device", cascade="all, delete-orphan")


class RecordingSession(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    timezone = Column(String)
    status = Column(String, default="recording", nullable=False)
    device = relationship("Device", back_populates="sessions")
    geo_points = relationship("GeoPoint", back_populates="session", cascade="all, delete-orphan")
    windows = relationship("FeatureWindow", back_populates="session", cascade="all, delete-orphan")


class GeoPoint(Base):
    __tablename__ = "geo_points"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    accuracy = Column(Float)
    provider = Column(String)
    session = relationship("RecordingSession", back_populates="geo_points")


class AudioRecord(Base):
    __tablename__ = "audio_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"))
    file_path = Column(String, nullable=False)
    sample_rate = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="audio_records")
    channels = Column(Integer)
    sample_width = Column(Integer)
    duration_ms = Column(Integer)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"))
    transcript_path = Column(String)
    transcript_text = Column(Text)


class RingData(Base):
    __tablename__ = "ring_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"))
    payload = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)

class RingRecord(Base):
    __tablename__ = "ring_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False
    )

    file_path = Column(String, nullable=False)

    file_size = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="ring_records")
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"))


class RingSample(Base):
    __tablename__ = "ring_samples"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ring_record_id = Column(UUID(as_uuid=True), ForeignKey("ring_records.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    heart_rate = Column(Integer)
    spo2 = Column(Integer)
    signal_quality = Column(Float)
    raw_payload = Column(JSONB)


class FeatureWindow(Base):
    __tablename__ = "feature_windows"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    t_start = Column(DateTime, nullable=False)
    t_end = Column(DateTime, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    r1 = Column(Float)
    r2 = Column(Float)
    r3 = Column(Float)
    r_total = Column(Float)
    heart_rate = Column(Integer)
    transcript = Column(Text)
    model_comment = Column(Text)
    quality_flags = Column(JSONB)
    session = relationship("RecordingSession", back_populates="windows")
