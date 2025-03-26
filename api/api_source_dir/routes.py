from fastapi import APIRouter, HTTPException, Request
from . import schemas
from . import services

router = APIRouter(tags=["default"])


@router.get("/test")
async def start():
    return {"status": "OK"}


@router.get("/find_me")
async def find_me(user_id: int):
    return {"message": f"i find you in db, your id={user_id}"}


@router.get("/statistic", response_model=schemas.Statistic)
async def get_today_statistic(
        user_id: int,
        request: Request,
):
    if not (today_stat := await services.get_user_stat(user_id, request.state.db)):
        raise HTTPException(status_code=500, detail="Cant get user info")
    return today_stat


@router.patch("/update_statistic")
async def update_statistic(
        user_stat: schemas.Statistic,
):
    pass
