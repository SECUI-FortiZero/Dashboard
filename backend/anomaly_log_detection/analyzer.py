import os
import json
from openai import OpenAI
from .prompt import build_suspicious_log_prompt

# OpenAI 클라이언트
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def analyze_logs_with_ai(logs):
    """
    OpenAI API를 이용해 이상 로그 탐지
    """
    prompt = build_suspicious_log_prompt(logs)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a log analysis AI. Return JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content.strip()

        # JSON 검증
        return json.loads(result)

    except Exception as e:
        print(f"❌ OpenAI API 오류: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": []
        }
