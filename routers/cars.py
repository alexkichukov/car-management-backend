from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from database import SessionDep
from models import Car, CarCreate, CarUpdate, CarPublic, Garage, Maintenance


router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/", response_model=list[CarPublic])
async def get_cars(
    session: SessionDep,
    carMake: str | None = None,
    garageId: int | None = None,
    fromYear: int | None = None,
    toYear: int | None = None,
):
    query = select(Car)

    if carMake:
        query = query.where(func.lower(Car.make) == carMake.lower())

    if garageId:
        query = query.where(Car.garages.any(Garage.id == garageId))

    if fromYear:
        query = query.where(Car.productionYear >= fromYear)

    if toYear:
        query = query.where(Car.productionYear <= toYear)

    cars = session.exec(query).all()
    return cars


@router.get("/{car_id}", response_model=CarPublic)
async def get_car(car_id: int, session: SessionDep):
    car = session.get(Car, car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


@router.post("/", response_model=CarPublic)
async def create_car(car: CarCreate, session: SessionDep):
    car_db = Car.model_validate(car)

    if car.garageIds:
        garages = session.exec(select(Garage).where(Garage.id.in_(car.garageIds))).all()

        if len(garages) != len(car.garageIds):
            raise HTTPException(status_code=404, detail="One or more garages not found")

        car_db.garages = garages

    session.add(car_db)
    session.commit()
    session.refresh(car_db)

    return car_db


@router.put("/{car_id}", response_model=CarPublic)
async def update_car(car_id: int, car: CarUpdate, session: SessionDep):
    car_db = session.get(Car, car_id)

    if not car_db:
        raise HTTPException(status_code=404, detail="Car not found")

    car_data = car.model_dump(exclude_unset=True)

    car_db.sqlmodel_update(car_data)

    if car.garageIds:
        garages = session.exec(select(Garage).where(Garage.id.in_(car.garageIds))).all()

        if len(garages) != len(car.garageIds):
            raise HTTPException(status_code=404, detail="One or more garages not found")

        car_db.garages = garages

    session.add(car_db)
    session.commit()
    session.refresh(car_db)

    return car_db


@router.delete("/{car_id}")
async def delete_car(car_id: int, session: SessionDep):
    car = session.get(Car, car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Delete maintenances that use the car
    maintenances = session.exec(
        select(Maintenance).where(Maintenance.carId == car_id)
    ).all()

    for maintenance in maintenances:
        session.delete(maintenance)

    session.delete(car)
    session.commit()

    return {"ok": True}
