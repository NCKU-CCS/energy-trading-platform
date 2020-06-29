import requests
bearer = "Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5MzQzMjU1MywiZXhwIjoxNTkzNTE4OTUzfQ.IjZjNzMxZmJhZDY1ZWU3NTEzYmM4NGVkN2FiNmRjNWE5Mjg2MTNlNzdjNjA2OGJiZWVjNWEwMzFlYWVkN2M3YjUi.Bwy8vV9RPXp2gUWUJBLRHrFBgoxsTwj5zyMnFcp7LCfPzjoSEWzde0cAMfd1Pe-EikP9mNoxjl22JywQke78Sw"

res = requests.options("http://140.116.247.117:5000/socket/association", headers={"API-version": "0.1", "Authorization": bearer}, json={"event": "association"})
print(res.status_code)
print(res.json())
