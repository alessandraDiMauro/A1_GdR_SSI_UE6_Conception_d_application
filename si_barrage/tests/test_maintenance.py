from fastapi.testclient import TestClient
from si_barrage.main import app

client = TestClient(app)

def test_get_tickets():
    """
    Test the /maintenance/tickets endpoint.
    """
    response = client.get("/maintenance/tickets")
    assert response.status_code == 200
    assert response.json() == {"message": "Tickets de maintenance"}

