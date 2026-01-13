import pandas as pd
import random
import sys
from collections import Counter

# 윈도우 콘솔 출력 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def load_and_analyze_data(file_path, history_count=20):
    """엑셀 파일에서 데이터를 읽어 각 번호의 가중치를 계산합니다."""
    print(f"📄 '{file_path}' 파일을 불러오는 중...")
    
    try:
        df = pd.read_excel(file_path)
        numbers_history = []
        
        print(f"📊 최근 {history_count}회차 데이터를 분석합니다.")
        
        count = 0
        for index, row in df.iterrows():
            if count >= history_count:
                break
            
            try:
                # 3번째 열(인덱스 2)부터 8번째 열(인덱스 7)까지 당첨번호
                nums = row.iloc[2:8].tolist()
                cleaned_nums = [int(n) for n in nums if isinstance(n, (int, float)) and not pd.isna(n)]
                
                if len(cleaned_nums) == 6:
                    numbers_history.extend(cleaned_nums)
                    count += 1
            except Exception:
                continue

        if not numbers_history:
            print("❌ 유효한 당첨 번호 데이터를 찾지 못했습니다.")
            return None

        # 빈도수 계산
        counter = Counter(numbers_history)
        
        # 가중치 딕셔너리 반환 (숫자: 가중치)
        # 전체 1~45 숫자에 대해 가중치 계산
        weights_dict = {n: counter.get(n, 0) + 1 for n in range(1, 46)}
        
        return weights_dict

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def get_user_numbers(title, max_count=6, prohibited_set=None):
    """사용자로부터 숫자를 입력받습니다."""
    if prohibited_set is None:
        prohibited_set = set()
        
    collected = set()
    print(f"\n👉 {title} (최대 {max_count}개, 입력 중단하려면 엔터)")
    
    while len(collected) < max_count:
        try:
            user_input = input(f"   숫자 입력 ({len(collected)+1}/{max_count}): ").strip()
            if not user_input:
                break
            
            num = int(user_input)
            
            if not (1 <= num <= 45):
                print("   ⚠️ 1부터 45 사이의 숫자를 입력해주세요.")
                continue
            
            if num in collected:
                print("   ⚠️ 이미 입력한 숫자입니다.")
                continue
                
            if num in prohibited_set:
                print("   ⚠️ 제외하거나 이미 선택된 숫자와 겹칩니다.")
                continue
                
            collected.add(num)
            
        except ValueError:
            print("   ⚠️ 올바른 숫자를 입력해주세요.")
            
    return collected

def generate_numbers(weights_dict, fixed_nums, excluded_nums):
    """설정된 가중치와 고정/제외 수를 반영하여 번호를 생성합니다."""
    
    # 1. 고정수를 미리 선택된 번호로 설정
    selected = set(fixed_nums)
    
    # 2. 후보군(population) 및 가중치(weights) 준비
    population = []
    weights = []
    
    for num in range(1, 46):
        # 이미 선택된 고정수이거나, 제외할 숫자는 후보에서 뺌
        if num in selected or num in excluded_nums:
            continue
        
        population.append(num)
        # 분석 데이터가 없으면 가중치 1, 있으면 해당 가중치 사용
        w = weights_dict.get(num, 1) if weights_dict else 1
        weights.append(w)
    
    # 3. 남은 자리만큼 뽑기
    while len(selected) < 6:
        if not population:
            break # 더 이상 뽑을 숫자가 없음 (이론상 드묾)
            
        # 가중치 랜덤 추출 (k=1)
        choice = random.choices(population, weights=weights, k=1)[0]
        
        # 중복 방지를 위해 선택된 숫자는 후보와 가중치에서 제거하고 다시 뽑거나
        # 간단히 다시 뽑는 방식(while 루프) 사용.
        # random.choices는 복원 추출이므로 뽑힌게 또 나올 수 있음.
        if choice not in selected:
            selected.add(choice)
            
    return sorted(list(selected))

if __name__ == "__main__":
    excel_file = '로또 회차별 당첨번호.xlsx'
    
    print("\n🔍 분석 옵션을 선택하세요:")
    print("1. 최근 30회차 분석")
    print("2. 전체 회차 분석")
    
    try:
        choice = input("선택 (1 또는 2): ").strip()
    except EOFError:
        choice = '1'
    
    if choice == '2':
        history_limit = 10000
        mode_str = "전체 회차"
    else:
        history_limit = 30
        mode_str = "최근 30회차"
        
    print(f"\n✅ '{mode_str}' 기준으로 데이터를 분석합니다.")
    
    # 1. 데이터 분석
    weights_dict = load_and_analyze_data(excel_file, history_limit)
    
    # 2. 사용자 입력 (포함/제외 숫자)
    fixed_nums = get_user_numbers("포함하고 싶은 숫자", 6)
    print(f"   -> 선택된 고정수: {sorted(list(fixed_nums))}")
    
    excluded_nums = get_user_numbers("제외하고 싶은 숫자", 6, prohibited_set=fixed_nums)
    print(f"   -> 선택된 제외수: {sorted(list(excluded_nums))}")
    
    # 3. 번호 생성 (5세트)
    print("\n" + "="*40)
    print(f"🔮 {mode_str} 분석 + 사용자 설정 반영 추천 번호")
    print("="*40)
    
    for i in range(5):
        lotto_nums = generate_numbers(weights_dict, fixed_nums, excluded_nums)
        print(f"   {i+1}세트: {lotto_nums}")
        
    print("="*40)