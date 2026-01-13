from fastapi.testclient import TestClient
from si_barrage.main import app

client = TestClient(app)

def test_get_releves():
    """
    Test the /meteo/releves endpoint.
    """
    response = client.get("/meteo/releves")
    assert response.status_code == 200
    assert response.json() == {"message": "Relevés météo"}

