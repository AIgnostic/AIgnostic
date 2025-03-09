import pytest
from fastapi.testclient import TestClient
from aggregator.aggregator import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == ["Welcome to the Aggregator Service"]

def test_fetch_frontend_information():
    response = client.get("/fetch-frontend-information")
    assert response.status_code == 200
    assert "legislation" in response.json()

def test_upload_selected_legislation():
    response = client.post("/upload-selected-legislation", json={"legislation": ["Legislation1", "Legislation2"]})
    print(response.json())
    assert response.status_code == 200
    assert response.json() == None
