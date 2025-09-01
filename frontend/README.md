# 🌐 AI 기반 하이브리드 방화벽 관리 시스템 - 프론트엔드

**사용자가 YAML 정책을 작성하고 결과를 확인할 수 있는 웹 대시보드입니다. React.js + Vite 번들러로 개발되었으며, Vercel을 통해 손쉽게 배포됩니다.**

---

## 📜 프로젝트 개요

이 프론트엔드는 백엔드 API와 연동하여 **방화벽 정책 관리 및 로그 분석 결과를 시각화**하는 역할을 담당합니다.
사용자는 웹 UI를 통해 정책을 작성·수정·삭제하고, 정책 적용 상태와 로그 분석 리포트를 직관적으로 확인할 수 있습니다.

---

## 🏗️ 시스템 아키텍처 및 흐름

```
1. 사용자 (웹 브라우저)
     |
     v
2. React.js SPA (Vite 번들링)
     |
     v
3. API 호출 (Flask 백엔드)
     |
     v
4. 백엔드 → Terraform / Ansible 실행 → 방화벽 정책 적용
     |
     v
5. 결과 로그/리포트 → 프론트 대시보드에 시각화
```

---

## 🛠️ 기술 스택

* **언어:** JavaScript (ES6+)
* **프레임워크:** React.js
* **번들러:** Vite
* **라우팅:** React Router DOM
* **HTTP 클라이언트:** Axios
* **스타일링:** CSS (Tailwind/Styled-components 확장 가능)
* **배포:** Vercel

---

## 🚀 시작하기 (로컬 환경 설정)

프론트엔드를 로컬에서 실행하고 테스트하기 위한 가이드입니다.

### 1. 소스 코드 복제 (Clone)

```bash
git clone https://github.com/SECUI-FortiZero/Dashboard.git
cd frontend
```

### 2. 의존성 설치

```bash
npm install
```

### 3. 환경 변수 설정

프로젝트 루트에 `.env.local` 파일을 생성하고 아래 예시를 참고해 값을 채워주세요.

`.env.example`

```
# API 서버 주소 (개발 환경)
VITE_API_BASE_URL=http://localhost:5000
```

> Vercel 배포 시에는 Vercel Dashboard에서 환경 변수를 등록합니다.

---

## 🧪 로컬에서 테스트하기

### 1. 개발 서버 실행

```bash
npm run dev
```

* 개발 서버가 `http://localhost:5173` 에서 실행됩니다.
* API 요청은 `VITE_API_BASE_URL` 환경변수를 기준으로 백엔드와 통신합니다.

### 2. 빌드 & 미리보기

```bash
npm run build
npm run preview
```

* `dist/` 디렉토리에 정적 빌드 파일이 생성됩니다.
* `npm run preview`로 로컬에서 배포 미리보기 가능.

---

## ☁️ 배포 현황

프론트엔드는 **Vercel**을 통해 자동 배포됩니다.
GitHub 저장소에 Push 시 Vercel이 빌드를 트리거하고, 결과물이 배포됩니다.

| 환경      | 상태            | 기본 URL                                 | 테스트 경로     |
| ------- | ------------- | -------------------------------------- | ---------- |
| 개발(Dev) | **Online 🟢** | `https://your-project-name.vercel.app` | `/` (홈 화면) |

---

## ⚙️ CI/CD 파이프라인

* `main` 브랜치 푸시 → Vercel이 자동으로 빌드 및 배포
* **CI:** Vite 빌드 테스트
* **CD:** 성공 시 Vercel 배포 URL 업데이트
* 커스텀 도메인 연결 예정 (예: `https://dashboard.fortizero.com`)

