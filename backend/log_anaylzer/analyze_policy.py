from fetcher import fetch_from_api
from analyzer import analyze_logs

def generate_markdown_report(content):
    """
    최종 분석 결과를 마크다운 형식 텍스트로 터미널 출력
    """
    print("\n===================== 📊 정책 로그 분석 보고서 =====================\n")
    print(content)
    print("\n====================================================================\n")

if __name__ == "__main__":
    print(">>> 정책 변경 로그 분석을 시작합니다...")

    # /api/policy API에서 원하는 타입/기간의 정책 로그를 가져옴
    params = {
        "type": "cloud",      # "cloud" 또는 "onprem"
        "range": "10min"     # "10min", "daily", "weekly" 등
    }
    logs = fetch_from_api("/api/policy", params=params)

    if not logs:
        print("분석할 정책 로그 데이터가 없습니다.")
    else:
        # 정책 로그도 동일한 분석 함수에 전달
        result = analyze_logs(logs)
        generate_markdown_report(result)