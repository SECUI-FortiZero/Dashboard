import os
from pymongo import MongoClient

# .env 파일에 정의된 MONGO_URI를 사용하여 데이터베이스에 연결
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)

# URI에 명시된 데이터베이스를 기본으로 사용
db = client.get_default_database()

# 사용할 컬렉션(RDBMS의 테이블과 유사) 정의
raw_logs_collection = db.raw_logs
threat_logs_collection = db.threats