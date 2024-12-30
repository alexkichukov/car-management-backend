import datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from database import SessionDep
from models import Maintenance, MaintenanceCreate, MaintenancePublic


router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.get("/", response_model=list[MaintenancePublic])
async def get_maintenances(
    session: SessionDep,
    carId: int | None = None,
    garageId: int | None = None,
    startDate: datetime.date | None = None,
    endDate: datetime.date | None = None,
):
    query = select(Maintenance)

    if carId:
        query = query.where(Maintenance.carId == carId)

    if garageId:
        query = query.where(Maintenance.garageId == garageId)

    if startDate:
        query = query.where(Maintenance.scheduledDate >= startDate)

    if endDate:
        query = query.where(Maintenance.scheduledDate <= endDate)

    maintenances = session.exec(query).all()

    maintenances_public = [maintenance.to_public() for maintenance in maintenances]

    return maintenances_public


@router.get("/{maintenance_id}", response_model=MaintenancePublic)
async def get_maintenance(maintenance_id: int, session: SessionDep):
    maintenance = session.get(Maintenance, maintenance_id)

    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")

    return maintenance.to_public()


@router.post("/", response_model=MaintenancePublic)
async def create_maintenance(maintenance: MaintenanceCreate, session: SessionDep):
    maintenance_db = Maintenance.model_validate(maintenance)

    session.add(maintenance_db)
    session.commit()
    session.refresh(maintenance_db)

    return maintenance_db.to_public()


@router.put("/{maintenance_id}", response_model=MaintenancePublic)
async def update_maintenance(
    maintenance_id: int, maintenance: MaintenanceCreate, session: SessionDep
):
    maintenance_db = session.get(Maintenance, maintenance_id)

    if not maintenance_db:
        raise HTTPException(status_code=404, detail="Maintenance not found")

    maintenance_data = maintenance.model_dump(exclude_unset=True)
    maintenance_db.sqlmodel_update(maintenance_data)

    session.add(maintenance_db)
    session.commit()
    session.refresh(maintenance_db)

    return maintenance_db.to_public()
