import os
import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5001")

def fetch_logs(log_type="cloud", range_type="daily", limit=50):
    """
    DB API에서 정책 로그 불러오기
    GET /api/policy?type={log_type}&range={range_type}
    """
    url = f"{API_BASE_URL}/api/policy?type={log_type}&range={range_type}"
    try:
        response = requests.get(url, params={"limit": limit})
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.RequestException as e:
        print(f"❌ API 호출 오류: {e}")
        return []
