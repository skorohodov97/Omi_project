from fastapi import FastAPI, Request
import time
from app.routers import audio, ring, devices, sessions

app = FastAPI(title="Audio Backend")


@app.middleware("http")
async def log_all(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    ms = int((time.time() - start) * 1000)
    print(f"{request.method} {request.url.path} -> {resp.status_code} ({ms}ms)")
    return resp


app.include_router(devices.router)
app.include_router(ring.router)
app.include_router(audio.router)
app.include_router(sessions.router)


@app.get("/health")
def health():
    return {"ok": True}
