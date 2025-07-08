import pytest
from proxy_flask import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

def test_proxy_endpoint(client):
    # Sostituisci '/proxy?url=https://httpbin.org/get' con il vero endpoint del tuo proxy se diverso
    response = client.get('/proxy?url=https://httpbin.org/get')
    assert response.status_code == 200
    # Puoi aggiungere altri assert per verificare il contenuto della risposta
