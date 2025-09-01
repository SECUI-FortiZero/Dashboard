

# 🔒 AI 기반 하이브리드 방화벽 관리 시스템

**온프레미스와 클라우드 방화벽을 하나의 정책(YAML)으로 통합 관리하고, AI를 통해 로그와 정책을 분석·리포트화하는 대시보드 시스템입니다.**
본 저장소는 \*\*백엔드(Flask)\*\*와 **프론트엔드(React + Vite)**, 그리고 **CI/CD 자동화** 구성을 포함합니다.

---

## 📜 프로젝트 개요

* **문제 인식**: 온프레미스 서버와 클라우드 방화벽 관리의 파편화, 운영자의 피로도 증가
* **해결 방법**: 사람이 읽기 쉬운 YAML 정책을 정의 → 자동으로 iptables + AWS SG에 반영
* **부가 기능**: 로그/정책 변경 이력을 AI로 요약하여 운영 효율 극대화
* **접근성**: 웹 대시보드에서 직관적으로 정책 작성·배포·로그 모니터링 가능

---

## 🏗️ 시스템 아키텍처

```
사용자 (웹 대시보드)
        │
        ▼
프론트엔드 (React + Vite, Vercel)
        │
        ▼
백엔드 (Flask API, AWS EC2, Docker)
        │
 ┌──────┴────────┐
 ▼               ▼
Terraform → AWS SG 적용   Ansible → On-premise iptables 적용
        │
        ▼
로그/정책 이력 → AI 분석 → 대시보드 시각화
```

---

## 🛠️ 기술 스택

* **Frontend**: React.js, Vite, React Router, Axios, Vercel
* **Backend**: Python 3.9+, Flask, Flask-CORS
* **IaC & 자동화**: Terraform, Ansible
* **CI/CD**: GitHub Actions
* **Infra**: AWS EC2, Docker
* **AI**: OpenAI API (정책/로그 요약)

---

## 🚀 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/SECUI-FortiZero/Dashboard.git
```

### 2. 백엔드 실행

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python run.py
# → http://localhost:5000/api/hello
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## ☁️ 배포 현황

| 영역       | 환경  | 배포 URL                                                               |
| -------- | --- | -------------------------------------------------------------------- |
| Frontend | Dev | [https://your-frontend.vercel.app](https://your-frontend.vercel.app) |
| Backend  | Dev | http\://\<EC2\_PUBLIC\_IP>:5000                                      |

---

## ⚙️ CI/CD

* **Frontend**: GitHub → Vercel 자동 빌드 & 배포
* **Backend**: GitHub Actions → Docker 이미지 빌드 & AWS EC2 배포

---

## 🌿 브랜치 전략

### 브랜치 구조

```
main (운영 배포)
 └─ develop (통합 개발 브랜치)
     ├─ backend/   (백엔드 기능 개발)
     ├─ frontend/  (프론트엔드 기능 개발)
     └─ feature/#이슈번호 (세부 작업 브랜치)
```

### 규칙

* **main**: 운영 배포용, 직접 push 금지
* **develop**: 기능 통합, PR을 통해 병합
* **backend/**, **frontend/**: 도메인별 개발 브랜치
* **feature/#이슈번호**: 실제 작업 브랜치 (예: `feature/#12`)

---

## 📝 작업 방식

1. 새로운 기능/버그 → GitHub Issue 생성
2. Issue 번호 기반 브랜치 생성:

   ```bash
   git checkout -b feature/#12-login-api develop
   ```
3. 작업 후 PR 생성 → 리뷰 & 승인 → develop 병합
4. 기능 안정화 후 develop → main 병합 → 배포

---

## ✅ 규칙 요약

* **이슈 단위로 작업 시작**
* **브랜치 이름은 feature/#이슈번호-설명**
* **PR 시 관련 이슈 번호 반드시 연결**
* **main 브랜치 직접 수정 금지**


