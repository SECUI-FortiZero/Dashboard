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
2. Flask 백엔드 API (로컬 PC에서 실행)
      |
      +--> 3a. Terraform/Ansible 코드 생성 및 실행
      |
      +--> 3b. AWS API 또는 On-premise 서버와 통신
```

---

## 🛠️ 기술 스택

- **언어:** Python 3.9+
- **프레임워크:** Flask
- **IaC & 자동화:** Terraform, Ansible
- **클라우드:** AWS

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
python -m venv .venv

# 가상환경 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 가상환경 활성화 (macOS/Linux)
source .venv/bin/activate
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
- 서버가 `0.0.0.0` 에서 실행되며, 같은 네트워크에 연결된 다른 장치에서도 접속할 수 있습니다.

- 터미널에 표시되는 Running on `http://192.168.x.x:5001` 과 같은 IP 주소를 확인하세요.

### 2. API 테스트

별도의 터미널을 열고 아래 `curl` 명령어를 실행하여 서버가 정상적으로 응답하는지 확인합니다.

```bash
# 서버를 실행한 PC에서 테스트하는 경우
curl http://localhost:5001/api/hello

# 다른 PC에서 테스트하는 경우 (서버 PC의 IP 주소로 변경)
curl http://192.168.x.x:5001/api/hello
```

**예상 응답**

```json
{
  "message": "Hello from your new Flask Backend!",
  "status": "success"
}
```
