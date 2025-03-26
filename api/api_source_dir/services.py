from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_source_dir.db.models import Statistic
from . import schemas


async def get_user_stat(user_id: int, session: AsyncSession) -> schemas.Statistic:
    # print(session)
    # return schemas.Statistic(
    #     steps=12
    # )
    user_stat_req = select(Statistic).where(Statistic.user_id == user_id)
    user_stat = await session.execute(user_stat_req)
    user_stat_db_model: Optional[schemas.Statistic] = user_stat.scalars().one_or_none()

    if not user_stat_db_model:
        return None

    user_stat_pydantic: schemas.Statistic = schemas.Statistic(**user_stat_db_model.__dict__)
    return user_stat_pydantic
