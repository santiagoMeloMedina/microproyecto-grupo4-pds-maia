from __future__ import annotations

from typing import Optional

import pandas as pd

from app.services.artifacts import Artifacts

DIAS = {1: "Lunes", 2: "Martes", 3: "Miercoles", 4: "Jueves",
        5: "Viernes", 6: "Sabado", 7: "Domingo"}


def apply_filters(
    data: pd.DataFrame,
    *,
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = None,
    slot: Optional[str] = None,
) -> pd.DataFrame:
    if airline:
        data = data[data["Airline"] == airline]
    if route:
        data = data[data["Ruta"] == route]
    if day_of_week is not None:
        data = data[data["DayOfWeek"] == day_of_week]
    if slot:
        data = data[data["Franja"] == slot]
    return data


def ranked_slots(
    artifacts: Artifacts,
    *,
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = None,
    slot: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """Franjas de itinerario ordenadas por riesgo descendente (la respuesta operativa
    del tablero: sobre que combinaciones concretas priorizar refuerzo)."""
    selection = apply_filters(
        artifacts.slots, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )
    if selection.empty:
        return []

    top = selection.nlargest(limit, "riesgo")
    rows = []
    for row in top.itertuples():
        risk = float(row.riesgo)
        rows.append(
            {
                "airline": row.Airline,
                "route": row.Ruta,
                "airport_from": row.AirportFrom,
                "airport_to": row.AirportTo,
                "day_of_week": int(row.DayOfWeek),
                "day_label": DIAS[int(row.DayOfWeek)],
                "slot": row.Franja,
                "time": int(row.Time),
                "length": int(row.Length),
                "flights": int(row.vuelos),
                "observed_rate": float(row.tasa_observada),
                "risk": risk,
                "band": artifacts.band(risk),
            }
        )
    return rows


def summary(
    artifacts: Artifacts,
    *,
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = None,
    slot: Optional[str] = None,
) -> dict:
    """KPIs de la seleccion activa (no del historico completo): ver dashboard/app.py."""
    flights = apply_filters(
        artifacts.flights, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )
    selection = apply_filters(
        artifacts.slots, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )

    if flights.empty:
        return {
            "delay_rate": None,
            "flights_in_selection": 0,
            "total_flights": int(len(artifacts.flights)),
            "schedule_slots": 0,
            "slots_over_threshold": 0,
            "slots_in_selection": 0,
            "roc_auc": artifacts.metadata.get("metricas_prueba", {}).get("roc_auc"),
            "threshold": artifacts.threshold,
        }

    n_slots = flights.groupby(
        ["Airline", "Ruta", "DayOfWeek", "Franja"], observed=True
    ).ngroups
    over_threshold = (
        int((selection["riesgo"] >= artifacts.threshold).sum()) if not selection.empty else 0
    )

    return {
        "delay_rate": float(flights["Delay"].mean()),
        "flights_in_selection": int(len(flights)),
        "total_flights": int(len(artifacts.flights)),
        "schedule_slots": n_slots,
        "slots_over_threshold": over_threshold,
        "slots_in_selection": int(len(selection)),
        "roc_auc": artifacts.metadata.get("metricas_prueba", {}).get("roc_auc"),
        "threshold": artifacts.threshold,
    }


_BREAKDOWN_COLUMNS = {
    "airline": "Airline",
    "slot": "Franja",
    "day": "DayOfWeek",
}


def breakdown(
    artifacts: Artifacts,
    by: str,
    *,
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = None,
    slot: Optional[str] = None,
    top: Optional[int] = None,
) -> list[dict]:
    """Tasa de retraso agrupada por aerolinea, franja horaria o dia, con volumen.

    Ver dashboard/app.py::barras_tasa_volumen: el volumen viaja junto a la tasa
    porque una tasa alta sobre pocos vuelos no es una senal accionable.
    """
    if by not in _BREAKDOWN_COLUMNS:
        raise ValueError(f"'by' debe ser uno de {sorted(_BREAKDOWN_COLUMNS)}")
    column = _BREAKDOWN_COLUMNS[by]

    flights = apply_filters(
        artifacts.flights, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )
    if flights.empty:
        return []

    grouped = flights.groupby(column, observed=True)["Delay"].agg(rate="mean", flights="size")
    grouped = grouped[grouped["flights"] > 0].sort_values("rate", ascending=False)
    if top:
        grouped = grouped.nlargest(top, "flights").sort_values("rate", ascending=False)

    return [
        {
            "key": str(key),
            "label": DIAS[int(key)] if by == "day" else str(key),
            "rate": float(row["rate"]),
            "flights": int(row["flights"]),
        }
        for key, row in grouped.iterrows()
    ]


def drift(
    artifacts: Artifacts,
    *,
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = None,
    slot: Optional[str] = None,
) -> list[dict]:
    """Evolucion diaria de la tasa de retraso en la seleccion, para ver por que el
    modelo caduca."""
    flights = apply_filters(
        artifacts.flights, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )
    if flights.empty:
        return []

    daily = flights.groupby("DiaCalendario")["Delay"].mean()
    return [{"day": int(day), "rate": float(rate)} for day, rate in daily.items()]
