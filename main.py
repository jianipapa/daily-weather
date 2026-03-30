import requests
from datetime import datetime, timedelta, timezone

# --- 설정 정보 ---
SERVICE_KEY = "3a47354f399bc29422ac0b77206835227bb518a61dc62911b1d8f137877dbaf9"
TELEGRAM_TOKEN = "8555362302:AAE2Y_BUSsA-sbfhwuOB6qR5AtP-3bdTvmU"
CHAT_ID = "529007689"

LOCATIONS = [
    ["행당역 (성동구)", 61, 126, "성동구"],
    ["당산역 (영등포구)", 58, 126, "영등포구"]
]

KST = timezone(timedelta(hours=9))

def get_weather_info(nx, ny):
    now = datetime.now(KST)
    base_date = now.strftime("%Y%m%d")
    
    # API 주소 최신화 및 안정적 호출 시간 설정
    url_ncst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    url_fcst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    # 새벽 실행 시 05:00 혹은 06:00 데이터 타겟팅
    base_time_ncst = (now - timedelta(hours=1)).strftime("%H00")
    
    try:
        # 1. 현재 기온 및 상태 (초단기실황)
        nc_res = requests.get(url_ncst, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time_ncst, 'nx': nx, 'ny': ny}, timeout=15).json()
        items = nc_res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
        cur_t = next((i['obsrValue'] for i in items if i['category'] == 'T1H'), "-")
        pty = next((i['obsrValue'] for i in items if i['category'] == 'PTY'), "0")
        status = "맑음☀️" if pty == "0" else "비/눈 내림🌧"

        # 2. 오늘 비 예보 확인 (02:00 발표된 단기예보 활용)
        fc_res = requests.get(url_fcst, params={'serviceKey': requests.utils.unquote(SERVICE_KEY), 'pageNo': '1', 'numOfRows': '200', 'dataType': 'JSON', 'base_date': base_date, 'base_time': '0200', 'nx': nx, 'ny': ny}, timeout=15).json()
        f_items = fc_res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        pop_list = [int(i['fcstValue']) for i in f_items if i['category'] == 'POP']
        rain_alert = "\n⚠️ 비 예보 있음 (우산 챙기세요!)" if any(p >= 40 for p in pop_list) else ""
        
        return f"🌡 기온: {cur_t}°C ({status}){rain_alert}"
    except Exception as e:
        return "🌡 날씨: 현재 기상청 서버 점검 중"

def get_dust_info(station):
    # 에어코리아 API 주소는 종종 변경되므로 최신 엔드포인트 사용
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'returnType': 'json', 'stationName': station, 'dataTerm': 'DAILY', 'ver': '1.0'}
    try:
        res = requests.get(url, params=params, timeout=15).json()
        item = res.get('response', {}).get('body', {}).get('items', [{}])[0]
        pm10_val = item.get('pm10Value', '-')
        
        if pm10_val.isdigit():
            v = int(pm10_val)
            if v <= 30: grade = "좋음💙"
            elif v <= 80: grade = "보통💚"
            elif v <= 150: grade = "나쁨🧡"
            else: grade = "매우나쁨❤️"
            return f"😷 미세먼지: {v} ({grade})"
        return f"😷 미세먼지: 측정 데이터 대기 중"
    except:
        return "😷 미세먼지: 정보 수신 지연"

if __name__ == "__main__":
    now_kst = datetime.now(KST)
    current_date = now_kst.strftime('%m월 %d일')
    header = f"🗓 *{current_date} 통합 날씨 리포트*\n\n"
    body = ""
    
    for loc in LOCATIONS:
        body += f"📍 *{loc[0]}*\n━━━━━━━━━━━━━━\n"
        body += f"{get_weather_info(loc[1], loc[2])}\n"
        body += f"{get_dust_info(loc[3])}\n\n"
    
    # 텔레그램 전송 (Markdown 적용)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": header + body, "parse_mode": "Markdown"})
