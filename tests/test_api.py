import pytest
from fastapi.testclient import TestClient
from api.main import app
from src.data.init_db import init_database


@pytest.fixture(scope="module")
def client():
    init_database()
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["database_status"] == "CONNECTED"


def test_players_endpoint(client):
    response = client.get("/players?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "players" in data
    assert len(data["players"]) <= 5


def test_market_summary_endpoint(client):
    response = client.get("/market/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_transfers"] > 0


def test_predictions_endpoint(client):
    payload = {
        "player_name": "Test Player",
        "player_market_value_eur": 25000000.0,
        "position": "Attack",
        "buying_club_name": "Arsenal"
    }
    response = client.post("/predictions/transfer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["transfer_probability"] <= 1.0
    assert "intelligence_score" in data
