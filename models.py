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
    make: str = Field(index=True)
    model: str = Field(index=True)
    productionYear: int = Field(index=True)
    licensePlate: str = Field(index=True)


class Car(CarBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    garages: list["Garage"] = Relationship(
        back_populates="cars", link_model=CarGarageLink
    )


class CarCreate(CarBase):
    garageIds: list[int] = []
    pass


class CarUpdate(CarBase):
    make: str | None = None
    model: str | None = None
    productionYear: int | None = None
    licensePlate: str | None = None
    garageIds: list[int] = []


class CarPublic(CarBase):
    id: int
    garages: list["GaragePublic"] = []


# Garage
class GarageBase(SQLModel):
    name: str = Field(index=True)
    location: str = Field(index=True)
    city: str = Field(index=True)
    capacity: int = Field(index=True)


class Garage(GarageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cars: list[Car] = Relationship(back_populates="garages", link_model=CarGarageLink)


class GarageCreate(GarageBase):
    pass


class GarageUpdate(GarageBase):
    name: str | None = None
    location: str | None = None
    city: str | None = None
    capacity: int | None = None


class GaragePublic(GarageBase):
    id: int


# Maintenance
class MaintenanceBase(SQLModel):
    serviceType: str = Field(index=True)
    scheduledDate: datetime.date = Field(index=True)


class Maintenance(MaintenanceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    carId: int = Field(default=None, foreign_key="car.id")
    garageId: int = Field(default=None, foreign_key="garage.id")
    car: Car = Relationship()
    garage: Garage = Relationship()

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
    serviceType: str | None = None
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
