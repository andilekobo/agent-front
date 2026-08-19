import json
import urllib.request as u
import urllib.error as e

url = "http://localhost:8000/agent"
data = json.dumps({"message": "Find junior software developer jobs in Johannesburg"}).encode("utf-8")
req = u.Request(url, data=data, headers={"Content-Type": "application/json"})
try:
    resp = u.urlopen(req)
    print("STATUS", resp.getcode())
    print(resp.read().decode())
except e.HTTPError as he:
    print("HTTP", he.code)
    try:
        print(he.read().decode())
    except Exception:
        pass
except Exception as ex:
    print("ERROR", ex)
