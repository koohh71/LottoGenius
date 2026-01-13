from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....database import get_db
from ....schemas import lotto as schemas
from ....services import lotto_service
from ....crud import lotto_crud

router = APIRouter()

@router.get("/latest-round", response_model=schemas.LatestRoundResponse)
def get_latest_round(db: Session = Depends(get_db)):
    """최신 회차 번호를 반환합니다."""
    return {"latest_round": lotto_crud.get_max_round(db)}

@router.post("/generate", response_model=dict)
def generate_numbers(req: schemas.GenerateRequest, db: Session = Depends(get_db)):
    """번호를 생성합니다."""
    results = lotto_service.generate_lotto_numbers(db, req)
    return {"recommendations": results}

@router.get("/stats", response_model=schemas.StatsResponse)
def get_stats(limit: int = 30, db: Session = Depends(get_db)):
    """통계 데이터를 반환합니다."""
    return lotto_service.get_lotto_stats(db, limit)

@router.post("/add-round", response_model=dict)
def add_round(req: schemas.AddRoundRequest = None, db: Session = Depends(get_db)):
    """회차를 추가합니다 (수동/자동)."""
    target_round = 0
    nums = []
    bonus = 0

    # 1. 수동 입력
    if req and req.round_no:
        target_round = req.round_no
        nums = req.numbers
        bonus = req.bonus
    # 2. 자동 업데이트 (삭제되었으나 API는 유지 - 필요시 부활 가능)
    else:
        current_max = lotto_crud.get_max_round(db)
        target_round = current_max + 1
        data = lotto_service.fetch_external_lotto_data(target_round)
        
        if not data:
            return {"status": "error", "message": "자동 업데이트 실패"}
        nums = data['nums']
        bonus = data['bonus']

    # 저장
    try:
        lotto_crud.create_lotto_round(db, target_round, nums, bonus)
        return {"status": "success", "message": f"{target_round}회차 저장 완료!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
