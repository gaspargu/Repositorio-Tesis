import requests

url = "http://127.0.0.1:8000/process_fallo"

with open("fallos/sentencia_1.txt", "r", encoding="utf-8") as f:
    fallo_text = f.read()

payload = {"fallo": fallo_text}

print("Sending request to:", url)
response = requests.post(url, json=payload)
print("Request sent.")
print("Status code:", response.status_code)
print("Response JSON:", response.json())