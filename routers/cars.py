from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from database import SessionDep
from models import Car, CarCreate, CarUpdate, CarPublic, Garage


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
        # TODO: Implement this
        pass

    if fromYear:
        query = query.where(Car.year >= fromYear)

    if toYear:
        query = query.where(Car.year <= toYear)

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

    for id in car.garageIds:
        garage = session.get(Garage, id)

        if not garage:
            raise HTTPException(status_code=404, detail="Garage not found")

        car_db.garages.append(garage)

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
        car_db.garages.clear()

        for id in car.garageIds:
            garage = session.get(Garage, id)

            if not garage:
                raise HTTPException(status_code=404, detail="Garage not found")

            car_db.garages.append(garage)

    session.add(car_db)
    session.commit()
    session.refresh(car_db)

    return car_db
