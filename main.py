import requests
from datetime import datetime

# 설정 정보
SERVICE_KEY = "3a47354f399bc29422ac0b77206835227bb518a61dc62911b1d8f137877dbaf9"
TELEGRAM_TOKEN = "8555362302:AAE2Y_BUSsA-sbfhwuOB6qR5AtP-3bdTvmU"
CHAT_ID = "529007689"

def get_korea_weather():
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H00")
    
    params = {
        'serviceKey': requests.utils.unquote(SERVICE_KEY),
        'pageNo': '1', 'numOfRows': '1000', 'dataType': 'JSON',
        'base_date': base_date, 'base_time': base_time,
        'nx': '60', 'ny': '127'
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        items = data['response']['body']['items']['item']
        
        t1h = next(i['obsrValue'] for i in items if i['category'] == 'T1H')
        reh = next(i['obsrValue'] for i in items if i['category'] == 'REH')
        
        return f"🇰🇷 기상청 실시간 날씨\n현재 기온: {t1h}°C\n습도: {reh}%"
    except Exception as e:
        return "날씨 정보를 불러오는 중입니다. 잠시 후 다시 시도됩니다."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    message = get_korea_weather()
    send_telegram(message)
