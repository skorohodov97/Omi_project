from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class DeviceCreate(BaseModel):
    name: str


class RingCreate(BaseModel):
    device_id: UUID
    payload: dict


class AudioResponse(BaseModel):
    id: UUID
    file_path: str