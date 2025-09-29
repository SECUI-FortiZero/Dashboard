from analyzer import analyze_logs

if __name__ == "__main__":
    # 로그 분석 실행
    result = analyze_logs(log_type="log_common", limit=50)

    # --- 마크다운 형식 그대로 터미널 출력 ---
    print("\n===================== 📊 로그 분석 보고서 (Markdown) =====================\n")
    print(result)
    print("\n==========================================================================\n")
