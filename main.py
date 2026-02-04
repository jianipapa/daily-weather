import requests
from datetime import datetime

# --- 설정 정보 ---
SERVICE_KEY = "3a47354f399bc29422ac0b77206835227bb518a61dc62911b1d8f137877dbaf9"
TELEGRAM_TOKEN = "8555362302:AAE2Y_BUSsA-sbfhwuOB6qR5AtP-3bdTvmU"
CHAT_ID = "529007689"

# 설정: [위치이름, nx, ny, 미세먼지 측정소명]
LOCATIONS = [
    ["행당역(성동구)", 61, 126, "성동구"],
    ["당산역(영등포구)", 58, 126, "영등포구"]
]

def get_combined_report(loc_name, nx, ny, station):
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    
    # 1. 날씨 데이터 (단기예보)
    url_w = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params_w = {
        'serviceKey': requests.utils.unquote(SERVICE_KEY),
        'pageNo': '1', 'numOfRows': '200', 'dataType': 'JSON',
        'base_date': base_date, 'base_time': '0500', 'nx': nx, 'ny': ny
    }
    
    # 2. 미세먼지 데이터
    url_d = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params_d = {
        'serviceKey': requests.utils.unquote(SERVICE_KEY),
        'returnType': 'json', 'numOfRows': '1', 'stationName': station, 'dataTerm': 'DAILY', 'ver': '1.0'
    }

    try:
        # 날씨 파싱
        w_res = requests.get(url_w, params=params_w, timeout=10).json()
        items = w_res['response']['body']['items']['item']
        tmn = next(i['fcstValue'] for i in items if i['category'] == 'TMN')
        tmx = next(i['fcstValue'] for i in items if i['category'] == 'TMX')
        sky = next(i['fcstValue'] for i in items if i['category'] == 'SKY')
        sky_name = {'1': '맑음☀️', '3': '구름많음☁️', '4': '흐림☁️'}.get(sky, "정보없음")

        # 미세먼지 파싱
        d_res = requests.get(url_d, params=params_d, timeout=10).json()
        d_item = d_res['response']['body']['items'][0]
        pm10 = d_item.get('pm10Value', '-')
        pm25 = d_item.get('pm25Value', '-')

        return (
            f"📍 {loc_name} 리포트\n"
            f"🌡️ 최저 {tmn}°C / 최고 {tmx}°C\n"
            f"☁️ 하늘: {sky_name}\n"
            f"😷 미세먼지: {pm10} / 초미세: {pm25}\n"
        )
    except:
        return f"📍 {loc_name}: 데이터 업데이트 중입니다.\n"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    final_msg = f"📅 {datetime.now().strftime('%m월 %d일')} 통합 날씨 리포트\n\n"
    for loc in LOCATIONS:
        final_msg += get_combined_report(loc[0], loc[1], loc[2], loc[3]) + "\n"
    
    final_msg += "오늘도 지안이랑 행복한 하루 되세요! 😊"
    send_telegram(final_msg)
