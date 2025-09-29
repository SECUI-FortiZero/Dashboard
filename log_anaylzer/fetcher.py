import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

def fetch_logs_from_api(log_type, limit=50, base_url=API_BASE_URL):
    try:
        response = requests.get(f"{base_url}/logs", params={"type": log_type, "limit": limit})
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"API 호출 오류: {e}")
        return []
