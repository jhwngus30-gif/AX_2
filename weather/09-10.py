import os
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 파일 경로 기반 .env 절대 경로 지정 (weather 폴더의 상위 폴더인 AX_2 폴더)
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

# .env 파일 강제 로드 (override=True)
is_loaded = load_dotenv(dotenv_path=dotenv_path, override=True)

WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
EXCHANGE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')

# Streamlit 기본 설정
st.set_page_config(
    page_title="날씨 & 환율 대시보드",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 실시간 날씨 및 환율 정보 서비스")
st.caption("OpenWeatherMap API & ExchangeRate-API 연동")

# 2. 키 확인 및 상세 진단 안내
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("`.env` 파일에서 필요한 API 키를 불러올 수 없습니다.")
    
    with st.expander("🔍 문제 해결 체크리스트 (클릭하여 확인)", expanded=True):
        st.write(f"- **탐색한 .env 파일 경로:** `{dotenv_path}`")
        st.write(f"- **해당 위치에 .env 파일 존재 여부:** `{dotenv_path.exists()}`")
        st.write(f"- **날씨 API 키 로드 여부:** {'✅ 정상' if WEATHER_API_KEY else '❌ 없음'}")
        st.write(f"- **환율 API 키 로드 여부:** {'✅ 정상' if EXCHANGE_API_KEY else '❌ 없음'}")
        
        st.markdown("""
        **확인할 사항:**
        1. 좌측 탐색기 `AX_2` 바로 아래에 있는 `.env` 파일을 열어 `Ctrl + S`로 꼭 저장했는지 확인하세요.
        2. `.env` 파일 안에 변수명이 정확한지 확인하세요:
           ```env
           OPENWEATHER_API_KEY=발급받은_날씨_키
           EXCHANGERATE_API_KEY=발급받은_환율_키
           ```
        3. 등호(`=`) 앞뒤에 띄어쓰기 공백이 없어야 하며, 따옴표(`"`, `'`) 없이 키만 입력해야 합니다.
        """)
    st.stop()

# 3. 사용자 입력 인터페이스
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        city = st.text_input("도시 이름 (영문 입력)", value="Seoul", placeholder="예: Seoul, Tokyo, London, New York")
    with c2:
        base_currency = st.selectbox("환율 기준 통화", options=["USD", "KRW", "EUR", "JPY"], index=0)

if st.button("조회하기", type="primary", use_container_width=True):
    if not city.strip():
        st.warning("도시 이름을 입력해주세요.")
    else:
        # 좌우 2개 컬럼 분할 (왼쪽: 날씨, 오른쪽: 환율)
        weather_col, rate_col = st.columns(2)

        # -----------------------------
        # 1) OpenWeatherMap 날씨 조회
        # -----------------------------
        with weather_col:
            st.subheader(f"⛅ {city.strip().capitalize()} 날씨")
            weather_url = "https://api.openweathermap.org/data/2.5/weather"
            w_params = {
                "q": city.strip(),
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "lang": "kr"
            }

            try:
                w_resp = requests.get(weather_url, params=w_params, timeout=5)
                w_data = w_resp.json()

                if w_resp.status_code == 200:
                    weather_desc = w_data["weather"][0]["description"]
                    icon_code = w_data["weather"][0]["icon"]
                    temp = w_data["main"]["temp"]
                    feels_like = w_data["main"]["feels_like"]
                    humidity = w_data["main"]["humidity"]
                    wind_speed = w_data["wind"]["speed"]
                    country = w_data["sys"].get("country", "")

                    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

                    sub1, sub2 = st.columns([1, 2])
                    with sub1:
                        st.image(icon_url, width=100)
                    with sub2:
                        st.write(f"**국가:** {country}")
                        st.metric(label="현재 기온", value=f"{temp}°C", delta=f"체감 {feels_like}°C")

                    st.write(f"**상태:** {weather_desc}")
                    st.write(f"**습도:** {humidity}% | **풍속:** {wind_speed} m/s")

                elif w_resp.status_code == 404:
                    st.error("도시를 찾을 수 없습니다. 영문 철자를 확인해주세요.")
                elif w_resp.status_code == 401:
                    st.error("날씨 API 키가 인증되지 않았습니다. 키를 다시 확인해주세요.")
                else:
                    st.error(f"날씨 API 오류: {w_data.get('message', '알 수 없음')}")

            except requests.exceptions.RequestException as e:
                st.error(f"날씨 네트워크 오류: {e}")

        # -----------------------------
        # 2) ExchangeRate-API 환율 조회
        # -----------------------------
        with rate_col:
            st.subheader(f"💵 실시간 환율 (기준: 1 {base_currency})")
            rate_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}"

            try:
                r_resp = requests.get(rate_url, timeout=5)
                r_data = r_resp.json()

                if r_resp.status_code == 200 and r_data.get("result") == "success":
                    rates = r_data.get("conversion_rates", {})
                    last_update = r_data.get("time_last_update_utc", "")[:16]

                    target_currencies = ["KRW", "USD", "EUR", "JPY"]
                    target_currencies = [c for c in target_currencies if c != base_currency]

                    cols = st.columns(len(target_currencies))
                    for idx, cur in enumerate(target_currencies):
                        rate_val = rates.get(cur, 0.0)
                        cols[idx].metric(label=f"1 {base_currency} ➡️ {cur}", value=f"{rate_val:,.2f}")

                    st.caption(f"기준 업데이트: {last_update} UTC")

                elif r_data.get("error-type") == "invalid-key":
                    st.error("환율 API 키가 올바르지 않습니다.")
                else:
                    st.error(f"환율 API 오류: {r_data.get('error-type', '알 수 없음')}")

            except requests.exceptions.RequestException as e:
                st.error(f"환율 네트워크 오류: {e}")