from typing import Optional

from app.schemas.base import CamelModel


class ScheduleSlot(CamelModel):
    airline: str
    route: str
    airport_from: str
    airport_to: str
    day_of_week: int
    day_label: str
    slot: str
    time: int
    length: int
    flights: int
    observed_rate: float
    risk: float
    band: str


class SlotsSummary(CamelModel):
    delay_rate: Optional[float]
    flights_in_selection: int
    total_flights: int
    schedule_slots: int
    slots_over_threshold: int
    slots_in_selection: int
    roc_auc: Optional[float]
    threshold: float
