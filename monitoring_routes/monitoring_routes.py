from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from schemas import MonitoringResponse
from models import User
from database import session, engine
from monitoring_routes.utils import calculate_monitoring_stats

monitoring_router = APIRouter(
    prefix="/api/monitoring",
    tags=["Monitoring"]
)

session = session(bind=engine)

@monitoring_router.get("/", response_model=MonitoringResponse)
def get_monitoring_data(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or missing")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stats = calculate_monitoring_stats(user_id=user.id)
    return stats

        

