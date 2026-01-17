# 로또 번호 생성 필터링 상수

# 총합 범위 (일반적으로 60~240 사이가 당첨 확률 높음)
SUM_MIN = 60
SUM_MAX = 240

# 홀짝 비율 (0:6 또는 6:0 제외)
ODD_EVEN_RATIO_EXCLUDE = [0, 6]

# 연속 번호 제한 (3개 이상 연속 금지 -> 연속 카운트 2 이상이면 탈락)
MAX_CONSECUTIVE_COUNT = 2

# 번호대별 최대 개수 (특정 구간 쏠림 방지, 4개 초과 금지)
MAX_PER_DECADE = 4

# 번호 생성 최대 시도 횟수
MAX_RETRIES = 100

# 분석 기본값
DEFAULT_HISTORY_LIMIT = 30
MAX_HISTORY_LIMIT = 10000
