import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import Response

from src.api.routes import router as api_router
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.middleware.logging import RequestLoggingMiddleware

# ---------------------------------------------------------------------------
# Setup logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ipl.server")

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "development")
IS_PRODUCTION = APP_ENV == "production"

# ---------------------------------------------------------------------------
# FastAPI app  (docs disabled in production)
# ---------------------------------------------------------------------------
app = FastAPI(
    title="IPL Prediction",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
)

# ---------------------------------------------------------------------------
# 1.  Rate Limiting  (100 req/min per IP)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ---------------------------------------------------------------------------
# 2.  CORS  (strict origin whitelist)
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "IPL_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 3.  Security Headers
# ---------------------------------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)

# ---------------------------------------------------------------------------
# 4.  Request Body Size Limit  (1 MB)
# ---------------------------------------------------------------------------
MAX_BODY_BYTES = 1 * 1024 * 1024  # 1 MB


class RequestSizeLimitMiddleware:
    """Reject requests whose Content-Length exceeds MAX_BODY_BYTES."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            content_length = headers.get(b"content-length")
            if content_length and int(content_length) > MAX_BODY_BYTES:
                response = Response("Request body too large", status_code=413)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


app.add_middleware(RequestSizeLimitMiddleware)

# ---------------------------------------------------------------------------
# 6.  Trusted Host Middleware
# ---------------------------------------------------------------------------
TRUSTED_HOSTS = [
    h.strip()
    for h in os.getenv("IPL_TRUSTED_HOSTS", "*").split(",")
    if h.strip()
]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

# ---------------------------------------------------------------------------
# 9.  Request Logging & Suspicious Activity Detection
# ---------------------------------------------------------------------------
app.add_middleware(RequestLoggingMiddleware)

# ---------------------------------------------------------------------------
# 10. HTTPS Redirect  (production only)
# ---------------------------------------------------------------------------
if IS_PRODUCTION:
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

    app.add_middleware(HTTPSRedirectMiddleware)

# ---------------------------------------------------------------------------
# Static file mounts
# ---------------------------------------------------------------------------
os.makedirs("outputs", exist_ok=True)
os.makedirs("data/assets/logos", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix="/api")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "healthy", "service": "IPL Prediction"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
