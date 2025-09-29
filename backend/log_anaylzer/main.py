from fetcher import fetch_from_api
from masker import apply_masking
from analyzer import analyze_logs

def generate_markdown_report(content):
    """
    최종 분석 결과를 마크다운 형식 텍스트로 터미널 출력
    """
    print("\n===================== 📊 로그 분석 보고서 (Markdown) =====================\n")
    print(content)
    print("\n==========================================================================\n")

if __name__ == "__main__":
    # 1. API에서 로그 가져오기 (cloud / daily), 원하는 형식으로 지정해주면 됨
    logs = fetch_from_api("/api/policy?type=cloud&range=daily", limit=50)

    if not logs:
        print("분석할 로그 데이터가 없습니다.")
    else:
        # 2. 민감정보 마스킹
        masked_logs = apply_masking(logs, log_type="log_common")

        # 3. OpenAI 분석
        result = analyze_logs(masked_logs)

        # 4. 보고서 출력
        generate_markdown_report(result)
