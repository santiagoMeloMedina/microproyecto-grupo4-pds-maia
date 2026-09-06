from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from airlines_ml.data import DIA_FIN_VALIDACION, OBJETIVO, cargar_crudo, limpiar

TARGET_COLUMN = OBJETIVO
CATEGORICAL_COLUMNS = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Route", "AirlineTimeBucket"]
FEATURE_COLUMNS = [
    "Airline",
    "AirportFrom",
    "AirportTo",
    "DayOfWeek",
    "Time",
    "Length",
    "Route",
    "AirlineDowPrevDelay",
    "AirlineTimeBucket",
]

MIN_ROUTE_COUNT = 50
OTHER_ROUTE_LABEL = "OTHER"
NO_PREV_FLIGHT_VALUE = -1
TIME_BUCKET_HOURS = 2


def load_data(data_path: str | None) -> pd.DataFrame:
    return limpiar(cargar_crudo(data_path))


def _add_airline_dow_prev_delay(df: pd.DataFrame) -> pd.DataFrame:
    sorted_df = df.sort_values(["Airline", "DayOfWeek", "Time"])
    prev_delay = sorted_df.groupby(["Airline", "DayOfWeek"])[TARGET_COLUMN].shift(1)
    df["AirlineDowPrevDelay"] = prev_delay.reindex(df.index).fillna(NO_PREV_FLIGHT_VALUE).astype(int)
    return df


def _add_airline_time_bucket(df: pd.DataFrame) -> pd.DataFrame:
    hour = (df["Time"] // 60) % 24
    df["AirlineTimeBucket"] = df["Airline"].astype(str) + "_" + (hour // TIME_BUCKET_HOURS).astype(str)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Route"] = df["AirportFrom"] + "_" + df["AirportTo"]
    route_counts = df["Route"].value_counts()
    rare_routes = route_counts[route_counts < MIN_ROUTE_COUNT].index
    df.loc[df["Route"].isin(rare_routes), "Route"] = OTHER_ROUTE_LABEL

    df = _add_airline_dow_prev_delay(df)
    df = _add_airline_time_bucket(df)

    for column in CATEGORICAL_COLUMNS:
        df[column] = df[column].astype("category")

    return df[FEATURE_COLUMNS + [TARGET_COLUMN, "DiaCalendario"]]


def prepare_dataset(data_path: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = build_features(load_data(data_path))
    dia = df["DiaCalendario"]
    train_df = df.loc[dia < DIA_FIN_VALIDACION].drop(columns=["DiaCalendario"]).reset_index(drop=True)
    test_df = df.loc[dia >= DIA_FIN_VALIDACION].drop(columns=["DiaCalendario"]).reset_index(drop=True)
    return train_df, test_df
