
from typing import Generator

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


class FakeModel:
    """predict_proba determinista: mayor Time => mayor riesgo, para poder
    aserciones estables sin depender del modelo real."""

    def predict_proba(self, frame: pd.DataFrame):
        risk = (frame["Time"] / 1439).clip(0.05, 0.95).to_numpy()
        return pd.DataFrame({0: 1 - risk, 1: risk}).to_numpy()


class FakeArtifacts:
    def __init__(self) -> None:
        self.model = FakeModel()
        self.metadata = {
            "familia": "fake-xgboost",
            "umbral": 0.5,
            "banda_alta": 0.7,
            "metricas_prueba": {"roc_auc": 0.7},
        }
        self.threshold = 0.5
        self.high_band_threshold = 0.7
        self.model_family = "fake-xgboost"

        self.flights = pd.DataFrame(
            {
                "Airline": ["WN", "WN", "AA", "AA"],
                "AirportFrom": ["DAL", "DAL", "JFK", "JFK"],
                "AirportTo": ["HOU", "HOU", "LAX", "LAX"],
                "Ruta": ["DAL-HOU", "DAL-HOU", "JFK-LAX", "JFK-LAX"],
                "DayOfWeek": [3, 3, 5, 5],
                "Franja": ["12-18", "12-18", "18-24", "18-24"],
                "Time": [840, 850, 1200, 1210],
                "Length": [60, 65, 320, 310],
                "Delay": [1, 0, 0, 1],
                "DiaCalendario": [1, 2, 1, 2],
            }
        )
        self.slots = self._build_slots()

    def _build_slots(self) -> pd.DataFrame:
        from app.services.artifacts import CLAVE_FRANJA

        grouped = (
            self.flights.groupby(CLAVE_FRANJA, observed=True)
            .agg(
                Time=("Time", "median"),
                Length=("Length", "median"),
                vuelos=("Delay", "size"),
                tasa_observada=("Delay", "mean"),
            )
            .reset_index()
        )
        grouped["Time"] = grouped["Time"].astype(int)
        grouped["Length"] = grouped["Length"].astype(int)
        grouped["Ruta"] = grouped["AirportFrom"] + "-" + grouped["AirportTo"]
        grouped["riesgo"] = self.model.predict_proba(grouped)[:, 1]
        return grouped

    def band(self, probability: float) -> str:
        if probability >= self.high_band_threshold:
            return "alto"
        if probability >= self.threshold:
            return "medio"
        return "bajo"

    def slot_of(self, minutes: int) -> str:
        return _franja_de(minutes)


def _franja_de(minutos: int) -> str:
    for tope, etiqueta in [(360, "00-06"), (720, "06-12"), (1080, "12-18")]:
        if minutos < tope:
            return etiqueta
    return "18-24"


@pytest.fixture()
def fake_artifacts() -> FakeArtifacts:
    return FakeArtifacts()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, fake_artifacts: FakeArtifacts) -> Generator:
    monkeypatch.setattr("app.api.get_artifacts", lambda: fake_artifacts)
    with TestClient(app) as _client:
        yield _client
