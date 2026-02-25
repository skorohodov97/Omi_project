from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Device
from app.schemas import DeviceCreate
from datetime import datetime

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register")
def register_device(data: DeviceCreate, db: Session = Depends(get_db)):
    device = Device(
        name=data.name,
        created_at=datetime.utcnow()
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return {
        "id": device.id,
        "name": device.name,
        "created_at": device.created_at
    }