
import os
from openai import OpenAI
import traceback
import json

# --- 서비스 내부 모듈 Import ---
from .log_service import get_logs
from .policy_service import get_policy_cloud, get_policy_onprem

# --- log_anaylzer 모듈 Import ---
from log_anaylzer.masking import mask_common
from log_anaylzer.prompt import build_log_analysis_prompt, build_threat_json_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _analyze_logs_with_ai(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a log analysis expert who responds in Korean."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("--- OpenAI API 호출 오류 ---")
        traceback.print_exc()
        return f"## 🤖 AI 분석 오류\n\nAPI 호출 중 문제가 발생했습니다: {e}"

# =======================================================
# 기능 1: 위협 로그만 JSON으로 추출
# =======================================================
def get_threat_logs_as_json(log_type: str = None, range_type: str = "daily", limit: int = 100) -> list:
    """
    로그를 조회하여 AI로 위협 로그만 분석하고, 결과를 JSON(리스트)으로 반환합니다.
    """
    logs = get_logs(range_type=range_type)

    if not logs:
        return []

    masked_logs = [mask_common(log) for log in logs]
    prompt = build_threat_json_prompt(masked_logs)

    ai_response = _analyze_logs_with_ai(prompt)

    try:
        # [수정] AI 응답이 문자열일 경우, JSON 부분만 추출하여 파싱하는 로직 추가
        if isinstance(ai_response, str):
            # AI 응답에서 첫 '{' 또는 '[' 와 마지막 '}' 또는 ']'를 찾아 그 사이의 내용만 추출
            json_start = -1
            if '[' in ai_response:
                json_start = ai_response.find('[')
            elif '{' in ai_response:
                json_start = ai_response.find('{')

            json_end = -1
            if ']' in ai_response:
                json_end = ai_response.rfind(']')
            elif '}' in ai_response:
                json_end = ai_response.rfind('}')

            if json_start != -1 and json_end != -1:
                # 순수한 JSON 문자열 부분만 잘라냄
                json_string = ai_response[json_start : json_end + 1]
                threat_list = json.loads(json_string)
            else:
                # 응답에서 JSON 형식을 전혀 찾지 못한 경우
                raise json.JSONDecodeError("Cannot find JSON object or array in AI response", ai_response, 0)
        else:
            # AI 라이브러리가 이미 파싱한 객체를 반환한 경우
            threat_list = ai_response
            
        return threat_list
    except json.JSONDecodeError as e:
        print("--- AI 응답 JSON 파싱 오류 ---")
        print(f"AI가 반환한 내용: {ai_response}")
        return [{"error": "AI가 유효한 JSON 형식으로 응답하지 않았습니다.", "details": str(e)}]

# =======================================================
# 기능 2: 트래픽 로그 상세 분석 보고서 생성
# =======================================================
def get_traffic_analysis_report(range_type: str = "daily", limit: int = 100) -> str:
    # [수정] log_service.get_logs에는 range_type만 전달합니다.
    # limit 파라미터는 여기서는 무시됩니다.
    logs = get_logs(range_type=range_type)

    if not logs:
        return "### 📝 분석 요약\n\n분석할 트래픽 로그 데이터가 없습니다."

    masked_logs = [mask_common(log) for log in logs]
    prompt = build_log_analysis_prompt(masked_logs)
    report = _analyze_logs_with_ai(prompt)
    return report

# =======================================================
# 기능 3: 정책 로그 상세 분석 보고서 생성
# =======================================================
def get_policy_analysis_report(policy_type: str, range_type: str = "daily") -> str:
    if policy_type == "cloud":
        logs = get_policy_cloud(range_type)
    elif policy_type == "onprem":
        logs = get_policy_onprem(range_type)
    else:
        return "### 📝 분석 오류\n\n정책 타입은 'cloud' 또는 'onprem'이어야 합니다."

    if not logs:
        return "### 📝 분석 요약\n\n분석할 정책 로그 데이터가 없습니다."

    masked_logs = [mask_common(log) for log in logs]
    prompt = build_log_analysis_prompt(masked_logs)
    report = _analyze_logs_with_ai(prompt)
    return report