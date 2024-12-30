import logging
import calendar
from datetime import datetime, date
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from database import SessionDep
from models import (
    Maintenance,
    MaintenanceCreate,
    MaintenancePublic,
    MaintenanceReport,
    MaintenanceReportYearMonth,
)

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.get("/", response_model=list[MaintenancePublic])
async def get_maintenances(
    session: SessionDep,
    carId: int | None = None,
    garageId: int | None = None,
    startDate: date | None = None,
    endDate: date | None = None,
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


@router.get("/monthlyRequestsReport", response_model=list[MaintenanceReport])
async def get_monthly_requests_report(
    session: SessionDep,
    garageId: int,
    startMonth: Annotated[str, Query(regex=r"^\d{4}-\d{2}$")],
    endMonth: Annotated[str, Query(regex=r"^\d{4}-\d{2}$")],
):
    startDate = datetime.strptime(startMonth, "%Y-%m")
    endDate = datetime.strptime(endMonth, "%Y-%m")
    endDate = endDate.replace(day=calendar.monthrange(endDate.year, endDate.month)[1])

    query = (
        select(Maintenance)
        .where(Maintenance.garageId == garageId)
        .where(Maintenance.scheduledDate >= startDate)
        .where(Maintenance.scheduledDate <= endDate)
    )

    maintenances = session.exec(query).all()

    result: list[MaintenanceReport] = []

    current_date = startDate

    while current_date <= endDate:
        # Count the maintanances for the current month
        current_month_maintenances = sum(
            1
            for maintenance in maintenances
            if maintenance.scheduledDate.month == current_date.month
            and maintenance.scheduledDate.year == current_date.year
        )

        result.append(
            MaintenanceReport(
                yearMonth=MaintenanceReportYearMonth(
                    year=current_date.year,
                    month=calendar.month_name[current_date.month],
                    leapYear=calendar.isleap(current_date.year),
                    monthValue=current_date.month,
                ),
                requests=current_month_maintenances,
            )
        )

        # Go to the next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    return result


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
