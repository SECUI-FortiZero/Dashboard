import json

def build_log_analysis_prompt(masked_logs):
    log_string = json.dumps(masked_logs, indent=2, ensure_ascii=False)
    return f"""
당신은 로그 분석 전문가입니다.  
다음은 'log_common' 테이블에서 추출된 마스킹된 로그 데이터입니다.  

이 로그를 분석하여 다음 항목을 작성해 주세요:

1. **분석 요약**: ONPREM과 CLOUD 환경 구분 요약 (1~2 문장)  
2. **주요 발견 사항**: 주목할 이벤트 3가지  
3. **에러 및 경고 로그**: 'level'이 ERROR/WARN인 항목 요약  
4. **보안 관련 이벤트**: login, delete_user 등 보안 이벤트 요약  
5. **대응 방안 및 조치**: 현재 상황에 대해 보안/운영 관점에서 필요한 조치 사항을 구체적으로 제안  

결과는 **마크다운 형식**으로 정리하세요.

--- 로그 데이터 ---
{log_string}
--- 분석 시작 ---
"""
