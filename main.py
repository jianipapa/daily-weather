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

def get_report(loc_name, nx, ny, station):
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    report = f"📍 *{loc_name}*\n━━━━━━━━━━━━━━\n"
    
    # 1. 날씨 시도
    try:
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        params = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'pageNo': '1', 'numOfRows': '50', 'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 'nx': nx, 'ny': ny}
        res = requests.get(url, params=params, timeout=10).json()
        items = res['response']['body']['items']['item']
        tmn = next(i['fcstValue'] for i in items if i['category'] == 'TMN')
        tmx = next(i['fcstValue'] for i in items if i['category'] == 'TMX')
        report += f"🌡  기온: 최저 {tmn}° / 최고 {tmx}°\n"
    except:
        report += "🌡  날씨: 데이터 준비 중\n"

    # 2. 미세먼지 시도
    try:
        url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
        params = {'serviceKey': requests.utils.unquote(SERVICE_KEY), 'returnType': 'json', 'stationName': station, 'dataTerm': 'DAILY', 'ver': '1.0'}
        res = requests.get(url, params=params, timeout=10).json()
        item = res['response']['body']['items'][0]
        pm10 = item.get('pm10Value', '-')
        report += f"😷  미세먼지: {pm10} ㎍/㎥\n"
    except:
        report += "😷  먼지: 데이터 점검 중\n"

    return report + "\n"

if __name__ == "__main__":
    header = f"🗓 *{datetime.now().strftime('%m월 %d일')} 날씨 리포트*\n\n"
    content = ""
    for loc in LOCATIONS:
        content += get_report(loc[0], loc[1], loc[2], loc[3])
    
    # 메시지 전송 테스트용 출력
    print(header + content)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": header + content, "parse_mode": "Markdown"})
