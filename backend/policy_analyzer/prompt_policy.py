import json

def build_policy_analysis_prompt(masked_policies):
    policy_str = json.dumps(masked_policies, indent=2, ensure_ascii=False)
    return f"""
당신은 클라우드 및 온프레 정책 분석 전문가입니다.  
다음은 'policy' 테이블에서 추출된 보안 정책 데이터입니다.  

이 데이터를 분석하여 다음 항목을 보고하세요:

1. **정책 요약**: CLOUD와 ONPREM 환경 별 1~2문장 요약
2. **중복/모순 규칙 탐지**: 동일하거나 상충되는 규칙 여부
3. **위험 정책 탐지**: 과도하게 개방된 규칙(예: 0.0.0.0/0) 등
4. **주요 발견 사항**: 특이사항 3가지
5. **대응 방안 및 조치**: 보안 운영 관점에서 필요한 개선 조치 제안

결과는 **Markdown 형식**으로 정리하세요.

--- 정책 데이터 (JSON) ---
{policy_str}
--- 분석 시작 ---
"""
