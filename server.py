import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.routes import router as api_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ipl.server")

app = FastAPI(title="IPL 2026 Prediction API")

# CORS setup
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
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs and assets for static access
os.makedirs("outputs", exist_ok=True)
os.makedirs("data/assets/logos", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "IPL 2026 Prediction API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
