import sys
import json
import urllib.request

def get_exchange_rate(target_currency='KRW'):
    # 무료 환율 API (USD 기준)
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            rates = data.get('rates', {})
            
            rate = rates.get(target_currency.upper())
            
            if rate:
                print(f"현재 환율: 1 USD = {rate} {target_currency.upper()}")
            else:
                print(f"오류: '{target_currency}' 통화 코드를 찾을 수 없습니다.")
                
    except Exception as e:
        print(f"환율 정보를 가져오는 중 오류 발생: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else 'KRW'
    get_exchange_rate(target)
