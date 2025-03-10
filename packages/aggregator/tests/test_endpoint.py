from fastapi.testclient import TestClient
from aggregator.aggregator import app
from aggregator.utils import create_legislation_info,  filter_legislation_information

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
    response = client.post(
        "/upload-selected-legislation",
        json={
            "user_id": "123",
            "legislation": ["Legislation1", "Legislation2"]
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() is None


def test_create_legislation_info():
    legislation_info = create_legislation_info("Test Legislation", "https://test-legislation.com")
    assert legislation_info.name == "Test Legislation"
    assert legislation_info.url == "https://test-legislation.com"
    assert legislation_info.article_extract(1) == "art-1-test_legislation"


def test_filter_legislation_information():
    labels = ["GDPR"]
    updated_info =  filter_legislation_information(labels)
    assert "gdpr" in updated_info
    assert updated_info["gdpr"].name == "GDPR"
    assert updated_info["gdpr"].url == "https://gdpr-info.eu/"
    assert updated_info["gdpr"].article_extract(1) == "art-1-gdpr"
    assert "eu_ai" not in updated_info


def test_filter_legislation_information_empty():
    labels = []
    updated_info =  filter_legislation_information(labels)
    assert updated_info == {}


def test_filter_legislation_information_multiple():
    labels = ["GDPR", "EU AI Act"]
    updated_info =  filter_legislation_information(labels)
    assert "gdpr" in updated_info
    assert "eu_ai" in updated_info
    assert updated_info["gdpr"].name == "GDPR"
    assert updated_info["eu_ai"].name == "EU AI Act"
