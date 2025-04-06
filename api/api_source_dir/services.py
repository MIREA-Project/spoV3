from typing import Optional

from sqlalchemy import select, update, insert, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from . import services
from .db.models import PFCc, Products, UserEating, Steps, Water, Goals, EatingType
from .db import get_session


async def get_user_stat(user_id: int, session: AsyncSession) -> schemas.Statistic:
    user_water_subquery = select(
        func.sum(Water.volume),
    ).where(
        and_(
            func.date(Water.water_datetime) == func.current_date(),
            Water.user_id == user_id
        )
    ).scalar_subquery()
    user_steps_subquery = select(
        func.sum(Steps.count)
    ).where(
        and_(
            Steps.user_id == user_id,
            Steps.steps_date == func.current_date(),
        )
    ).scalar_subquery()
    user_stat_req = select(
        func.sum(PFCc.fats).label("fats"),
        func.sum(PFCc.proteins).label("proteins"),
        func.sum(PFCc.cb).label("cb"),
        func.sum(PFCc.calories).label("calories"),
        user_water_subquery.label("water"),
        user_steps_subquery.label("steps"),
    ).join(
        Products,
        Products.pfcc_id == PFCc.id
    ).join(
        UserEating,
        UserEating.product_id == Products.id
    ).where(
        and_(
            UserEating.user_id == user_id,
            UserEating.create_date == func.current_date()
        )
    )
    user_stat = await session.execute(user_stat_req)
    user_stat_dict: Optional[dict] = user_stat.mappings().one_or_none()
    if not user_stat_dict:
        return None
    c = 0
    for v in user_stat_dict.values():
        if v is None:
            c += 1
    if c == len(user_stat_dict.values()):
        return None
    user_stat_pydantic: schemas.Statistic = schemas.Statistic(**user_stat_dict)

    return user_stat_pydantic


async def add_product(name: str, session):
    pass
    # async with session.begin():
    #     create_product_req = insert(Products).values(name=name)
