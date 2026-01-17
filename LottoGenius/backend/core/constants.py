# 로또 번호 생성 필터링 상수

# 총합 범위 (통계적으로 가장 빈도가 높은 100~175 구간으로 축소)
SUM_MIN = 100
SUM_MAX = 175

# 홀짝 비율 (0:6 또는 6:0 제외)
ODD_EVEN_RATIO_EXCLUDE = [0, 6]

# 연속 번호 제한 (3개 이상 연속 금지)
MAX_CONSECUTIVE_COUNT = 2

# 번호대별 최대 개수 (3개 초과 금지 - 더 엄격하게)
MAX_PER_DECADE = 3

# 번호 생성 최대 시도 횟수
MAX_RETRIES = 500

# 분석 기본값
DEFAULT_HISTORY_LIMIT = 30
MAX_HISTORY_LIMIT = 10000
