import pandas as pd
import os
from backend.database import SessionLocal, engine, Base
from backend.models import LottoRound
from backend.utils import get_excel_path, find_round_column

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

def migrate():
    excel_path = get_excel_path()
    if not os.path.exists(excel_path):
        print(f"❌ 엑셀 파일이 없습니다: {excel_path}")
        return

    print(f"📂 엑셀 데이터 로딩 중... ({excel_path})")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"❌ 엑셀 읽기 실패: {e}")
        return

    # 회차 컬럼 찾기
    round_col = find_round_column(df)
    if not round_col:
        # 컬럼 못 찾으면 대략 2번째 컬럼 가정
        if len(df.columns) > 1:
            round_col = df.columns[1]
        else:
            print("❌ 회차 컬럼을 찾을 수 없습니다.")
            return

    db = SessionLocal()
    count = 0
    
    # 엑셀은 보통 최신 회차가 위에 있으므로 역순으로 넣거나 그냥 넣어도 됨
    # DB는 순서 상관없음 (쿼리할 때 정렬)
    
    print("🚀 데이터 이관 시작...")
    
    try:
        # 기존 데이터 확인 (중복 방지)
        existing_rounds = {r[0] for r in db.query(LottoRound.round_no).all()}
        
        for _, row in df.iterrows():
            try:
                # 데이터 파싱
                r_val = row[round_col]
                if pd.isna(r_val): continue
                
                round_no = int(r_val)
                if round_no in existing_rounds:
                    continue # 이미 있으면 패스

                # 당첨번호 파싱 (보통 회차 컬럼 다음부터 6개)
                # find_round_column이 B열(index 1)이라면 C~H(index 2~7)가 번호
                col_idx = df.columns.get_loc(round_col)
                nums = row.iloc[col_idx+1 : col_idx+7].tolist()
                bonus = row.iloc[col_idx+7]
                
                # 정수 변환
                clean_nums = [int(n) for n in nums if pd.notna(n)]
                if len(clean_nums) != 6: continue
                
                clean_bonus = int(bonus) if pd.notna(bonus) else 0

                # DB 객체 생성
                db_item = LottoRound(
                    round_no=round_no,
                    drwt_no1=clean_nums[0],
                    drwt_no2=clean_nums[1],
                    drwt_no3=clean_nums[2],
                    drwt_no4=clean_nums[3],
                    drwt_no5=clean_nums[4],
                    drwt_no6=clean_nums[5],
                    bnus_no=clean_bonus
                )
                db.add(db_item)
                count += 1
                
            except Exception as e:
                # print(f"Row skip: {e}")
                continue
        
        db.commit()
        print(f"✅ 마이그레이션 완료! 총 {count}개 회차가 DB에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ DB 저장 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
