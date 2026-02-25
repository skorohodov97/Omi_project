import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
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