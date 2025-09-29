from app.database import raw_logs_collection
from app.tasks import analyze_log_task
from datetime import datetime

def save_and_analyze_log(log_data):
    """로그를 DB에 저장하고, 비동기 AI 분석 작업을 시작시킵니다."""
    # 로그 수신 시 타임스탬프 추가
    log_data['timestamp'] = datetime.utcnow()
    log_data['analyzed'] = False
    
    result = raw_logs_collection.insert_one(log_data)
    inserted_id_str = str(result.inserted_id)
    
    # Celery 작업자에게 분석 요청 (ID만 전달하여 가볍게)
    analyze_log_task.delay(log_id_str=inserted_id_str)
    
    return inserted_id_str