import requests

res = requests.post("http://140.116.247.117:5000/login", json={"account": "SGESC_D_BEMS", "password": "test"})
print(res.status_code)
print(res.json())
