# 🤖 AI 기반 하이브리드 방화벽 관리 시스템 - 백엔드

**하나의 정책(YAML)으로 온프레미스와 클라우드 방화벽을 통합 관리하고, AI를 통해 로그와 정책을 분석하는 시스템의 백엔드 API 서버입니다.**

## 📜 프로젝트 개요

이 프로젝트는 파편화된 방화벽 관리의 복잡성을 해결하는 것을 목표로 합니다. 사용자는 사람이 읽기 쉬운 YAML 형식으로 정책을 정의하기만 하면, 백엔드 시스템이 이를 해석하여 온프레미스 서버(iptables)와 클라우드(AWS Security Group)에 자동으로 적용합니다. 또한, 수집된 로그와 정책 변경 이력은 AI를 통해 자동 요약 및 리포트화되어 운영 효율을 극대화합니다.

---

## 🏗️ 시스템 아키텍처 및 흐름

```
1. 사용자 (웹 대시보드)
     |
     v
2. Flask 백엔드 API (정책 YAML 수신)
     |
     +--> 3a. Terraform 코드 생성 --> AWS API 호출 (Security Group 적용)
     |
     +--> 3b. Ansible 코드 생성 --> SSH 접속 (On-premise 서버 iptables 적용)
     |
     v
4. [CI/CD] GitHub Actions (main 브랜치 Push 시 자동 배포)
     |
     v
5. AWS EC2 서버 (Docker 컨테이너로 서비스 운영)
```

---

## 🛠️ 기술 스택

- **언어:** Python 3.9+
- **프레임워크:** Flask
- **컨테이너:** Docker
- **IaC & 자동화:** Terraform, Ansible
- **CI/CD:** GitHub Actions
- **클라우드:** AWS EC2

---

## 🚀 시작하기 (로컬 환경 설정)

이 프로젝트를 로컬 PC에서 실행하고 테스트하기 위한 가이드입니다.

### 1. 소스 코드 복제 (Clone)

```bash
git clone https://github.com/SECUI-FortiZero/Dashboard.git
cd backend
```

### 2. Python 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
# 가상환경 활성화 (Windows)
.\venv\Scripts\activate
```

### 3. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

프로젝트 루트의 `.env` 파일을 생성하고 아래 내용을 채워주세요. 민감한 정보이므로 이 파일은 Git에 포함되지 않습니다. 절대 절대 올리면 안됩니다.

`.env.example`

```
# AWS Credentials
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY

# OpenAI API Key (AI 기능 개발 시 필요)
OPENAI_API_KEY=YOUR_OPENAI_KEY

# Flask Debug Mode
FLASK_DEBUG=1
```

---

## 🧪 로컬에서 테스트하기

### 1. 백엔드 서버 실행

아래 명령어로 로컬 테스트 서버를 시작합니다.

```bash
python run.py
```

- 서버가 `http://127.0.0.1:5000` 에서 실행됩니다.

### 2. API 테스트

별도의 터미널을 열고 아래 `curl` 명령어를 실행하여 서버가 정상적으로 응답하는지 확인합니다.

```bash
curl http://localhost:5000/api/hello
```

**예상 응답**

```json
{
  "message": "Hello from your new Flask Backend!",
  "status": "success"
}
```

---

## ☁️ 배포 현황

현재 개발 버전이 아래 주소에 배포되어 있습니다.

| 환경 | 상태 | 기본 URL | 테스트 엔드포인트 |
| --- | --- | --- | --- |
| 개발(Dev) | **Online 🟢** | `http://54.180.83.235` | `http://54.180.83.235/api/hello` |

---

## ⚙️ CI/CD 파이프라인

이 프로젝트는 GitHub Actions를 통해 CI/CD가 자동화되어 있습니다.

- `main` 브랜치에 코드가 푸시(Push)되면, 워크플로우가 자동으로 실행됩니다.
- **CI:** Docker 이미지를 빌드하여 Docker Hub에 푸시합니다.
- **CD:** AWS EC2 서버에 SSH로 접속하여 최신 Docker 이미지를 받아 컨테이너를 재시작합니다.