import os
import requests
import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
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
# 3) 일자별 환율 변동 추이 (계산기 위로 이동)
# -----------------------------
st.divider()
st.subheader("📅 일자별 환율 변동 추이")

chart_col1, chart_col2, chart_col3 = st.columns([1, 1, 1])

with chart_col1:
    chart_from = st.selectbox("기준 통화", options=["USD", "EUR", "JPY", "GBP"], index=0, key="chart_from")
with chart_col2:
    chart_to = st.selectbox("대상 통화", options=["KRW", "USD", "JPY", "EUR"], index=0, key="chart_to")
with chart_col3:
    period_label = st.selectbox("조회 기간", options=["최근 7일", "최근 1개월", "최근 3개월", "최근 1년"], index=1)

period_map = {
    "최근 7일": "7d",
    "최근 1개월": "1mo",
    "최근 3개월": "3mo",
    "최근 1년": "1y"
}
selected_period = period_map[period_label]

if chart_from == chart_to:
    st.warning("서로 다른 통화를 선택해 주세요.")
else:
    ticker_symbol = f"{chart_from}{chart_to}=X"

    with st.spinner(f"{period_label} 일별 환율 데이터를 불러오는 중..."):
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=selected_period, interval="1d")

            if not hist.empty:
                chart_df = pd.DataFrame({
                    "날짜": hist.index.strftime("%Y-%m-%d"),
                    "종가 환율": hist["Close"].round(2)
                })

                y_min = float(chart_df["종가 환율"].min())
                y_max = float(chart_df["종가 환율"].max())
                padding = (y_max - y_min) * 0.15 if y_max != y_min else 1.0

                chart = (
                    alt.Chart(chart_df)
                    .mark_line(
                        color="#FF4B4B",
                        strokeWidth=3,
                        point=alt.OverlayMarkDef(filled=True, size=50, color="#FF4B4B")
                    )
                    .encode(
                        x=alt.X("날짜:N", title="날짜", axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y(
                            "종가 환율:Q",
                            title=f"환율 ({chart_to})",
                            scale=alt.Scale(domain=[y_min - padding, y_max + padding], zero=False),
                            axis=alt.Axis(format=",.2f")
                        ),
                        tooltip=["날짜", "종가 환율"]
                    )
                    .interactive()
                )

                st.altair_chart(chart, use_container_width=True)

                # 기간 변동 통계
                start_val = float(hist["Close"].iloc[0])
                latest_val = float(hist["Close"].iloc[-1])
                diff = latest_val - start_val
                pct_diff = (diff / start_val) * 100

                m1, m2, m3 = st.columns(3)
                m1.metric(label="최근 마감 환율", value=f"{latest_val:,.2f} {chart_to}")
                m2.metric(label=f"{period_label} 변동폭", value=f"{diff:+,.2f}", delta=f"{pct_diff:+.2f}%")
                m3.metric(
                    label="기간 최고 / 최저",
                    value=f"{hist['High'].max():,.2f}",
                    delta=f"최저 {hist['Low'].min():,.2f}",
                    delta_color="off"
                )
            else:
                st.info("선택한 통화쌍에 대한 일별 데이터가 없습니다.")

        except Exception as e:
            st.error(f"환율 차트 데이터를 가져오지 못했습니다: {e}")

# -----------------------------
# 4) 실시간 환율 계산기 (하단 배치)
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