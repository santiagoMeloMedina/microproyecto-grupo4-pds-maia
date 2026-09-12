from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app import __version__, schemas
from app.config import settings
from app.services import slots as slots_service
from app.services.artifacts import get_artifacts

api_router = APIRouter()

MIN_ROUTE_FLIGHTS = 500


@api_router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """Estado de la API y del modelo cargado."""
    artifacts = get_artifacts()
    return {
        "name": settings.PROJECT_NAME,
        "api_version": __version__,
        "model_version": artifacts.model_version,
        "model_family": artifacts.model_family,
        "threshold": artifacts.threshold,
        "high_band_threshold": artifacts.high_band_threshold,
    }


@api_router.get("/catalog", response_model=schemas.Catalog, status_code=200)
def catalog() -> dict:
    """Aerolineas, aeropuertos, rutas frecuentes y dias validos para el formulario
    de prediccion y los filtros del tablero, derivados del historico cargado."""
    artifacts = get_artifacts()
    flights = artifacts.flights

    route_counts = flights.groupby("Ruta", observed=True).size()
    routes = sorted(route_counts[route_counts >= MIN_ROUTE_FLIGHTS].index.tolist())

    return {
        "airlines": sorted(flights["Airline"].unique().tolist()),
        "airports": sorted(set(flights["AirportFrom"]) | set(flights["AirportTo"])),
        "routes": routes,
        "days": [
            {"value": value, "label": label}
            for value, label in slots_service.DIAS.items()
        ],
    }


@api_router.post("/predict", response_model=schemas.PredictionResult, status_code=200)
def predict(input_data: schemas.PredictionRequest) -> dict:
    """Riesgo estimado de retraso para un itinerario, con referencias historicas.

    Equivalente al callback 'evaluar' de dashboard/app.py: mismo modelo, mismas
    columnas de entrada (Airline, AirportFrom, AirportTo, DayOfWeek, Time, Length).
    """
    artifacts = get_artifacts()

    entry = pd.DataFrame(
        [
            {
                "Airline": input_data.airline,
                "AirportFrom": input_data.airport_from,
                "AirportTo": input_data.airport_to,
                "DayOfWeek": input_data.day_of_week,
                "Time": input_data.time,
                "Length": input_data.length,
            }
        ]
    )

    try:
        probability = float(artifacts.model.predict_proba(entry)[0, 1])
    except Exception as exc:  # modelo rechaza una categoria no vista, etc.
        logger.warning(f"Prediction error for input {input_data}: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    band = artifacts.band(probability)
    route = f"{input_data.airport_from}-{input_data.airport_to}"
    slot = artifacts.slot_of(input_data.time)
    flights = artifacts.flights

    candidates = {
        f"Historico {input_data.airline}": flights.loc[
            flights["Airline"] == input_data.airline, "Delay"
        ].mean(),
        f"Historico {route}": flights.loc[flights["Ruta"] == route, "Delay"].mean(),
        f"Historico franja {slot}": flights.loc[flights["Franja"] == slot, "Delay"].mean(),
        "Media global": flights["Delay"].mean(),
    }
    references = [
        {"label": label, "rate": float(rate)}
        for label, rate in candidates.items()
        if pd.notna(rate)
    ]

    return {
        "probability": probability,
        "band": band,
        "threshold": artifacts.threshold,
        "high_band_threshold": artifacts.high_band_threshold,
        "references": references,
        # La version del modelo, no la de la API: es lo que permite rastrear con
        # que artefacto se produjo una prediccion concreta.
        "model_version": artifacts.model_version,
    }


@api_router.get(
    "/schedule-slots", response_model=list[schemas.ScheduleSlot], status_code=200
)
def schedule_slots(
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = Query(None, ge=1, le=7),
    slot: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
) -> list[dict]:
    """Franjas de itinerario con mayor riesgo estimado, con los mismos cuatro
    filtros del tablero (aerolinea, ruta, dia, franja)."""
    artifacts = get_artifacts()
    return slots_service.ranked_slots(
        artifacts,
        airline=airline,
        route=route,
        day_of_week=day_of_week,
        slot=slot,
        limit=limit,
    )


@api_router.get(
    "/schedule-slots/summary", response_model=schemas.SlotsSummary, status_code=200
)
def schedule_slots_summary(
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = Query(None, ge=1, le=7),
    slot: Optional[str] = None,
) -> dict:
    """KPIs de la seleccion activa: tasa de retraso, vuelos, franjas y AUC del modelo."""
    artifacts = get_artifacts()
    return slots_service.summary(
        artifacts, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )


@api_router.get(
    "/schedule-slots/breakdown",
    response_model=list[schemas.SlotsBreakdownItem],
    status_code=200,
)
def schedule_slots_breakdown(
    by: str = Query(..., pattern="^(airline|slot|day)$"),
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = Query(None, ge=1, le=7),
    slot: Optional[str] = None,
    top: Optional[int] = Query(None, ge=1, le=50),
) -> list[dict]:
    """Tasa de retraso agrupada por aerolinea, franja horaria o dia, con volumen."""
    artifacts = get_artifacts()
    try:
        return slots_service.breakdown(
            artifacts,
            by,
            airline=airline,
            route=route,
            day_of_week=day_of_week,
            slot=slot,
            top=top,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get(
    "/schedule-slots/drift", response_model=list[schemas.DriftPoint], status_code=200
)
def schedule_slots_drift(
    airline: Optional[str] = None,
    route: Optional[str] = None,
    day_of_week: Optional[int] = Query(None, ge=1, le=7),
    slot: Optional[str] = None,
) -> list[dict]:
    """Evolucion diaria de la tasa de retraso en la seleccion activa (deriva del modelo)."""
    artifacts = get_artifacts()
    return slots_service.drift(
        artifacts, airline=airline, route=route, day_of_week=day_of_week, slot=slot
    )
