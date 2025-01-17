import pytest
from fastapi.testclient import TestClient
from tests.modelAPI.model.scikit_mock import app
from pytest_httpserver import HTTPServer
import aignostic

client = TestClient(app)

def test_server():
    response = client.get("/hello")
    print(response)
    assert response.status_code == 200, response.text
    assert response.text == '"Hello World"'
    assert 1 == 2

# def test_response():
#     # post empty pandas ndataframe
#     response = client.post("/predict", json={})
#     assert response.status_code == 422
    

def test_nothing():
    pass