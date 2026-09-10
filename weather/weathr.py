import os
import requests
import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from dotenv import load_dotenv

# 1. Streamlit 기본 설정
st.set_page_config(
    page_title="여행 수첩: 날씨 & 환율",
    page_icon="✏️",
    layout="centered"  # 모바일/수첩 느낌을 살리기 위해 centered 추천
)

# 2. 핸드드로잉 모눈종이 스타일 커스텀 CSS 주입
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&display=swap');

/* 전체 배경: 도트 그리드(모눈종이) 및 손글씨 폰트 */
html, body, [class*="css"], .stApp {
    font-family: 'Gaegu', cursive !important;
    font-size: 20px;
    background-color: #fbfbf9 !important;
    background-image: radial-gradient(#d1d5db 1.2px, transparent 1.2px) !important;
    background-size: 20px 20px !important;
    color: #2c3e50 !important;
}

/* 손으로 그린 듯한 삐뚤빼뚤 카드 박스 */
.sketch-card {
    border: 2px solid #2b2b2b;
    border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
    padding: 16px 20px;
    margin-bottom: 20px;
    background-color: #ffffff;
    box-shadow: 3px 4px 0px #2b2b2b;
}

/* 형광펜 테두리 카드 (핑크색 강조) */
.sketch-card-pink {
    border: 3px solid #ff76ac;
    border-radius: 12px 255px 15px 255px/255px 15px 255px 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    background-color: #ffffff;
    box-shadow: 3px 4px 0px #ff76ac;
}

/* 형광펜 배지 라벨 (연두색) */
.sketch-badge {
    display: inline-block;
    background-color: #bbf7d0;
    border: 1.5px solid #16a34a;
    border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
    padding: 2px 12px;
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 8px;
}

/* 버튼: 손으로 칠한 주황/피치 톤 버튼 */
.stButton > button {
    font-family: 'Gaegu', cursive !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    background-color: #fed7aa !important;
    color: #431407 !important;
    border: 2px solid #2b2b2b !important;
    border-radius: 255px 25px 225px 25px/25px 225px 25px 255px !important;
    box-shadow: 3px 4px 0px #2b2b2b !important;
    transition: 0.1s ease-in-out;
}
.stButton > button:hover {
    transform: translate(2px, 2px);
    box-shadow: 1px 2px 0px #2b2b2b !important;
    background-color: #fdba74 !important;
}

/* 입력창 & 셀렉트박스 스케치 스타일 */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    border: 2px solid #2b2b2b !important;
    border-radius: 180px 15px 190px 15px/15px 190px 15px 180px !important;
    background-color: #ffffff !important;
    box-shadow: 2px 2px 0px #9ca3af !important;
    font-family: 'Gaegu', cursive !important;
    font-size: 20px !important;
}

/* 구분선 스케치 점선 */
hr {
    border-top: 2px dashed #9ca3af !important;
    margin: 25px 0 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. 로컬 환경용 .env 로드
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)

# 4. API 키 안전 로드
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

# 타이틀 헤더
st.markdown("<h1 style='text-align: center; font-size: 45px;'>✏️ My Travel Diary</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 22px; color: #6b7280;'>Find your city weather & daily exchange rate</p>", unsafe_allow_html=True)

if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("API 키를 찾을 수 없습니다. Streamlit Cloud Secrets를 확인해주세요.")
    st.stop()

# 5. 검색 컨트롤 영역 (핸드드로잉 카드)
st.markdown('<div class="sketch-card">', unsafe_allow_html=True)
st.markdown('<span class="sketch-badge">Where are you going?</span>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
with c1:
    city = st.text_input("목적지 도시 (영문)", value="Dublin", placeholder="예: Dublin, Tokyo, Paris, Seoul")
with c2:
    base_currency = st.selectbox("기준 화폐", options=["USD", "EUR", "KRW", "JPY"], index=1)

search_btn = st.button("🔎 수첩 펼쳐보기", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if search_btn or city:
    # -----------------------------
    # 1) 날씨 & 환율 카드 섹션
    # -----------------------------
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="sketch-card-pink">', unsafe_allow_html=True)
        st.markdown(f'<span class="sketch-badge">Weather in {city.strip().capitalize()}</span>', unsafe_allow_html=True)
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        w_params = {"q": city.strip(), "appid": WEATHER_API_KEY, "units": "metric", "lang": "kr"}

        try:
            w_resp = requests.get(weather_url, params=w_params, timeout=5)
            w_data = w_resp.json()
            if w_resp.status_code == 200:
                temp = w_data["main"]["temp"]
                feels = w_data["main"]["feels_like"]
                desc = w_data["weather"][0]["description"]
                humidity = w_data["main"]["humidity"]
                icon = w_data["weather"][0]["icon"]

                w_c1, w_c2 = st.columns([1, 1.5])
                with w_c1:
                    st.image(f"https://openweathermap.org/img/wn/{icon}@2x.png", width=85)
                with w_c2:
                    st.markdown(f"<h2 style='margin:0; font-size:38px;'>{temp:.1f}°C</h2>", unsafe_allow_html=True)
                    st.write(f"체감: {feels:.1f}°C | {desc}")
                st.write(f"💧 습도: {humidity}% | 💨 바람: {w_data['wind']['speed']} m/s")
            else:
                st.warning("도시를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"날씨 오류: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="sketch-card">', unsafe_allow_html=True)
        st.markdown(f'<span class="sketch-badge">1 {base_currency} Real-time Rate</span>', unsafe_allow_html=True)
        rate_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}"

        try:
            r_resp = requests.get(rate_url, timeout=5)
            r_data = r_resp.json()
            if r_resp.status_code == 200 and r_data.get("result") == "success":
                rates = r_data.get("conversion_rates", {})
                targets = [c for c in ["KRW", "USD", "EUR", "JPY"] if c != base_currency]
                for cur in targets:
                    val = rates.get(cur, 0.0)
                    st.write(f"👉 **1 {base_currency}** = **{val:,.2f} {cur}**")
            else:
                st.warning("환율을 불러오지 못했습니다.")
        except Exception as e:
            st.error(f"환율 오류: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # 2) 일자별 환율 변동 추이 차트
    # -----------------------------
    st.markdown('<div class="sketch-card">', unsafe_allow_html=True)
    st.markdown('<span class="sketch-badge">Rate Trend Chart</span>', unsafe_allow_html=True)

    chart_c1, chart_c2, chart_c3 = st.columns(3)
    with chart_c1:
        chart_from = st.selectbox("기준 통화", options=["USD", "EUR", "JPY", "GBP"], index=1, key="c_from")
    with chart_c2:
        chart_to = st.selectbox("대상 통화", options=["KRW", "USD", "JPY", "EUR"], index=0, key="c_to")
    with chart_c3:
        period_label = st.selectbox("조회 기간", options=["최근 7일", "최근 1개월", "최근 3개월"], index=1)

    period_map = {"최근 7일": "7d", "최근 1개월": "1mo", "최근 3개월": "3mo"}
    
    if chart_from != chart_to:
        ticker = yf.Ticker(f"{chart_from}{chart_to}=X")
        hist = ticker.history(period=period_map[period_label], interval="1d")

        if not hist.empty:
            chart_df = pd.DataFrame({
                "날짜": hist.index.strftime("%m/%d"),
                "환율": hist["Close"].round(2)
            })

            y_min = float(chart_df["환율"].min())
            y_max = float(chart_df["환율"].max())
            pad = (y_max - y_min) * 0.15 if y_max != y_min else 1.0

            chart = (
                alt.Chart(chart_df)
                .mark_line(
                    color="#2b2b2b",  # 손그림 펜 색상(진회색)
                    strokeWidth=2.5,
                    point=alt.OverlayMarkDef(filled=True, size=45, color="#ff76ac") # 핑크색 포인트 점
                )
                .encode(
                    x=alt.X("날짜:N", title="일자", axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("환율:Q", title=f"환율 ({chart_to})", scale=alt.Scale(domain=[y_min - pad, y_max + pad], zero=False)),
                    tooltip=["날짜", "환율"]
                )
                .properties(height=260)
            )
            st.altair_chart(chart, use_container_width=True)

            last_val = float(hist["Close"].iloc[-1])
            start_val = float(hist["Close"].iloc[0])
            diff = last_val - start_val
            pct = (diff / start_val) * 100

            m1, m2, m3 = st.columns(3)
            m1.metric("마감 환율", f"{last_val:,.2f}")
            m2.metric(f"{period_label} 변동", f"{diff:+,.2f}", f"{pct:+.2f}%")
            m3.metric("최고 / 최저", f"{hist['High'].max():,.2f}", f"최저 {hist['Low'].min():,.2f}", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # 3) 실시간 환율 계산기
    # -----------------------------
    st.markdown('<div class="sketch-card-pink">', unsafe_allow_html=True)
    st.markdown('<span class="sketch-badge">Quick Currency Calculator</span>', unsafe_allow_html=True)

    calc1, calc2, calc3 = st.columns([2, 1, 1])
    with calc1:
        amount = st.number_input("환전할 금액", min_value=0.0, value=77.0, step=10.0, format="%.2f")
    with calc2:
        calc_from = st.selectbox("From", ["EUR", "USD", "KRW", "JPY"], index=0, key="calc_from")
    with calc3:
        calc_to = st.selectbox("To", ["KRW", "USD", "EUR", "JPY"], index=0, key="calc_to")

    if st.button("✏️ 계산하기", use_container_width=True):
        if calc_from == calc_to:
            st.info(f"{amount:,.2f} {calc_from} = {amount:,.2f} {calc_to}")
        else:
            c_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{calc_from}/{calc_to}/{amount}"
            try:
                res = requests.get(c_url, timeout=5).json()
                if res.get("result") == "success":
                    ans = res.get("conversion_result", 0.0)
                    st.markdown(f"<h3 style='text-align: center; color: #be185d;'>{amount:,.2f} {calc_from} ➡️ {ans:,.2f} {calc_to}</h3>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"계산 실패: {e}")
    st.markdown('</div>', unsafe_allow_html=True)