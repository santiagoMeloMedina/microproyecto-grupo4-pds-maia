from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["modelFamily"] == "fake-xgboost"
    assert body["threshold"] == 0.5


def test_catalog(client: TestClient) -> None:
    response = client.get("/api/v1/catalog")

    assert response.status_code == 200
    body = response.json()
    assert body["airlines"] == ["AA", "WN"]
    assert len(body["days"]) == 7


def test_predict(client: TestClient) -> None:
    payload = {
        "airline": "WN",
        "airportFrom": "DAL",
        "airportTo": "HOU",
        "dayOfWeek": 3,
        "time": 840,
        "length": 60,
    }

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["probability"] <= 1.0
    assert body["band"] in {"bajo", "medio", "alto"}
    assert body["references"]


def test_predict_rejects_same_airport(client: TestClient) -> None:
    payload = {
        "airline": "WN",
        "airportFrom": "DAL",
        "airportTo": "DAL",
        "dayOfWeek": 3,
        "time": 840,
        "length": 60,
    }

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422


def test_schedule_slots_filters_by_airline(client: TestClient) -> None:
    response = client.get("/api/v1/schedule-slots", params={"airline": "AA"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["airline"] == "AA"


def test_schedule_slots_summary(client: TestClient) -> None:
    response = client.get("/api/v1/schedule-slots/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["flightsInSelection"] == 4
    assert body["totalFlights"] == 4


def test_schedule_slots_breakdown_by_airline(client: TestClient) -> None:
    response = client.get(
        "/api/v1/schedule-slots/breakdown", params={"by": "airline"}
    )

    assert response.status_code == 200
    body = response.json()
    assert {item["key"] for item in body} == {"AA", "WN"}


def test_schedule_slots_breakdown_rejects_invalid_by(client: TestClient) -> None:
    response = client.get(
        "/api/v1/schedule-slots/breakdown", params={"by": "not-a-column"}
    )

    assert response.status_code == 422


def test_schedule_slots_drift(client: TestClient) -> None:
    response = client.get("/api/v1/schedule-slots/drift")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_health_reporta_la_version_del_modelo(client: TestClient) -> None:
    """La version del modelo es distinta de la de la API y debe viajar aparte."""
    body = client.get("/api/v1/health").json()

    assert body["modelVersion"] == "0.0.0-fake"
    assert body["apiVersion"] != body["modelVersion"]


def test_cors_permite_el_origen_del_tablero(client: TestClient) -> None:
    """Regresion: pydantic normaliza AnyHttpUrl agregando una barra final.

    El navegador manda Origin sin barra y Starlette compara por igualdad
    exacta, asi que con la barra el tablero quedaba sin datos aunque la API
    respondiera bien por curl.
    """
    response = client.options(
        "/api/v1/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_los_origenes_cors_no_llevan_barra_final() -> None:
    from app.config import settings

    assert settings.cors_origins
    assert all(not origen.endswith("/") for origen in settings.cors_origins)
