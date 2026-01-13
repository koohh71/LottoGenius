from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import LottoRound
from typing import List, Dict, Optional
from collections import Counter

def get_max_round(db: Session) -> int:
    """DB에서 가장 높은 회차 번호를 반환합니다."""
    latest = db.query(LottoRound).order_by(LottoRound.round_no.desc()).first()
    return latest.round_no if latest else 0

def get_recent_rounds(db: Session, limit: int) -> List[LottoRound]:
    """최근 N회차 데이터를 가져옵니다."""
    return db.query(LottoRound).order_by(LottoRound.round_no.desc()).limit(limit).all()

def create_lotto_round(db: Session, round_no: int, numbers: List[int], bonus: int):
    """새로운 회차 정보를 저장합니다."""
    # 중복 체크
    existing = db.query(LottoRound).filter(LottoRound.round_no == round_no).first()
    if existing:
        return existing
        
    db_item = LottoRound(
        round_no=round_no,
        drwt_no1=numbers[0],
        drwt_no2=numbers[1],
        drwt_no3=numbers[2],
        drwt_no4=numbers[3],
        drwt_no5=numbers[4],
        drwt_no6=numbers[5],
        bnus_no=bonus
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
