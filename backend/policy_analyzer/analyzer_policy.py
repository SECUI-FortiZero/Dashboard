import os
from openai import OpenAI
from prompt_policy import build_policy_analysis_prompt

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_policies(masked_policies):
    """
    OpenAI API를 사용하여 정책 분석 보고서 생성
    """
    prompt = build_policy_analysis_prompt(masked_policies)
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a policy analysis expert. Output must be in Korean Markdown."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"## 오류\n\nAPI 호출 중 실패: {e}"
