import json

def build_suspicious_log_prompt(logs):
    """
    이상 로그 탐지를 위한 OpenAI 프롬프트 생성 
    (탐지 개수 ≤ 5, 우선순위 적용 + severity 필드 추가)
    """
    logs_str = json.dumps(logs, indent=2, ensure_ascii=False)
    return f"""
당신은 보안 로그 분석 전문가입니다.
다음 JSON 로그 데이터를 분석하여 "이상 로그"만 추려주세요.

⚠️ 반드시 조건을 지켜주세요:
1. 탐지된 개수는 최대 5개 이내로 제한합니다.
2. 탐지 우선순위는 아래와 같습니다:
   - 1순위: level이 "ERROR"인 로그
   - 2순위: level이 "WARN"인 로그
   - 3순위: login, delete_user 같은 보안 관련 이벤트
3. 각 로그에는 "reason" 필드를 추가하세요.
   - reason: 해당 로그가 의심스러운 이유를 짧게 한 줄로 설명
4. 각 로그에는 "severity" 필드를 추가하세요.
   - severity: "Critical", "High", "Medium", "Low" 중 하나로 분류
   - 기준 예시:
     * Critical: 즉각적인 보안 위협 (예: DB 삭제, 관리자 계정 탈취 시도)
     * High: 시스템 오류, 인증 실패 반복, 의심스러운 접근
     * Medium: 비정상적인 동작, 반복된 경고
     * Low: 경미한 이슈, 참고용 경고
5. 출력은 반드시 JSON 형식만 반환하세요.

출력 스키마:
{{
  "status": "success",
  "detected": <탐지된 개수>,
  "logs": [
    {{
      "timestamp": "string",
      "source_ip": "string",
      "user": "string",
      "action": "string",
      "detail": "string",
      "reason": "짧막한 설명",
      "severity": "Critical|High|Medium|Low"
    }}
  ]
}}

--- 로그 데이터 ---
{logs_str}
--- 분석 시작 ---
"""
