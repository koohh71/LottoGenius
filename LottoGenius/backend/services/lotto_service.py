import random
import requests
import urllib3
from typing import List, Dict, Set
from collections import Counter
from sqlalchemy.orm import Session

from ..crud import lotto_crud
from ..schemas.lotto import GenerateRequest

# SSL 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def calculate_weights(db: Session, limit: int) -> Dict[int, int]:
    """최근 데이터를 기반으로 가중치를 계산합니다."""
    rounds = lotto_crud.get_recent_rounds(db, limit)
    if not rounds:
        return {n: 1 for n in range(1, 46)}
        
    numbers_history = []
    for r in rounds:
        numbers_history.extend([
            r.drwt_no1, r.drwt_no2, r.drwt_no3, 
            r.drwt_no4, r.drwt_no5, r.drwt_no6
        ])
    
    counter = Counter(numbers_history)
    return {n: counter.get(n, 0) + 1 for n in range(1, 46)}

def generate_lotto_numbers(db: Session, req: GenerateRequest) -> List[List[int]]:
    """조건에 맞는 로또 번호를 생성합니다."""
    limit = 10000 if req.history_limit > 1000 else req.history_limit
    weights_dict = calculate_weights(db, limit)
    
    results = []
    for _ in range(req.count):
        selected = set(req.fixed_nums)
        population = []
        weights = []
        
        for num in range(1, 46):
            if num in selected or num in req.excluded_nums:
                continue
            population.append(num)
            weights.append(weights_dict.get(num, 1))
            
        while len(selected) < 6:
            if not population: break
            choice = random.choices(population, weights=weights, k=1)[0]
            if choice not in selected:
                selected.add(choice)
        
        results.append(sorted(list(selected)))
    return results

def get_lotto_stats(db: Session, limit: int) -> Dict:
    """통계 데이터를 생성합니다."""
    rounds = lotto_crud.get_recent_rounds(db, limit)
    if not rounds:
        return {}
        
    numbers_history = []
    for r in rounds:
        numbers_history.extend([
            r.drwt_no1, r.drwt_no2, r.drwt_no3, 
            r.drwt_no4, r.drwt_no5, r.drwt_no6
        ])
    
    # 1~45번 모든 번호의 빈도 계산 (0회 출현 포함)
    counter = {n: 0 for n in range(1, 46)}
    for n in numbers_history:
        counter[n] += 1
        
    # 정렬 (오름차순: 적게 나온 순)
    sorted_counts = sorted(counter.items(), key=lambda x: x[1])
    
    # 최소 당첨 (적게 나온 순서 10개)
    min_freq_data = [{"num": k, "count": v} for k, v in sorted_counts[:10]]
    
    # 최다 당첨 (많이 나온 순서 10개 - 뒤에서부터 자르고 뒤집기)
    max_freq_data = [{"num": k, "count": v} for k, v in sorted_counts[-10:]]
    max_freq_data.reverse()
    
    ranges = {"1-10": 0, "11-20": 0, "21-30": 0, "31-40": 0, "41-45": 0}
    for n in numbers_history:
        if 1 <= n <= 10: ranges["1-10"] += 1
        elif 11 <= n <= 20: ranges["11-20"] += 1
        elif 21 <= n <= 30: ranges["21-30"] += 1
        elif 31 <= n <= 40: ranges["31-40"] += 1
        elif 41 <= n <= 45: ranges["41-45"] += 1
    
    range_data = [{"name": k, "value": v} for k, v in ranges.items()]
    
    return {
        "frequency": max_freq_data,
        "min_frequency": min_freq_data,
        "ranges": range_data
    }

def fetch_external_lotto_data(round_no: int):
    """외부 API에서 로또 데이터를 가져옵니다."""
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={round_no}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Referer': 'https://www.dhlottery.co.kr/'
    }
    
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=5)
        data = res.json()
        if data.get("returnValue") == "success":
            return {
                "nums": [data.get(f"drwtNo{i}") for i in range(1, 7)],
                "bonus": data.get("bnusNo")
            }
        return None
    except Exception:
        return None
