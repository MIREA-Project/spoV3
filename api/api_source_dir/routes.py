import logging
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from . import services
from .db.models import PFCc, Products, UserEating, Steps, Water, Goals
from .db import get_session

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

# Food (Products) endpoints
@router.post("/products")
async def add_product(
    name: str,
    proteins: float,
    fats: float,
    carbs: float,
    calories: float,
    session: AsyncSession = Depends(get_session)
):
    # Create PFCc record
    pfcc = PFCc(proteins=proteins, fats=fats, cb=carbs, calories=calories)
    session.add(pfcc)
    await session.flush()
    
    # Create product with PFCc reference
    product = Products(name=name, pfcc_id=pfcc.id)
    session.add(product)
    await session.commit()
    return {"message": "Product added successfully", "product_id": product.id}

@router.post("/eating/batch")
async def add_eating_batch(
    user_id: int,
    product_ids: List[int],
    eating_type_id: int,
    session: AsyncSession = Depends(get_session)
):
    today = date.today()
    for product_id in product_ids:
        eating = UserEating(
            user_id=user_id,
            create_date=today,
            eating_type_id=eating_type_id,
            product_id=product_id
        )
        session.add(eating)
    await session.commit()
    return {"message": "Eating records added successfully"}

@router.delete("/eating/{eating_id}")
async def delete_eating(
    eating_id: int,
    session: AsyncSession = Depends(get_session)
):
    eating = await session.get(UserEating, eating_id)
    if not eating:
        raise HTTPException(status_code=404, detail="Eating record not found")
    await session.delete(eating)
    await session.commit()
    return {"message": "Eating record deleted successfully"}

# Steps endpoints
@router.post("/steps")
async def add_steps(
    user_id: int,
    count: int,
    session: AsyncSession = Depends(get_session)
):
    today = date.today()
    # Check if steps record exists for today
    existing_steps = await session.execute(
        select(Steps).where(
            Steps.user_id == user_id,
            Steps.steps_date == today
        )
    )
    existing_steps = existing_steps.scalar_one_or_none()
    
    if existing_steps:
        existing_steps.count += count
    else:
        new_steps = Steps(user_id=user_id, steps_date=today, count=count)
        session.add(new_steps)
    
    await session.commit()
    return {"message": "Steps added successfully"}

@router.delete("/steps/{steps_id}")
async def delete_steps(
    steps_id: int,
    count: int,
    session: AsyncSession = Depends(get_session)
):
    steps = await session.get(Steps, steps_id)
    if not steps:
        raise HTTPException(status_code=404, detail="Steps record not found")
    
    if steps.count <= count:
        await session.delete(steps)
    else:
        steps.count -= count
    
    await session.commit()
    return {"message": "Steps updated/deleted successfully"}

# Water endpoints
@router.post("/water")
async def add_water(
    user_id: int,
    volume: float,
    session: AsyncSession = Depends(get_session)
):
    water = Water(
        user_id=user_id,
        water_datetime=datetime.utcnow(),
        volume=volume
    )
    session.add(water)
    await session.commit()
    return {"message": "Water intake recorded successfully"}

@router.delete("/water/{water_id}")
async def delete_water(
    water_id: int,
    session: AsyncSession = Depends(get_session)
):
    water = await session.get(Water, water_id)
    if not water:
        raise HTTPException(status_code=404, detail="Water record not found")
    await session.delete(water)
    await session.commit()
    return {"message": "Water record deleted successfully"}

# Goals endpoints
@router.post("/goals")
async def add_goals(
    user_id: int,
    daily_calories: float,
    daily_proteins: float,
    daily_fats: float,
    daily_carbs: float,
    daily_water: float,
    daily_steps: int,
    session: AsyncSession = Depends(get_session)
):
    # Check if goals already exist for user
    existing_goals = await session.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    existing_goals = existing_goals.scalar_one_or_none()
    
    if existing_goals:
        raise HTTPException(status_code=400, detail="Goals already exist for this user")
    
    goals = Goals(
        user_id=user_id,
        daily_calories=daily_calories,
        daily_proteins=daily_proteins,
        daily_fats=daily_fats,
        daily_carbs=daily_carbs,
        daily_water=daily_water,
        daily_steps=daily_steps
    )
    session.add(goals)
    await session.commit()
    return {"message": "Goals added successfully"}

@router.get("/goals/{user_id}")
async def get_goals(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    goals = await session.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    goals = goals.scalar_one_or_none()
    if not goals:
        raise HTTPException(status_code=404, detail="Goals not found")
    return goals

@router.patch("/goals/{user_id}")
async def update_goals(
    user_id: int,
    daily_calories: Optional[float] = None,
    daily_proteins: Optional[float] = None,
    daily_fats: Optional[float] = None,
    daily_carbs: Optional[float] = None,
    daily_water: Optional[float] = None,
    daily_steps: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    goals = await session.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    goals = goals.scalar_one_or_none()
    if not goals:
        raise HTTPException(status_code=404, detail="Goals not found")
    
    if daily_calories is not None:
        goals.daily_calories = daily_calories
    if daily_proteins is not None:
        goals.daily_proteins = daily_proteins
    if daily_fats is not None:
        goals.daily_fats = daily_fats
    if daily_carbs is not None:
        goals.daily_carbs = daily_carbs
    if daily_water is not None:
        goals.daily_water = daily_water
    if daily_steps is not None:
        goals.daily_steps = daily_steps
    
    await session.commit()
    return {"message": "Goals updated successfully"}

# Weekly quality calculation
@router.get("/weekly-quality/{user_id}")
async def calculate_weekly_quality(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Get user's goals
    goals = await session.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    goals = goals.scalar_one_or_none()
    if not goals:
        raise HTTPException(status_code=404, detail="Goals not found")
    
    # Get start and end dates for the week
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Calculate average daily metrics
    # Water
    water_query = select(func.avg(Water.volume)).where(
        Water.user_id == user_id,
        Water.water_datetime >= week_start,
        Water.water_datetime <= week_end
    )
    avg_water = await session.execute(water_query)
    avg_water = avg_water.scalar() or 0
    
    # Steps
    steps_query = select(func.avg(Steps.count)).where(
        Steps.user_id == user_id,
        Steps.steps_date >= week_start,
        Steps.steps_date <= week_end
    )
    avg_steps = await session.execute(steps_query)
    avg_steps = avg_steps.scalar() or 0
    
    # Calculate quality scores
    water_quality = min(100, (avg_water / goals.daily_water) * 100)
    steps_quality = min(100, (avg_steps / goals.daily_steps) * 100)
    
    # Calculate nutrition quality
    nutrition_query = select(
        func.avg(PFCc.calories).label('avg_calories'),
        func.avg(PFCc.proteins).label('avg_proteins'),
        func.avg(PFCc.fats).label('avg_fats'),
        func.avg(PFCc.cb).label('avg_carbs')
    ).join(Products).join(UserEating).where(
        UserEating.user_id == user_id,
        UserEating.create_date >= week_start,
        UserEating.create_date <= week_end
    )
    nutrition = await session.execute(nutrition_query)
    nutrition = nutrition.first()
    
    calories_quality = min(100, (nutrition.avg_calories / goals.daily_calories) * 100) if nutrition.avg_calories else 0
    proteins_quality = min(100, (nutrition.avg_proteins / goals.daily_proteins) * 100) if nutrition.avg_proteins else 0
    fats_quality = min(100, (nutrition.avg_fats / goals.daily_fats) * 100) if nutrition.avg_fats else 0
    carbs_quality = min(100, (nutrition.avg_carbs / goals.daily_carbs) * 100) if nutrition.avg_carbs else 0
    
    # Calculate overall quality
    overall_quality = (
        water_quality + steps_quality + calories_quality + 
        proteins_quality + fats_quality + carbs_quality
    ) / 6
    
    return {
        "week_start": week_start,
        "week_end": week_end,
        "water_quality": water_quality,
        "steps_quality": steps_quality,
        "calories_quality": calories_quality,
        "proteins_quality": proteins_quality,
        "fats_quality": fats_quality,
        "carbs_quality": carbs_quality,
        "overall_quality": overall_quality
    }
