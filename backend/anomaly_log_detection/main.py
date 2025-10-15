import json
from detector.fetcher import fetch_logs
from detector.analyzer import analyze_logs_with_ai

if __name__ == "__main__":
    # 1. DB API에서 로그 가져오기
    logs = fetch_logs(log_type="cloud", range_type="daily", limit=100)

    if not logs:
        print(json.dumps({
            "status": "error",
            "message": "분석할 로그가 없습니다.",
            "logs": []
        }, indent=2, ensure_ascii=False))
    else:
        # 2. AI 분석 수행
        result = analyze_logs_with_ai(logs)

        # 3. 결과 JSON 출력
        print(json.dumps(result, indent=2, ensure_ascii=False))
