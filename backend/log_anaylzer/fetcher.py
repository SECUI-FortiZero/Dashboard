
import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")

def fetch_from_api(path: str, params: dict | None = None):
    """
    지정된 경로(path)와 파라미터(params)로 API 서버에서 데이터를 가져옵니다.

    Args:
        path (str): API 경로 (예: "/api/logs", "/api/policy")
        params (dict, optional): 쿼리 파라미터 딕셔너리 (예: {"range": "daily"}). Defaults to None.
    """
    try:
        url = f"{API_BASE_URL}{path}"
        
        # requests 라이브러리가 params 딕셔너리를 안전하게 URL 쿼리 스트링으로 만들어줍니다.
        # 예: {"range":"daily"} -> ?range=daily
        response = requests.get(url, params=params, timeout=60)
        
        response.raise_for_status()
        return response.json().get("data", [])
    
    except requests.exceptions.RequestException as e:
        print(f"API 호출 오류 ({url}): {e}")
        return []