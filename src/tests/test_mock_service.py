import re
from fastapi.testclient import TestClient
from manager_extension.mock_service.main import app


def test_main_url():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()['message'] == 'heh'
        assert re.fullmatch(r'^(\d|10)$', str(response.json()['delta'])) is not None
