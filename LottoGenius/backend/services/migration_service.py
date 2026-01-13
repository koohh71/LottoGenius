import pandas as pd
import os
from sqlalchemy.orm import Session
from ..crud import lotto_crud
from ..database import SessionLocal

# 프로젝트 루트 (LottoGenius) 찾기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCEL_FILE = os.path.join(BASE_DIR, '로또 회차별 당첨번호.xlsx')

def find_round_column(df: pd.DataFrame):
    for col in df.columns:
        if "회차" in str(col): return col
    if len(df.columns) > 1: return df.columns[1]
    return None

def migrate_if_empty(db: Session):
    # DB에 데이터가 있는지 확인
    if lotto_crud.get_max_round(db) > 0:
        print("✅ DB has data. Skipping migration.")
        return

    if not os.path.exists(EXCEL_FILE):
        print(f"⚠️ Excel file not found at {EXCEL_FILE}. Skipping migration.")
        return

    print("🚀 Initializing DB from Excel...")
    try:
        df = pd.read_excel(EXCEL_FILE)
        round_col = find_round_column(df)
        if not round_col: return

        count = 0
        existing_rounds = set() # DB is empty anyway

        for _, row in df.iterrows():
            try:
                r_val = row[round_col]
                if pd.isna(r_val): continue
                round_no = int(r_val)

                # Find numbers (next 6 cols)
                col_idx = df.columns.get_loc(round_col)
                nums = row.iloc[col_idx+1 : col_idx+7].tolist()
                bonus = row.iloc[col_idx+7]
                
                clean_nums = [int(n) for n in nums if pd.notna(n)]
                if len(clean_nums) != 6: continue
                clean_bonus = int(bonus) if pd.notna(bonus) else 0

                lotto_crud.create_lotto_round(db, round_no, clean_nums, clean_bonus)
                count += 1
            except: continue
        
        print(f"✅ Migration complete! {count} rounds imported.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
