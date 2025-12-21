import requests

url = "http://127.0.0.1:5000/review"

payload = {
    "code": "def add(a,b): return a+b"
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print("Response:", response.json())
