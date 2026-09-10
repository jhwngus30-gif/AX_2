import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Streamlit 기본 설정
st.set_page_config(
    page_title="날씨 & 환율 대시보드",
    page_icon="🌍",
    layout="wide"
)

# 1. 로컬 환경용 .env 로드
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)

# 2. 키 조회 (Secrets 우선, 없을 시 os.getenv)
WEATHER_API_KEY = None
EXCHANGE_API_KEY = None

try:
    if "OPENWEATHER_API_KEY" in st.secrets:
        WEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except Exception:
    pass

try:
    if "EXCHANGERATE_API_KEY" in st.secrets:
        EXCHANGE_API_KEY = st.secrets["EXCHANGERATE_API_KEY"]
except Exception:
    pass

if not WEATHER_API_KEY:
    WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not EXCHANGE_API_KEY:
    EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

st.title("🌍 실시간 날씨 및 환율 정보 서비스")
st.caption("OpenWeatherMap API & ExchangeRate-API 연동")

# 3. 키 확인 및 안내
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("🚨 API 키를 불러오지 못했습니다!")
    st.write(f"- 날씨 키 상태: {'✅ 로드됨' if WEATHER_API_KEY else '❌ 누락됨'}")
    st.write(f"- 환율 키 상태: {'✅ 로드됨' if EXCHANGE_API_KEY else '❌ 누락됨'}")
    st.warning("우측 하단 Manage app -> Settings -> Secrets에 키를 입력하고 Save를 눌러주세요.")
    st.stop()

# 4. 사용자 입력 인터페이스
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

# -----------------------------
# 3) 실시간 환율 계산기
# -----------------------------
st.divider()
st.subheader("🧮 실시간 환율 계산기")

calc_col1, calc_col2, calc_col3 = st.columns([2, 1, 1])

with calc_col1:
    amount = st.number_input("금액 입력", min_value=0.0, value=1.0, step=10.0, format="%.2f")

currency_list = ["USD", "KRW", "EUR", "JPY", "CNY", "GBP", "CAD", "AUD"]

with calc_col2:
    from_currency = st.selectbox("보낸 통화 (From)", options=currency_list, index=0)

with calc_col3:
    to_currency = st.selectbox("받을 통화 (To)", options=currency_list, index=1)

if st.button("계산하기", use_container_width=True):
    if from_currency == to_currency:
        st.info(f"**결과:** {amount:,.2f} {from_currency} = **{amount:,.2f} {to_currency}**")
    else:
        calc_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{from_currency}/{to_currency}/{amount}"
        try:
            c_resp = requests.get(calc_url, timeout=5)
            c_data = c_resp.json()

            if c_resp.status_code == 200 and c_data.get("result") == "success":
                converted_result = c_data.get("conversion_result", 0.0)
                unit_rate = c_data.get("conversion_rate", 0.0)

                st.success(f"### {amount:,.2f} {from_currency} = **{converted_result:,.2f} {to_currency}**")
                st.caption(f"적용 환율: 1 {from_currency} = {unit_rate:,.4f} {to_currency}")
            else:
                st.error(f"환율 계산 오류: {c_data.get('error-type', '알 수 없음')}")
        except requests.exceptions.RequestException as e:
            st.error(f"네트워크 오류: {e}")