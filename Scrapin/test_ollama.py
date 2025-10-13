from fastapi.testclient import TestClient
from ollama_app import app
import pytest
from requests.exceptions import Timeout

client = TestClient(app)

def test_process_fallo(fallo_file: str) -> None:
    with open(fallo_file, 'r', encoding='utf-8') as file:
        fallo_text = file.read() 

    print('Input fallo text: ', fallo_text[:20])  # Print first 200 characters
    payload = {"fallo": fallo_text}
    url = "/process_fallo"
    with pytest.raises(Timeout):
        response = client.post(url=url, json=payload, timeout=10)
    assert response.status_code == 200, f'Expected 200 but got {response.status_code}'
    print('Response: ', response.json())

if __name__ == "__main__":
    test_process_fallo('fallos/sentencia_1.txt')