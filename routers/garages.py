from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from database import SessionDep
from models import Garage, GarageCreate, GaragePublic, GarageUpdate, Maintenance


router = APIRouter(prefix="/garages", tags=["garages"])


@router.get("/", response_model=list[GaragePublic])
async def get_garages(session: SessionDep, city: str | None = None):
    query = select(Garage)

    if city:
        query = query.where(func.lower(Garage.city) == city.lower())

    garages = session.exec(query).all()
    return garages


@router.get("/{garage_id}", response_model=GaragePublic)
async def get_garage(garage_id: int, session: SessionDep):
    garage = session.get(Garage, garage_id)

    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    return garage


@router.post("/", response_model=GaragePublic)
async def create_garage(garage: GarageCreate, session: SessionDep):
    garage_db = Garage.model_validate(garage)

    session.add(garage_db)
    session.commit()
    session.refresh(garage_db)

    return garage_db


@router.put("/{garage_id}", response_model=GaragePublic)
async def update_garage(garage_id: int, garage: GarageUpdate, session: SessionDep):
    garage_db = session.get(Garage, garage_id)

    if not garage_db:
        raise HTTPException(status_code=404, detail="Garage not found")

    garage_data = garage.model_dump(exclude_unset=True)
    garage_db.sqlmodel_update(garage_data)

    session.add(garage_db)
    session.commit()
    session.refresh(garage_db)

    return garage_db


@router.delete("/{garage_id}")
async def delete_garage(garage_id: int, session: SessionDep):
    garage = session.get(Garage, garage_id)

    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Delete the garage from cars linked to it
    for car in garage.cars:
        car.garages.remove(garage)
        session.add(car)

    # Delete maintenances that use the garage
    for maintenance in garage.maintenances:
        session.delete(maintenance)

    session.delete(garage)
    session.commit()

    return {"ok": True}
