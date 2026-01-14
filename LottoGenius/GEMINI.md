# Project Context: Lotto Genius (v2.0)

## Overview
**Lotto Genius**는 로또 당첨 번호를 과학적으로 분석(가중치 적용)하여 번호를 추천해주는 웹 애플리케이션입니다.
초기 엑셀 기반의 스크립트에서 시작하여, 현재는 DB 기반의 **Full-Stack Web Application**으로 고도화되었으며 클라우드에 배포되어 있습니다.

## Tech Stack
- **Frontend:** React (Vite), Tailwind CSS, Recharts, Axios
- **Backend:** FastAPI (Python), SQLAlchemy, Pydantic
- **Database:** 
  - Local: SQLite (`data/lotto.db`)
  - Production: PostgreSQL (Render Managed DB)
- **Deployment:**
  - Frontend: **Netlify** (Env: `VITE_API_URL`)
  - Backend: **Render** (Env: `DATABASE_URL`, Python 3.13)

## Architecture
- **Layered Architecture:** `routers` -> `services` -> `crud` -> `models`
- **Hybrid Data Update:**
  - 앱 시작 시 데이터가 없으면 엑셀(`로또 회차별 당첨번호.xlsx`)에서 자동 마이그레이션.
  - 이후 사용자가 관리자 화면에서 수동으로 최신 회차 추가 가능.

## Deployment Status (2026-01-14)
- **Frontend URL:** (Netlify) `https://dulcet-chaja-ebf450.netlify.app`
- **Backend URL:** (Render) `https://lotto-backend-3208.onrender.com`
- **Repository:** GitHub `koohh71/LottoGenius`

## Development Commands (Local)

### 1. Backend
```bash
cd LottoGenius
# 가상환경 활성화 권장
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 0.0.0.0
```
*Access: http://localhost:8000/docs*

### 2. Frontend
```bash
cd LottoGenius/frontend
npm install
npm run dev -- --host
```
*Access: http://localhost:5173*

## Directory Structure
- `backend/`: FastAPI source (api, core, crud, models, schemas, services)
- `frontend/`: React source
- `data/`: SQLite DB file location
- `docs/`: Technical specifications (`기술사양서_v2.doc`)
- `scripts/`: Utility scripts (migration, etc.)

## Todo / Future Improvements
- [x] Excel -> DB Migration (SQLite/Postgres)
- [x] Backend Refactoring (Layered Arch)
- [x] Feature: Stats Charts (Recharts)
- [x] Feature: Hybrid Generation (Manual + Auto)
- [x] Deployment (Render + Netlify)
- [ ] User Authentication (Login/Sign-up)
- [ ] Notification System (Email/SMS for results)
