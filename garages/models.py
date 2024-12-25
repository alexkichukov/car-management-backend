from sqlmodel import Field, SQLModel


# Base model
class GarageBase(SQLModel):
    name: str = Field(index=True)
    location: str = Field(index=True)
    city: str = Field(index=True)
    capacity: int = Field(index=True)


# Table model
class Garage(GarageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# Crud models
class GarageCreate(GarageBase):
    pass


class GarageUpdate(GarageBase):
    name: str | None = None
    location: str | None = None
    city: str | None = None
    capacity: int | None = None


class GaragePublic(GarageBase):
    id: int
