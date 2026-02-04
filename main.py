import requests
from datetime import datetime

# --- 설정 정보 ---
SERVICE_KEY = "3a47354f399bc29422ac0b77206835227bb518a61dc62911b1d8f137877dbaf9"
TELEGRAM_TOKEN = "8555362302:AAE2Y_BUSsA-sbfhwuOB6qR5AtP-3bdTvmU"
CHAT_ID = "529007689"

LOCATIONS = [
    ["행당역 (성동구)", 61, 126, "성동구"],
    ["당산역 (영등포구)", 58, 126, "영등포구"]
]

def get_dust_grade(val, is_pm10=True):
    if not val or not val.isdigit(): return "측정중"
    v = int(val)
    if is_pm10: # 미세먼지 기준
        if v <= 30: return "좋음💙"
        if v <= 80: return "보통💚"
        if v <= 150: return "나쁨🧡"
        return "매우나쁨❤️"
    else: # 초미세먼지 기준
        if v <= 15: return "좋음💙"
        if v <= 35: return "보통💚"
        if v <= 75: return "나쁨🧡"
        return "매우나쁨❤️"

def get_styled_report(loc_name, nx, ny, station):
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    
    url_ncst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    url_fcst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    url_dust = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"

    # 실시간 데이터 시간 설정
    base_time_ncst = now.strftime("%H00") if now.minute >= 45 else f"{now.hour-1:02d}00" if now.hour > 0 else "2300"
    
    report = f"📍 *{loc_name}*\n"
    report += "━━━━━━━━━━━━━━\n"

    try:
        # 1. 기온 정보 (실시간 및 예보)
        nc_res = requests.get(url_ncst, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time_ncst, 'nx': nx, 'ny': ny}, timeout=10).json()
        cur_t = next(i['obsrValue'] for i in nc_res['response']['body']['items']['item'] if i['category'] == 'T1H')
        
        fc_res = requests.get(url_fcst, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'pageNo': '1', 'numOfRows': '200', 'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 'nx': nx, 'ny': ny}, timeout=10).json()
        f_items = fc_res['response']['body']['items']['item']
        tmn = next(i['fcstValue'] for i in f_items if i['category'] == 'TMN')
        tmx = next(i['fcstValue'] for i in f_items if i['category'] == 'TMX')
        
        report += f"🌡  *현재 {cur_t}°C* (최저 {tmn}°/최고 {tmx}°)\n"
    except:
        report += "🌡  날씨 정보 점검 중\n"

    try:
        # 2. 미세먼지 정보
        d_res = requests.get(url_dust, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'returnType': 'json', 'stationName': station, 'dataTerm': 'DAILY', 'ver': '1.0'}, timeout=10).json()
        d_item = d_res['response']['body']['items'][0]
        pm10, pm25 = d_item.get('pm10Value'), d_item.get('pm25Value')
        
        report += f"😷  미세먼지: {pm10 if pm10 else '-'} ({get_dust_grade(pm10, True)})\n"
        report += f"🌫  초미세먼지: {pm25 if pm25 else '-'} ({get_dust_grade(pm25, False)})\n"
    except:
        report += "😷  먼지 정보 점검 중\n"

    return report + "\n"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    header = f"🗓 *{datetime.now().strftime('%m월 %d일')} 통합 날씨 리포트*\n\n"
    body = "".join(get_styled_report(loc[0], loc[1], loc[2], loc[3]) for loc in LOCATIONS)
    send_telegram(header + body)
