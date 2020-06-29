import requests

bearer = "Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5MzI0OTU1NCwiZXhwIjoxNTkzMzM1OTU0fQ.IjZjNzMxZmJhZDY1ZWU3NTEzYmM4NGVkN2FiNmRjNWE5Mjg2MTNlNzdjNjA2OGJiZWVjNWEwMzFlYWVkN2M3YjUi.uAzW9BPsIFH-B-OgeoVs8EpIqvT4SnsF4WOhnuY6kq2Ie6MC-O3ztg43v9T5mS21J3Fax4vl2V5uRhEhHw5Yow"
req = requests.get("http://140.116.247.117:5000/bidsubmit?per_page=10&page=5&bid_type=buy", headers={"Content-Type": "application/json", "Authorization": bearer})


print(req.status_code)
print(req.json())
