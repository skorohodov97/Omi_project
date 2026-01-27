from fastapi import FastAPI, Request
from app.receiver import router
import time

app = FastAPI(title="Audio Ingest MVP")

@app.middleware("http")
async def log_all(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    ms = int((time.time() - start) * 1000)
    print(
        f"IN {request.client.host}:{request.client.port} "
        f"{request.method} {request.url.path}?{request.url.query} "
        f"CT={request.headers.get('content-type')} "
        f"CL={request.headers.get('content-length')} "
        f"-> {resp.status_code} ({ms}ms)"
    )
    return resp

app.include_router(router)

