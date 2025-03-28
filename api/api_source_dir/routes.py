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

# To do

# добавление еды, как рецепт для создания своего продукта с бжу
# добавление еды (patch списком продуктов и мы создаем строки)
# удаление еды, которую скушал
# добавление шагов (если нет шагов, то insert, если есть, то update)
# вычитание шагов (если нет шагов, то дроп тейбл, если есть, то вычитаем, но проверить, чтобы в - не ушли)
# добавление воды (также, как с шагами)
# вычитание воды
# добавить класс Goals с его целью по питанию, воде и т.п.
# получение Goals по user_id 
# добавление Goals 
# изменение Goals
# Посчитать качество недели
# ИИ для рекомендации по неделе, если не 100 из 100
