# log_anaylzer/decorators.py (수정 후)

from functools import wraps
from masking import mask_common
from prompt import build_log_analysis_prompt

def log_analyzer(func):
    @wraps(func)
    def wrapper(logs: list, *args, **kwargs):
        if not logs:
            return "분석할 로그 데이터가 없습니다."

        masked_logs = [mask_common(log) for log in logs]
        prompt = build_log_analysis_prompt(masked_logs)
        
        return func(prompt, *args, **kwargs)
    return wrapper