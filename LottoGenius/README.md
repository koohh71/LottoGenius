# 🔮 Lotto Genius (로또 지니어스)

**Lotto Genius**는 과거 당첨 데이터를 과학적으로 분석하여 최적의 로또 번호를 추천해주는 지능형 웹 애플리케이션입니다. 단순한 랜덤 생성이 아닌, 역대 패턴을 분석한 가중치 알고리즘과 현실적인 필터링 시스템을 통해 당첨 확률을 높이는 것을 목표로 합니다.

![Lotto Genius Screenshot](https://github.com/koohh71/LottoGenius/assets/placeholder.png)

## ✨ Key Features

*   **📊 정밀 통계 분석:**
    *   **HOT (최다 당첨):** 최근 가장 많이 나온 번호 Top 10 시각화.
    *   **COLD (최소 당첨):** 오랫동안 나오지 않은 번호 Top 10 시각화.
    *   **구간 분포:** 번호 대역별(10번대, 20번대 등) 출현 비율 분석.
*   **🧠 스마트 AI 필터링:**
    *   비현실적인 패턴(3연속 번호, 특정 구간 쏠림, 홀짝 불균형 등)을 자동으로 제거.
*   **⚖️ 하이브리드 생성 모드:**
    *   사용자가 원하는 **고정수(반자동)**를 지정하면, 나머지를 AI가 최적의 조합으로 채워줍니다.
*   **📸 이미지 저장:**
    *   생성된 5게임 조합을 깔끔한 이미지 카드(.png)로 즉시 다운로드하여 소장 가능.
*   **🚀 고성능 아키텍처:**
    *   인메모리 캐싱(Caching)을 통한 0.1초 미만의 빠른 응답 속도.
    *   SQLite/PostgreSQL 하이브리드 DB 지원.

## 🛠 Tech Stack

### Frontend
*   **React 18** (Vite)
*   **Tailwind CSS** (Styling)
*   **Recharts** (Data Visualization)
*   **Axios** (API Client)
*   **html2canvas** (Image Export)

### Backend
*   **Python 3.13**
*   **FastAPI** (High-performance Web Framework)
*   **SQLAlchemy** (ORM)
*   **Pydantic** (Data Validation)
*   **Pandas & OpenPyXL** (Data Processing)

### Infrastructure
*   **Render** (Backend Hosting)
*   **Netlify** (Frontend Hosting)
*   **PostgreSQL** (Production DB)

## 🚀 Getting Started (Local Development)

### Prerequisites
*   Python 3.8+
*   Node.js 18+

### 1. Backend Setup
```bash
cd LottoGenius
# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run server
python -m uvicorn backend.main:app --reload --host 0.0.0.0
```
Server will start at `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd LottoGenius/frontend

# Install dependencies
npm install

# Run development server
npm run dev -- --host
```
App will start at `http://localhost:5173`.

## 📂 Project Structure

```
LottoGenius/
├── backend/                # FastAPI Application
│   ├── api/v1/routers/     # API Endpoints
│   ├── core/               # Configuration & Constants
│   ├── crud/               # Database Access Layer
│   ├── models/             # SQLAlchemy Models
│   ├── schemas/            # Pydantic Schemas
│   ├── services/           # Business Logic (AI & Filter)
│   └── main.py             # Entry Point
├── frontend/               # React Application
│   ├── src/
│   │   ├── components/     # UI Components (Modularized)
│   │   ├── services/       # API Integration
│   │   └── App.jsx         # Main Layout
├── data/                   # SQLite Database (Local)
└── docs/                   # Technical Specifications
```

## 📝 License
This project is open-sourced under the MIT License.

---
Created with ❤️ by **Lotto Genius Team**.