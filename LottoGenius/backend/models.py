from sqlalchemy import Column, Integer, Date
from .database import Base

class LottoRound(Base):
    __tablename__ = "lotto_rounds"

    round_no = Column(Integer, primary_key=True, index=True) # 회차
    drwt_no1 = Column(Integer)
    drwt_no2 = Column(Integer)
    drwt_no3 = Column(Integer)
    drwt_no4 = Column(Integer)
    drwt_no5 = Column(Integer)
    drwt_no6 = Column(Integer)
    bnus_no = Column(Integer)
