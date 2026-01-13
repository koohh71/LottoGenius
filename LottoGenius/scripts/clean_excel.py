import pandas as pd
import os

file_path = '로또 회차별 당첨번호.xlsx'

print(f"📂 '{file_path}' 파일 검사 중...")

# 엑셀 읽기
try:
    df = pd.read_excel(file_path)
    
    # B열(인덱스 1)이 '회차'라고 가정
    # 컬럼명이 정확하지 않을 수 있으므로 iloc 사용
    round_col_idx = 1
    
    # 1206 값을 가진 행 찾기
    # 숫자로 변환 가능한지 확인 (문자열 '1206'일 수도 있음)
    mask = pd.to_numeric(df.iloc[:, round_col_idx], errors='coerce') == 1206
    
    count = mask.sum()
    
    if count > 0:
        print(f"⚠️ 1206회차 데이터를 {count}개 발견했습니다. 삭제합니다.")
        
        # 1206이 아닌 행만 남기기
        df_cleaned = df[~mask]
        
        # 저장 (인덱스 제외)
        df_cleaned.to_excel(file_path, index=False)
        print("✅ 삭제 완료! 파일을 덮어썼습니다.")
        
        # 확인 사살
        max_round = pd.to_numeric(df_cleaned.iloc[:, 1], errors='coerce').max()
        print(f"📉 이제 파일 내 최대 회차는 '{int(max_round)}'회 입니다.")
        
    else:
        print("❓ 1206회차 데이터를 찾을 수 없습니다. (이미 지워진 듯 합니다)")
        # 혹시 모르니 최대값 출력
        max_round = pd.to_numeric(df.iloc[:, 1], errors='coerce').max()
        print(f"ℹ️ 현재 최대 회차: {max_round}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
