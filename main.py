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
    
    # 1. 현재 기온 가져오기 (초단기실황)
    url_ncst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    base_time_ncst = now.strftime("%H00") if now.minute >= 45 else f"{now.hour-1:02d}00" if now.hour > 0 else "2300"
    params_ncst = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time_ncst, 'nx': nx, 'ny': ny}
    
    # 2. 최저/최고 기온 및 하늘상태 가져오기 (단기예보 - 05시 발표 기준)
    url_fcst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params_fcst = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'pageNo': '1', 'numOfRows': '200', 'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 'nx': nx, 'ny': ny}
    
    # 3. 미세먼지 데이터
    url_dust = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params_dust = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'returnType': 'json', 'stationName': station, 'dataTerm': 'DAILY', 'ver': '1.0'}

    report_parts = [f"📍 {loc_name}"]
    
    try:
        # 실시간 기온 파싱
        ncst_res = requests.get(url_ncst, params=params_ncst, timeout=10).json()
        ncst_items = ncst_res['response']['body']['items']['item']
        current_temp = next(i['obsrValue'] for i in ncst_items if i['category'] == 'T1H')
        
        # 최저/최고/하늘상태 파싱
        fcst_res = requests.get(url_fcst, params=params_fcst, timeout=10).json()
        fcst_items = fcst_res['response']['body']['items']['item']
        tmn = next(i['fcstValue'] for i in fcst_items if i['category'] == 'TMN')
        tmx = next(i['fcstValue'] for i in fcst_items if i['category'] == 'TMX')
        sky = next(i['fcstValue'] for i in fcst_items if i['category'] == 'SKY')
        sky_name = {'1': '맑음☀️', '3': '구름많음☁️', '4': '흐림☁️'}.get(sky, "정보없음")
        
        report_parts.append(f"🌡️ 기온: 현재 {current_temp}°C (최저 {tmn}° / 최고 {tmx}°)")
        report_parts.append(f"☁️ 하늘: {sky_name}")
    except:
        report_parts.append("🌡️ 날씨: 정보 업데이트 대기 중")

    try:
        # 미세먼지 파싱
        d_res = requests.get(url_dust, params=params_dust, timeout=10).json()
        d_item = d_res['response']['body']['items'][0]
        pm10 = d_item.get('pm10Value', '-')
        pm25 = d_item.get('pm25Value', '-')
        report_parts.append(f"😷 미세먼지: {pm10} / 초미세: {pm25}")
    except:
        report_parts.append("😷 미세먼지: 점검 중")

    return "\n".join(report_parts) + "\n"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    header = f"📅 {datetime.now().strftime('%m월 %d일')} 통합 날씨 리포트\n\n"
    body = "".join(get_combined_report(loc[0], loc[1], loc[2], loc[3]) for loc in LOCATIONS)
    send_telegram(header + body)
