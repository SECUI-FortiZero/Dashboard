from fetcher import fetch_from_api
from analyzer import analyze_logs
# ... (이전과 동일한 나머지 import 및 함수 정의) ...

def generate_markdown_report(content):
    print("\n===================== 📊 로그 분석 보고서 (Markdown) =====================\n")
    print(content)
    print("\n==========================================================================\n")

if __name__ == "__main__":
    # --- 일반 트래픽 로그 분석 예시 ---
    print(">>> 일반 트래픽 로그(최근 1시간) 분석을 시작합니다...")
    
    # 1. /api/logs API에서 최근 1시간(hourly) 로그를 가져옴
    traffic_logs = fetch_from_api("/api/logs", params={"range": "weekly"})

    if not traffic_logs:
        print("분석할 트래픽 로그 데이터가 없습니다.")
    else:
        # 2. 가져온 로그를 분석 함수에 전달
        # (데코레이터가 마스킹, 프롬프트 생성 등을 처리)
        traffic_result = analyze_logs(traffic_logs)
        generate_markdown_report(traffic_result)

    
    # --- 정책 변경 로그 분석 예시 ---
    print("\n>>> 클라우드 정책 변경 로그(최근 7일) 분석을 시작합니다...")

    # 1. /api/policy API에서 클라우드(cloud) 정책 로그를 최근 7일(weekly)치 가져옴
    policy_logs = fetch_from_api("/api/policy", params={"type": "onprem", "range": "weekly"})

    if not policy_logs:
        print("분석할 정책 로그 데이터가 없습니다.")
    else:
        # 2. 정책 로그도 동일한 분석 함수에 전달 가능
        policy_result = analyze_logs(policy_logs)
        generate_markdown_report(policy_result)