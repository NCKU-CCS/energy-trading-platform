import requests

bearer="Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5MzI0OTU1NCwiZXhwIjoxNTkzMzM1OTU0fQ.IjZjNzMxZmJhZDY1ZWU3NTEzYmM4NGVkN2FiNmRjNWE5Mjg2MTNlNzdjNjA2OGJiZWVjNWEwMzFlYWVkN2M3YjUi.uAzW9BPsIFH-B-OgeoVs8EpIqvT4SnsF4WOhnuY6kq2Ie6MC-O3ztg43v9T5mS21J3Fax4vl2V5uRhEhHw5Yow"
res = requests.delete("http://140.116.247.117:5000/bidsubmit", headers={"Authorization":bearer}, json={"id":"26256af9-104a-459a-b1a9-3b6b115d1252", "bid_type":"sell", "start_time":"2020/06/27 20", "end_time":"2020/06/27 21"})

print(res.status_code)
print(res.json())
