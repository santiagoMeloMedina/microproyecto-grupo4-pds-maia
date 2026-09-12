from app.schemas.base import CamelModel


class DayOption(CamelModel):
    value: int
    label: str


class Catalog(CamelModel):
    airlines: list[str]
    airports: list[str]
    routes: list[str]
    days: list[DayOption]
