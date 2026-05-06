from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, vitals, messages, alerts, admin, doctor, iot

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vitals.router, prefix="/vitals", tags=["vitals"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(doctor.router, prefix="/doctor", tags=["doctor"]) # Added Doctor Router
api_router.include_router(iot.router, prefix="/iot", tags=["iot"])
