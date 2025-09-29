from fetcher_policy import fetch_policies
from masking_policy import apply_policy_masking
from analyzer_policy import analyze_policies
from decorators import pipeline

@pipeline(fetcher=fetch_policies, masker=apply_policy_masking, analyzer=analyze_policies)
def run_policy_analysis(policy_type="cloud", range_type="daily"):
    pass  # 데코레이터가 실제 실행 흐름을 처리

if __name__ == "__main__":
    result = run_policy_analysis(policy_type="cloud", range_type="daily")

    print("\n===================== 🛡️ 정책 분석 보고서 (Markdown) =====================\n")
    print(result)
    print("\n============================================================================\n")
