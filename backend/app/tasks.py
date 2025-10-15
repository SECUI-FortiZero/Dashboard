import os
import json
from celery_worker import celery_app
from app.database import raw_logs_collection, threat_logs_collection
from bson import ObjectId
import google.generativeai as genai

# .env 파일에서 Gemini API 키를 가져와 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@celery_app.task
def analyze_log_task(log_id_str):
    """Gemini API를 사용하여 로그를 분석하고 위협이면 DB에 저장하는 Celery Task"""
    
    log_id = ObjectId(log_id_str)
    log_entry = raw_logs_collection.find_one({'_id': log_id})

    # 로그가 없거나 이미 분석된 경우 작업을 종료
    if not log_entry or log_entry.get('analyzed', False):
        return f"Log {log_id_str} not found or already analyzed."

    log_message = log_entry.get('message', '')

    # Gemini 모델에 전달할 프롬프트
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are a cybersecurity expert specializing in firewall log analysis.
    Analyze the following log entry and determine if it constitutes a security threat.
    Threats can include, but are not limited to: brute-force attacks, port scanning, SQL injection probes, or malware communication patterns.

    Log entry: "{log_message}"

    Respond ONLY with a JSON object.
    If it is a threat, the JSON should have the keys "is_threat" (boolean true), "threat_type" (string), "severity" (string, one of "high", "medium", "low"), and "recommendation" (string).
    If it is not a threat, the JSON should have ONLY the key "is_threat" (boolean false).
    """

    try:
        response = model.generate_content(prompt)
        # Gemini 응답에서 JSON 부분만 깔끔하게 정리
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        ai_result = json.loads(cleaned_response)

        # AI가 위협이라고 판단한 경우, threat_logs 컬렉션에 저장
        if ai_result.get('is_threat'):
            threat_log = {
                "original_log_id": log_id,
                "timestamp": log_entry.get('timestamp'),
                "message": log_message,
                "ai_analysis": ai_result
            }
            threat_logs_collection.insert_one(threat_log)
        
        # 원본 로그에 'analyzed: true' 플래그를 업데이트하여 중복 분석 방지
        raw_logs_collection.update_one({'_id': log_id}, {'$set': {'analyzed': True}})
        return f"Log {log_id_str} analyzed. Threat found: {ai_result.get('is_threat', False)}"

    except Exception as e:
        # 분석 실패 시 에러 로깅
        raw_logs_collection.update_one({'_id': log_id}, {'$set': {'analyzed': 'failed', 'error': str(e)}})
        return f"Error analyzing log {log_id_str}: {str(e)}"