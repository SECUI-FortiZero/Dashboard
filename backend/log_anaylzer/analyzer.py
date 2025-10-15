from openai import OpenAI
import os
from decorators import log_analyzer

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@log_analyzer
def analyze_logs(prompt, client=client):
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a log analysis expert who generates reports in Korean Markdown format."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
