import requests
from datetime import datetime, timedelta, timezone

# --- 설정 정보 (규환님 정보 고정) ---
SERVICE_KEY = "3a47354f399bc29422ac0b77206835227bb518a61dc62911b1d8f137877dbaf9"
TELEGRAM_TOKEN = "8555362302:AAE2Y_BUSsA-sbfhwuOB6qR5AtP-3bdTvmU"
CHAT_ID = "529007689"

# 행당역(성동구)과 당산역(영등포구) 설정
LOCATIONS = [
    ["행당역 (성동구)", 61, 126, "성동구"],
    ["당산역 (영등포구)", 58, 126, "영등포구"]
]

# 한국 시간대(KST) 설정
KST = timezone(timedelta(hours=9))

def get_weather_info(nx, ny):
    now = datetime.now(KST)
    base_date = now.strftime("%Y%m%d")
    url_ncst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    url_fcst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    # 오전 7시 알림용 데이터 기준 시간
    base_time = "0600"
    
    try:
        # 1. 현재 기온 및 강수 상태
        nc_res = requests.get(url_ncst, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time, 'nx': nx, 'ny': ny}, timeout=10).json()
        n_items = nc_res['response']['body']['items']['item']
        cur_t = next(i['obsrValue'] for i in n_items if i['category'] == 'T1H')
        pty = next(i['obsrValue'] for i in n_items if i['category'] == 'PTY')
        status = "맑음☀️" if pty == "0" else "비/눈 내림🌧"
        
        # 2. 오늘 전체 시간 중 비 예보(강수확률 40% 이상) 확인
        fc_res = requests.get(url_fcst, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'pageNo': '1', 'numOfRows': '200', 'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 'nx': nx, 'ny': ny}, timeout=10).json()
        f_items = fc_res['response']['body']['items']['item']
        pop_list = [int(i['fcstValue']) for i in f_items if i['category'] == 'POP']
        rain_alert = "⚠️ 비 예보 있음 (우산 챙기세요!)" if any(p >= 40 for p in pop_list) else ""
        
        return f"🌡 기온: {cur_t}°C ({status})\n{rain_alert}".strip()
    except:
        return "🌡 날씨: 정보 업데이트 중"

def get_dust_info(station):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'returnType': 'json', 'stationName': station, 'dataTerm': 'DAILY', 'ver': '1.0'}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        item = res['response']['body']['items'][0]
        pm10 = int(item['pm10Value']) if item['pm10Value'].isdigit() else 0
        
        if pm10 <= 30: grade = "좋음💙"
        elif pm10 <= 80: grade = "보통💚"
        elif pm10 <= 150: grade = "나쁨🧡"
        else: grade = "매우나쁨❤️"
        
        return f"😷 미세먼지: {pm10} ({grade})"
    except:
        return "😷 미세먼지: 점검 중"

if __name__ == "__main__":
    now_kst = datetime.now(KST)
    current_date = now_kst.strftime('%m월 %d일')
    header = f"🗓 *{current_date} 통합 날씨 리포트*\n\n"
    body = ""
    
    for loc in LOCATIONS:
        body += f"📍 *{loc[0]}*\n"
        body += "━━━━━━━━━━━━━━\n"
        body += f"{get_weather_info(loc[1], loc[2])}\n"
        body += f"{get_dust_info(loc[3])}\n\n"
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": header + body, "parse_mode": "Markdown"})
