import random
import requests
import urllib3
from typing import List, Dict, Set
from collections import Counter
from sqlalchemy.orm import Session

from ..crud import lotto_crud
from ..schemas.lotto import GenerateRequest
from ..core import constants

# SSL 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 인메모리 캐시 (속도 최적화) ---
_CACHE = {
    "last_round": 0,
    "weights": {},  # key: limit
    "stats": {}     # key: limit
}

def _check_cache_validity(db: Session):
    """DB의 최신 회차와 캐시된 회차가 다르면 캐시를 초기화합니다."""
    current_max = lotto_crud.get_max_round(db)
    if _CACHE["last_round"] != current_max:
        _CACHE["last_round"] = current_max
        _CACHE["weights"] = {}
        _CACHE["stats"] = {}
    return current_max

def calculate_weights(db: Session, limit: int) -> Dict[int, int]:
    """최근 데이터를 기반으로 가중치를 계산합니다 (캐싱 적용)."""
    _check_cache_validity(db)
    
    # 캐시 적중 시 바로 반환
    if limit in _CACHE["weights"]:
        return _CACHE["weights"][limit]

    # 캐시 없으면 계산
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
    weights = {n: counter.get(n, 0) + 1 for n in range(1, 46)}
    
    # 결과 캐싱
    _CACHE["weights"][limit] = weights
    return weights

def is_valid_combination(nums: List[int]) -> bool:
    """생성된 번호 조합이 현실적인 패턴인지 검증합니다."""
    # 1. 총합 검사
    total = sum(nums)
    if not (constants.SUM_MIN <= total <= constants.SUM_MAX):
        return False

    # 2. 홀짝 비율 검사
    odds = sum(1 for n in nums if n % 2 != 0)
    if odds in constants.ODD_EVEN_RATIO_EXCLUDE:
        return False

    # 3. 연속 번호 검사
    consecutive_cnt = 0 # 3연속 방지용
    pair_cnt = 0        # 2연속 쌍 개수 (1,2 & 10,11 방지)
    
    for i in range(len(nums) - 1):
        if nums[i+1] == nums[i] + 1:
            consecutive_cnt += 1
            if consecutive_cnt == 1: # 새로운 쌍 발견
                pair_cnt += 1
            if consecutive_cnt >= constants.MAX_CONSECUTIVE_COUNT: # 3연속 이상 즉시 탈락
                return False
        else:
            consecutive_cnt = 0
            
    # 연속된 쌍이 2개 이상이면 탈락 (너무 작위적임)
    if pair_cnt > 1:
        return False

    # 4. 구간 쏠림 검사
    ranges = [0] * 5
    for n in nums:
        idx = (n - 1) // 10
        if idx > 4: idx = 4
        ranges[idx] += 1
    if any(r > constants.MAX_PER_DECADE for r in ranges):
        return False

    return True

def generate_lotto_numbers(db: Session, req: GenerateRequest) -> List[List[int]]:
    """조건에 맞는 로또 번호를 생성합니다 (패턴 필터링 적용)."""
    limit = constants.MAX_HISTORY_LIMIT if req.history_limit > 1000 else req.history_limit
    weights_dict = calculate_weights(db, limit)
    
    results = []
    
    # 요청한 게임 수만큼 반복
    for _ in range(req.count):
        best_candidate = []
        
        # 유효한 조합을 찾을 때까지 시도
        for _ in range(constants.MAX_RETRIES):
            selected = set(req.fixed_nums)
            population = []
            weights = []
            
            for num in range(1, 46):
                if num in selected or num in req.excluded_nums:
                    continue
                population.append(num)
                weights.append(weights_dict.get(num, 1))
                
            # 번호 채우기
            temp_population = population[:]
            temp_weights = weights[:]
            
            while len(selected) < 6:
                if not temp_population: break
                choice = random.choices(temp_population, weights=temp_weights, k=1)[0]
                if choice not in selected:
                    selected.add(choice)
            
            candidate = sorted(list(selected))
            
            # 패턴 검사 통과하면 채택
            if len(candidate) == 6 and is_valid_combination(candidate):
                best_candidate = candidate
                break
            
            # 실패했어도 일단 후보로 저장
            if len(candidate) == 6:
                best_candidate = candidate
        
        results.append(best_candidate)

    return results

def get_lotto_stats(db: Session, limit: int) -> Dict:
    """통계 데이터를 생성합니다 (캐싱 적용)."""
    _check_cache_validity(db)

    # 캐시 적중 시 바로 반환
    if limit in _CACHE["stats"]:
        return _CACHE["stats"][limit]

    rounds = lotto_crud.get_recent_rounds(db, limit)
    if not rounds:
        return {}
        
    numbers_history = []
    for r in rounds:
        numbers_history.extend([
            r.drwt_no1, r.drwt_no2, r.drwt_no3, 
            r.drwt_no4, r.drwt_no5, r.drwt_no6
        ])
    
    # 1~45번 모든 번호의 빈도 계산
    counter = {n: 0 for n in range(1, 46)}
    for n in numbers_history:
        counter[n] += 1
        
    sorted_counts = sorted(counter.items(), key=lambda x: x[1])
    
    min_freq_data = [{"num": k, "count": v} for k, v in sorted_counts[:10]]
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
    
    result = {
        "frequency": max_freq_data,
        "min_frequency": min_freq_data,
        "ranges": range_data
    }
    
    # 결과 캐싱
    _CACHE["stats"][limit] = result
    return result

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
