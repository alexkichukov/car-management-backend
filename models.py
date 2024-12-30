import datetime
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


# Association table for many-to-many relationship between cars and garages
class CarGarageLink(SQLModel, table=True):
    car_id: int | None = Field(default=None, foreign_key="car.id", primary_key=True)
    garage_id: int | None = Field(
        default=None, foreign_key="garage.id", primary_key=True
    )


# Car
class CarBase(SQLModel):
    make: str = Field(index=True, min_length=1)
    model: str = Field(index=True, min_length=1)
    productionYear: int = Field(index=True, gt=0)
    licensePlate: str = Field(index=True, min_length=1)


class Car(CarBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    garages: list["Garage"] = Relationship(
        back_populates="cars", link_model=CarGarageLink
    )
    maintenances: list["Maintenance"] = Relationship(back_populates="car")


class CarCreate(CarBase):
    garageIds: list[int] = []
    pass


class CarUpdate(CarBase):
    make: str | None = Field(min_length=1, default=None)
    model: str | None = Field(min_length=1, default=None)
    productionYear: int | None = Field(gt=0, default=None)
    licensePlate: str | None = Field(min_length=1, default=None)
    garageIds: list[int] = []


class CarPublic(CarBase):
    id: int
    garages: list["GaragePublic"] = []


# Garage
class GarageBase(SQLModel):
    name: str = Field(index=True, min_length=1)
    location: str = Field(index=True, min_length=1)
    city: str = Field(index=True, min_length=1)
    capacity: int = Field(index=True, gt=0)


class Garage(GarageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cars: list[Car] = Relationship(back_populates="garages", link_model=CarGarageLink)
    maintenances: list["Maintenance"] = Relationship(back_populates="garage")


class GarageCreate(GarageBase):
    pass


class GarageUpdate(GarageBase):
    name: str | None = None
    location: str | None = None
    city: str | None = None
    capacity: int | None = None


class GaragePublic(GarageBase):
    id: int


class GarageAvailabilityReport(BaseModel):
    date: datetime.date
    requests: int
    availableCapacity: int


# Maintenance
class MaintenanceBase(SQLModel):
    serviceType: str = Field(index=True, min_length=1)
    scheduledDate: datetime.date = Field(index=True)


class Maintenance(MaintenanceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    carId: int = Field(default=None, foreign_key="car.id")
    garageId: int = Field(default=None, foreign_key="garage.id")
    car: Car = Relationship(back_populates="maintenances")
    garage: Garage = Relationship(back_populates="maintenances")

    def to_public(self) -> "MaintenancePublic":
        return MaintenancePublic(
            id=self.id,
            serviceType=self.serviceType,
            scheduledDate=self.scheduledDate,
            carId=self.car.id,
            carName=self.car.make + " " + self.car.model,
            garageId=self.garage.id,
            garageName=self.garage.name,
        )


class MaintenanceCreate(MaintenanceBase):
    carId: int
    garageId: int


class MaintenanceUpdate(MaintenanceBase):
    carId: int | None = None
    garageId: int | None = None
    serviceType: str | None = Field(min_length=1, default=None)
    scheduledDate: datetime.date | None = None


class MaintenancePublic(MaintenanceBase):
    id: int
    carId: int
    carName: str
    garageId: int
    garageName: str


class MaintenanceReportYearMonth(BaseModel):
    year: int
    month: str
    leapYear: bool
    monthValue: int


class MaintenanceReport(BaseModel):
    yearMonth: MaintenanceReportYearMonth
    requests: int
