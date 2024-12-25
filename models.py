from sqlmodel import Field, Relationship, SQLModel


# Association table for many-to-many relationship between cars and garages
class CarGarageLink(SQLModel, table=True):
    car_id: int | None = Field(default=None, foreign_key="car.id", primary_key=True)
    garage_id: int | None = Field(
        default=None, foreign_key="garage.id", primary_key=True
    )


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
