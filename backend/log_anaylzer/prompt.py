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
def build_threat_json_prompt(masked_logs):
    log_string = json.dumps(masked_logs, indent=2, ensure_ascii=False)
    return f"""
You are a security expert who detects threats from log data and responds only in JSON format.
Analyze the following log data and extract only the logs that are highly likely to be security threats.

Threat detection criteria:
- Access attempts from outside to sensitive internal ports (e.g., 22, 3389, 6379).
- Port scanning activities.
- Access from known malicious IPs or unusual geolocations.

Your response MUST be a JSON array of objects. Each object must contain the following keys: "timestamp", "src_ip", "dst_ip", "dst_port", "protocol", "reason".
The "reason" field should be a brief explanation in Korean of why you identified it as a threat.

If no threats are detected, return an empty array `[]`.
Do not include any other text or explanations outside of the JSON array.

Example of a valid response:
[
  {{
    "timestamp": "2025-09-29T16:47:25",
    "src_ip": "1.183.69.193",
    "dst_ip": "10.20.1.121",
    "dst_port": "23",
    "protocol": "6",
    "reason": "외부에서 내부망으로 비암호화 프로토콜인 Telnet(23) 접속 시도."
  }}
]

--- Log Data ---
{log_string}
--- Analysis Start ---
"""