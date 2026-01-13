from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.routers import lotto
from .database import engine, Base, SessionLocal
from .services import migration_service

# DB 테이블 생성 (앱 시작 시 자동 생성)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lotto Genius API", version="1.0.0")

@app.on_event("startup")
def startup_event():
    try:
        db = SessionLocal()
        try:
            migration_service.migrate_if_empty(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Startup migration failed: {e}")
        # 서버 시작은 계속 진행

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(lotto.router, prefix="/api", tags=["Lotto"])

@app.get("/")
def read_root():
    return {"message": "Lotto Genius API Running 🚀"}