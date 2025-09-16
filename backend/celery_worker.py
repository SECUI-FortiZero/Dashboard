import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Celery 앱 생성 및 설정
celery_app = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND'),
    # 실행할 작업들이 정의된 파일을 'include'에 추가합니다.
    include=['app.tasks']
)