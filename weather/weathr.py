import os
import requests
import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from dotenv import load_dotenv

# Streamlit 기본 설정
st.set_page_config(
    page_title="여행 수첩: 날씨 & 환율",
    page_icon="✏️",
    layout="centered"
)

# -----------------------------
# 0) 핸드스케치 모눈종이 커스텀 CSS 주입
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&display=swap');

/* 전체 배경: 모눈종이 도트 패턴 및 손글씨 폰트 */
html, body, [class*="css"], .stApp {
    font-family: 'Gaegu', cursive !important;
    font-size: 21px;
    background-color: #fbfbf9 !important;
    background-image: radial-gradient(#cbd5e1 1.4px, transparent 1.4px) !important;
    background-size: 18px 18px !important;
    color: #1e293b !important;
}

/* Streamlit 테두리 컨테이너를 비대칭 손그림 카드로 변환 */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #2d3748 !important;
    border-radius: 255px 15px 225px 15px/15px 225px 15px 255px !important;
    background-color: #ffffff !important;
    box-shadow: 3px 4px 0px #2d3748 !important;
    padding: 18px 22px !important;
    margin-bottom: 20px !important;
}

/* 형광펜 배지 라벨 */
.sketch-badge {
    display: inline-block;
    background-color: #bbf7d0;
    border: 1.5px solid #16a34a;
    border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
    padding: 2px 12px;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
    color: #166534;
}

/* 주황색 손그림 버튼 */
.stButton > button {
    font-family: 'Gaegu', cursive !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    background-color: #fed7aa !important;
    color: #7c2d12 !important;
    border: 2px solid #2d3748 !important;
    border-radius: 255px 25px 225px 25px/25px 225px 25px 255px !important;
    box-shadow: 3px 4px 0px #2d3748 !important;
    transition: 0.1s ease-in-out;
}
.stButton > button:hover {
    transform: translate(2px, 2px);
    box-shadow: 1px 2px 0px #2d3748 !important;
    background-color: #fdba74 !important;
}

/* 입력창 및 선택창 손그림 스타일 */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    border: 2px solid #2d3748 !important;
    border-radius: 180px 15px 190px 15px/15px 190px 15px 180px !important;
    background-color: #ffffff !important;
    box-shadow: 2px 2px 0px #94a3b8 !important;
    font-family: 'Gaegu', cursive !important;
    font-size: 20px !important;
}

/* 점선 구분선 */
hr {
    border: none !important;
    border-top: 2px dashed #94a3b8 !important;
    margin: 24px 0 !important;
}

/* 통계 메트릭 폰트 */
[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-family: 'Gaegu', cursive !important;
}
</style>
""", unsafe_allow_html=True)

# 1. 로컬 환경용 .env 로드
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)

# 2. API 키 안전 로드
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

# 메인 타이틀 헤더
st.markdown("<h1 style='text-align: center; font-size: 44px; margin-bottom: 0;'>✏️ Visit & Travel Diary</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 22px; color: #64748b; margin-top: 4px;'>Find your city weather & live exchange rate</p>", unsafe_allow_html=True)

# 3. 키 확인 및 배포 안내
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("🚨 API 키를 불러오지 못했습니다!")
    st.write(f"- 날씨 키 상태: {'✅ 로드됨' if WEATHER_API_KEY else '❌ 누락됨'}")
    st.write(f"- 환율 키 상태: {'✅ 로드됨' if EXCHANGE_API_KEY else '❌ 누락됨'}")
    st.warning("우측 하단 Manage app -> Settings -> Secrets에 키를 입력하고 Save를 눌러주세요.")
    st.stop()

# 4. 수첩 상태(Session State) 초기화
if "opened" not in st.session_state:
    st.session_state.opened = False

# 5. 상단 검색 카드
with st.container(border=True):
    st.markdown('<span class="sketch-badge">Where to travel?</span>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        city = st.text_input("도시 이름 (영문 입력)", value="Seoul", placeholder="예: Seoul, Dublin, Tokyo, Paris")
    with c2:
        base_currency = st.selectbox("환율 기준 통화", options=["USD", "KRW", "EUR", "JPY"], index=0)

    # 버튼 클릭 시 session_state를 True로 변경
    if st.button("📖 수첩 열어보기", type="primary", use_container_width=True):
        if not city.strip():
            st.warning("도시 이름을 입력해주세요.")
            st.session_state.opened = False
        else:
            st.session_state.opened = True

# 6. 버튼을 눌렀을 때만 하단 내용 표시
if st.session_state.opened and city.strip():
    col_weather, col_rate = st.columns(2)

    # -----------------------------
    # 1) OpenWeatherMap 날씨 카드
    # -----------------------------
    with col_weather:
        with st.container(border=True):
            st.markdown(f'<span class="sketch-badge">⛅ {city.strip().capitalize()} 날씨</span>', unsafe_allow_html=True)
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
                        st.image(icon_url, width=80)
                    with sub2:
                        st.write(f"**국가:** {country}")
                        st.metric(label="현재 기온", value=f"{temp}°C", delta=f"체감 {feels_like}°C")

                    st.write(f"**상태:** {weather_desc}")
                    st.write(f"**습도:** {humidity}% | **풍속:** {wind_speed} m/s")

                elif w_resp.status_code == 404:
                    st.error("도시를 찾을 수 없습니다. 영문 철자를 확인해주세요.")
                elif w_resp.status_code == 401:
                    st.error("날씨 API 키가 인증되지 않았습니다.")
                else:
                    st.error(f"날씨 API 오류: {w_data.get('message', '알 수 없음')}")

            except requests.exceptions.RequestException as e:
                st.error(f"날씨 네트워크 오류: {e}")

    # -----------------------------
    # 2) ExchangeRate-API 실시간 환율 카드
    # -----------------------------
    with col_rate:
        with st.container(border=True):
            st.markdown(f'<span class="sketch-badge">💵 실시간 환율 (1 {base_currency})</span>', unsafe_allow_html=True)
            rate_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}"

            try:
                r_resp = requests.get(rate_url, timeout=5)
                r_data = r_resp.json()

                if r_resp.status_code == 200 and r_data.get("result") == "success":
                    rates = r_data.get("conversion_rates", {})
                    last_update = r_data.get("time_last_update_utc", "")[:16]

                    target_currencies = ["KRW", "USD", "EUR", "JPY"]
                    target_currencies = [c for c in target_currencies if c != base_currency]

                    for cur in target_currencies:
                        rate_val = rates.get(cur, 0.0)
                        st.write(f"👉 **1 {base_currency}** = **{rate_val:,.2f} {cur}**")

                    st.caption(f"업데이트: {last_update} UTC")

                elif r_data.get("error-type") == "invalid-key":
                    st.error("환율 API 키가 올바르지 않습니다.")
                else:
                    st.error(f"환율 API 오류: {r_data.get('error-type', '알 수 없음')}")

            except requests.exceptions.RequestException as e:
                st.error(f"환율 네트워크 오류: {e}")

    # -----------------------------
    # 3) 일자별 환율 변동 추이 카드
    # -----------------------------
    with st.container(border=True):
        st.markdown('<span class="sketch-badge">📈 일자별 환율 변동 추이</span>', unsafe_allow_html=True)

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

            with st.spinner(f"{period_label} 데이터를 스케치하는 중..."):
                try:
                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(period=selected_period, interval="1d")

                    if not hist.empty:
                        chart_df = pd.DataFrame({
                            "날짜": hist.index.strftime("%m/%d"),
                            "종가 환율": hist["Close"].round(2)
                        })

                        y_min = float(chart_df["종가 환율"].min())
                        y_max = float(chart_df["종가 환율"].max())
                        padding = (y_max - y_min) * 0.15 if y_max != y_min else 1.0

                        chart = (
                            alt.Chart(chart_df)
                            .mark_line(
                                color="#2d3748",
                                strokeWidth=2.5,
                                point=alt.OverlayMarkDef(filled=True, size=50, color="#f472b6")
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
                            .properties(height=280)
                            .interactive()
                        )

                        st.altair_chart(chart, use_container_width=True)

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
                        st.info("선택한 통화쌍의 일별 데이터가 없습니다.")

                except Exception as e:
                    st.error(f"환율 차트 데이터를 가져오지 못했습니다: {e}")

    # -----------------------------
    # 4) 실시간 환율 계산기 카드
    # -----------------------------
    with st.container(border=True):
        st.markdown('<span class="sketch-badge">🧮 실시간 환율 계산기</span>', unsafe_allow_html=True)

        calc_col1, calc_col2, calc_col3 = st.columns([2, 1, 1])

        with calc_col1:
            amount = st.number_input("금액 입력", min_value=0.0, value=77.0, step=10.0, format="%.2f")

        currency_list = ["USD", "KRW", "EUR", "JPY", "CNY", "GBP", "CAD", "AUD"]

        with calc_col2:
            from_currency = st.selectbox("보낸 통화 (From)", options=currency_list, index=0)

        with calc_col3:
            to_currency = st.selectbox("받을 통화 (To)", options=currency_list, index=1)

        if st.button("✏️ 환율 계산하기", use_container_width=True):
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

                        st.markdown(f"<h3 style='text-align: center; color: #be185d; margin: 10px 0;'>{amount:,.2f} {from_currency} ➡️ {converted_result:,.2f} {to_currency}</h3>", unsafe_allow_html=True)
                        st.caption(f"적용 환율: 1 {from_currency} = {unit_rate:,.4f} {to_currency}")
                    else:
                        st.error(f"환율 계산 오류: {c_data.get('error-type', '알 수 없음')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"네트워크 오류: {e}")