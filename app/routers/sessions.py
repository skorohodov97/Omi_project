from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.services.analysis_service import make_window

router = APIRouter(tags=["sessions"])

def epoch(v): return datetime.fromtimestamp(v / 1000, tz=timezone.utc).replace(tzinfo=None)

@router.post("/sessions")
async def create_session(request: Request, db: Session = Depends(get_db)):
    data = await request.json(); device_id = UUID(data["device_id"])
    if not db.get(models.Device, device_id): raise HTTPException(404, "Device not found")
    session=models.RecordingSession(device_id=device_id, started_at=epoch(int(data["started_at"])), timezone=data.get("timezone"), status="uploading")
    db.add(session); db.commit(); db.refresh(session); return {"id": session.id}

@router.post("/sessions/{session_id}/geo-points")
async def geo_points(session_id: UUID, request: Request, db: Session = Depends(get_db)):
    session=db.get(models.RecordingSession, session_id)
    if not session: raise HTTPException(404, "Session not found")
    points=await request.json()
    for p in points:
        if "latitude" in p and "longitude" in p: db.add(models.GeoPoint(session_id=session_id, timestamp=epoch(int(p["timestamp"])), latitude=p["latitude"], longitude=p["longitude"], altitude=p.get("altitude"), accuracy=p.get("accuracy"), provider=p.get("provider")))
    db.commit(); return {"count": len(points)}

@router.post("/sessions/{session_id}/finish")
def finish_session(session_id: UUID, db: Session = Depends(get_db)):
    session=db.get(models.RecordingSession, session_id)
    if not session: raise HTTPException(404, "Session not found")
    session.ended_at=datetime.utcnow(); session.status="ready"; make_window(session, db); db.commit(); return {"id":session.id,"status":session.status}

@router.get("/route/events")
def route_events(device_id: UUID, day: str | None = None, db: Session = Depends(get_db)):
    q=db.query(models.FeatureWindow).join(models.RecordingSession).filter(models.RecordingSession.device_id==device_id)
    if day: q=q.filter(models.FeatureWindow.t_start >= datetime.fromisoformat(day), models.FeatureWindow.t_start < datetime.fromisoformat(day).replace(hour=23, minute=59, second=59))
    result=[]
    for w in q.order_by(models.FeatureWindow.t_start.desc()):
        audio=db.query(models.AudioRecord).filter(models.AudioRecord.session_id == w.session_id).order_by(models.AudioRecord.created_at.desc()).first()
        result.append({"id":str(w.id),"timestamp":w.t_start,"latitude":w.latitude,"longitude":w.longitude,"r1":w.r1,"r2":w.r2,"r3":w.r3,"risk":w.r_total,"heart_rate":w.heart_rate,"transcript":w.transcript or (audio.transcript_text if audio else ""),"comment":w.model_comment,"has_location":w.latitude is not None,"audio_url":f"/data/audio/files/{audio.id}/download" if audio and audio.file_path.endswith('.wav') else None})
    return result
