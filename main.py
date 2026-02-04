import requests
from datetime import datetime

# --- 설정 정보 ---
SERVICE_KEY = "3a47354f399bc29422ac0b77206835227bb518a61dc62911b1d8f137877dbaf9"
TELEGRAM_TOKEN = "8555362302:AAE2Y_BUSsA-sbfhwuOB6qR5AtP-3bdTvmU"
CHAT_ID = "529007689"

def get_weather_report():
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    
    # 1. 기상청 단기예보 (최고/최저 기온, 하늘 상태)
    url_fcst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params_fcst = {
        'serviceKey': requests.utils.unquote(SERVICE_KEY),
        'pageNo': '1', 'numOfRows': '200', 'dataType': 'JSON',
        'base_date': base_date, 'base_time': '0500', 'nx': '60', 'ny': '127'
    }
    
    # 2. 미세먼지 (에어코리아)
    url_dust = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params_dust = {
        'serviceKey': requests.utils.unquote(SERVICE_KEY),
        'returnType': 'json', 'numOfRows': '1', 'pageNo': '1',
        'stationName': '종로구', 'dataTerm': 'DAILY', 'ver': '1.0'
    }

    try:
        # 날씨 파싱
        f_res = requests.get(url_fcst, params=params_fcst).json()
        items = f_res['response']['body']['items']['item']
        
        tmn = next(i['fcstValue'] for i in items if i['category'] == 'TMN') # 최저
        tmx = next(i['fcstValue'] for i in items if i['category'] == 'TMX') # 최고
        sky = next(i['fcstValue'] for i in items if i['category'] == 'SKY') # 하늘상태 (1맑음, 3구름많음, 4흐림)
        
        sky_icon = {'1': '맑음☀️', '3': '구름많음☁️', '4': '흐림☁️'}.get(sky, "정보없음")

        # 미세먼지 파싱
        d_res = requests.get(url_dust, params=params_dust).json()
        d_item = d_res['response']['body']['items'][0]
        pm10 = d_item['pm10Value']
        pm25 = d_item['pm25Value']

        return (
            f"📅 {now.strftime('%m월 %d일')} 모닝 리포트\n"
            f"--------------------------\n"
            f"🌡️ 기온: 최저 {tmn}°C / 최고 {tmx}°C\n"
            f"☁️ 하늘: {sky_icon}\n"
            f"😷 미세먼지: {pm10}㎍/㎥\n"
            f"🌫️ 초미세먼지: {pm25}㎍/㎥\n"
            f"--------------------------\n"
            f"오늘도 지안이랑 행복한 하루 되세요! 😊"
        )
    except Exception as e:
        return f"데이터 연동 중입니다. (에러: {e})"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    msg = get_weather_report()
    send_telegram(msg)
