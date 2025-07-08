import pytest
import json
from proxy import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_version_endpoint(client):
    response = client.get('/version')
    assert response.status_code == 200
    data = response.get_json()
    assert data['platform'] == 'Residorg'
    assert data['version'] == '3.0.1'
