from fastapi.testclient import TestClient
from si_barrage.main import app

client = TestClient(app)

def test_get_historique():
    """
    Test the /production/historique endpoint.
    """
    response = client.get("/production/historique")
    assert response.status_code == 200
    assert response.json() == {"message": "Historique de production"}

