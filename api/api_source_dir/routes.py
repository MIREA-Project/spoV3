import logging
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from . import schemas
from . import services
from .db.models import PFCc, Products, UserEating, Steps, Water, Goals, EatingType
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

@router.delete("/eating")
async def delete_eating(
    user_id: int,
    eating_type_id: int,
    session: AsyncSession = Depends(get_session)
):
    today = date.today()
    eating_records = await session.execute(
        select(UserEating).where(
            UserEating.user_id == user_id,
            UserEating.eating_type_id == eating_type_id,
            UserEating.create_date == today
        )
    )
    eating_records = eating_records.scalars().all()
    
    if not eating_records:
        raise HTTPException(status_code=404, detail="No eating records found for today")
    
    for record in eating_records:
        await session.delete(record)
    
    await session.commit()
    return {"message": "Eating records deleted successfully"}

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

@router.delete("/steps")
async def delete_steps(
    user_id: int,
    count: int,
    session: AsyncSession = Depends(get_session)
):
    today = date.today()
    steps = await session.execute(
        select(Steps).where(
            Steps.user_id == user_id,
            Steps.steps_date == today
        )
    )
    steps = steps.scalar_one_or_none()
    
    if not steps:
        raise HTTPException(status_code=404, detail="No steps record found for today")
    
    if steps.count - count < 0:
        raise HTTPException(status_code=400, detail="Cannot delete more steps than available")
    
    if steps.count - count == 0:
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

@router.delete("/water")
async def delete_water(
    user_id: int,
    volume: float,
    session: AsyncSession = Depends(get_session)
):
    today = date.today()
    water_records = await session.execute(
        select(Water).where(
            Water.user_id == user_id,
            func.date(Water.water_datetime) == today
        )
    )
    water_records = water_records.scalars().all()
    
    if not water_records:
        raise HTTPException(status_code=404, detail="No water records found for today")
    
    total_volume = sum(record.volume for record in water_records)
    if total_volume - volume < 0:
        raise HTTPException(status_code=400, detail="Cannot delete more water than available")
    
    # Delete records until we reach the desired volume
    remaining_volume = volume
    for record in water_records:
        if remaining_volume <= 0:
            break
        if record.volume <= remaining_volume:
            await session.delete(record)
            remaining_volume -= record.volume
        else:
            record.volume -= remaining_volume
            remaining_volume = 0
    
    await session.commit()
    return {"message": "Water records updated/deleted successfully"}

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
        Decimal(water_quality) + Decimal(steps_quality) + Decimal(calories_quality) + 
        Decimal(proteins_quality) + Decimal(fats_quality) + Decimal(carbs_quality)
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

# GET endpoints for all models
@router.get("/products")
async def get_products(
    session: AsyncSession = Depends(get_session)
):
    query = select(Products)
    products = await session.execute(query)
    return products.scalars().all()

@router.get("/eating")
async def get_eating(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(UserEating)
    if user_id:
        query = query.where(UserEating.user_id == user_id)
    eating_records = await session.execute(query)
    return eating_records.scalars().all()

@router.get("/steps")
async def get_steps(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(Steps)
    if user_id:
        query = query.where(Steps.user_id == user_id)
    steps = await session.execute(query)
    return steps.scalars().all()

@router.get("/water")
async def get_water(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(Water)
    if user_id:
        query = query.where(Water.user_id == user_id)
    water_records = await session.execute(query)
    return water_records.scalars().all()

@router.get("/eating-types")
async def get_eating_types(
    session: AsyncSession = Depends(get_session)
):
    eating_types = await session.execute(select(EatingType))
    return eating_types.scalars().all()

@router.get("/products/search")
async def search_products(
    name: str,
    session: AsyncSession = Depends(get_session)
):
    query = select(Products).where(
        Products.name.ilike(f"%{name}%")
    )
    products = await session.execute(query)
    return products.scalars().all()

@router.post("/goals/calculate")
async def calculate_and_set_goals(
    user_id: int,
    height_cm: float,  # рост в сантиметрах
    weight_kg: float,  # вес в килограммах
    session: AsyncSession = Depends(get_session)
):
    # Конвертируем рост в метры
    height_m = height_cm / 100
    
    # Рассчитываем ИМТ
    bmi = weight_kg / (height_m ** 2)
    
    # Рассчитываем базовый обмен веществ (BMR)
    # Используем формулу Миффлина-Сан Жеора
    # Предполагаем средний возраст 30 лет
    age = 30
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    
    # Рассчитываем дневную норму калорий
    # Используем коэффициент 1.2 для умеренной активности
    daily_calories = bmr * 1.2
    
    # Рассчитываем макронутриенты
    # Белки: 30% от калорий (4 калории на грамм)
    daily_proteins = (daily_calories * 0.3) / 4
    
    # Жиры: 30% от калорий (9 калорий на грамм)
    daily_fats = (daily_calories * 0.3) / 9
    
    # Углеводы: 40% от калорий (4 калории на грамм)
    daily_carbs = (daily_calories * 0.4) / 4
    
    # Рекомендуемое количество воды (30 мл на кг веса)
    daily_water = weight_kg * 30
    
    # Рекомендуемое количество шагов (10000 для умеренной активности)
    daily_steps = 10000
    
    # Проверяем существующие цели
    existing_goals = await session.execute(
        select(Goals).where(Goals.user_id == user_id)
    )
    existing_goals = existing_goals.scalar_one_or_none()
    
    if existing_goals:
        # Обновляем существующие цели
        existing_goals.daily_calories = daily_calories
        existing_goals.daily_proteins = daily_proteins
        existing_goals.daily_fats = daily_fats
        existing_goals.daily_carbs = daily_carbs
        existing_goals.daily_water = daily_water
        existing_goals.daily_steps = daily_steps
    else:
        # Создаем новые цели
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
    
    return {
        "message": "Goals calculated and set successfully",
        "bmi": bmi,
        "daily_calories": daily_calories,
        "daily_proteins": daily_proteins,
        "daily_fats": daily_fats,
        "daily_carbs": daily_carbs,
        "daily_water": daily_water,
        "daily_steps": daily_steps
    }
