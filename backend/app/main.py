from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RPM Vital Collection & Alert System",
    description="Backend API for Post-Operative Monitoring",
    version="1.0.0",
)

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.api import api_router
from app.core.config import settings

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to RPM Vital Collection System API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
