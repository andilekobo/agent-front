import traceback
from fastapi.testclient import TestClient

try:
    from main import app
    client = TestClient(app)
    resp = client.post("/agent", json={"message": "Find junior software developer jobs in Johannesburg"})
    print("STATUS:", resp.status_code)
    print("TEXT:", resp.text)
except Exception as e:
    print("EXCEPTION:")
    traceback.print_exc()