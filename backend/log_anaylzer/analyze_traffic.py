from fetcher import fetch_from_api
from analyzer import analyze_logs

def generate_markdown_report(content):
    """
    최종 분석 결과를 마크다운 형식 텍스트로 터미널 출력
    """
    print("\n===================== 📊 트래픽 로그 분석 보고서 =====================\n")
    print(content)
    print("\n====================================================================\n")

if __name__ == "__main__":
    print(">>> 일반 트래픽 로그 분석을 시작합니다...")
    
    # /api/logs API에서 원하는 기간(예: "hourly", "daily", "weekly")의 로그를 가져옴
    params = {
        "range": "10min" 
    }
    logs = fetch_from_api("/api/logs", params=params)

    if not logs:
        print("분석할 트래픽 로그 데이터가 없습니다.")
    else:
        # 가져온 로그를 분석 함수에 전달
        result = analyze_logs(logs)
        generate_markdown_report(result)