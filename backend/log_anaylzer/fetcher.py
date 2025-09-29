import os
import requests
from dotenv import load_dotenv

# .env 로드
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")

def fetch_from_api(endpoint: str, limit: int = 50):
    """
    지정된 endpoint에서 데이터를 가져옵니다.
    endpoint 예: /api/policy?type=cloud&range=daily
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"  # baseurl + endpoint 합치기
        response = requests.get(url, params={"limit": limit}, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"API 호출 오류: {e}")
        return []
