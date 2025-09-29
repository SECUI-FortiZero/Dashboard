import os
import requests

API_PORT = os.environ.get("API_PORT", "5001")
BASE_URL = f"http://localhost:{API_PORT}"

def fetch_policies(policy_type: str, range_type: str, base_url: str = BASE_URL):
    """
    /api/policy?type={policy_type}&range={range_type} 형식으로 정책 데이터를 가져옵니다.
    """
    url = f"{base_url}/api/policy?type={policy_type}&range={range_type}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ API 호출 중 오류 발생: {e}")
        return []
