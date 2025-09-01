# 1. 베이스 이미지 선택 (가벼운 파이썬 3.9)
FROM python:3.9-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일(requirements.txt) 복사
COPY requirements.txt .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 현재 폴더의 모든 파일을 작업 디렉토리로 복사
COPY . .

# 6. 컨테이너가 시작될 때 실행할 명령 정의
CMD ["python", "run.py"]