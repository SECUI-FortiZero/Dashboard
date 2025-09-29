from functools import wraps
from fetcher import fetch_logs_from_api
from masking import mask_common
from prompt import build_log_analysis_prompt

def log_analyzer(func):
    @wraps(func)
    def wrapper(log_type="log_common", limit=50, *args, **kwargs):
        logs = fetch_logs_from_api(log_type, limit)
        if not logs:
            return "분석할 로그 데이터가 없습니다."

        # 마스킹 처리
        masked_logs = [mask_common(log) for log in logs]

        # 프롬프트 생성
        prompt = build_log_analysis_prompt(masked_logs)

        # 분석 함수 실행
        return func(prompt, *args, **kwargs)
    return wrapper
