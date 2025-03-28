import logging

from fastapi import APIRouter, HTTPException, Request
from . import schemas
from . import services

logger = logging.getLogger(__name__)
router = APIRouter(tags=["default"])


@router.get("/health")
async def check_api_health():
    return {"status": "OK"}


@router.get("/statistic", response_model=schemas.Statistic)
async def get_today_statistic(
        user_id: int,
        request: Request,
):
    if not (today_stat := await services.get_user_stat(user_id, request.state.db)):
        raise HTTPException(status_code=404, detail="Cant get user info or no info for today")
    return today_stat
