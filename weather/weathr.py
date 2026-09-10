import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 로컬 환경용 .env 로드 (배포 환경에서는 파일이 없어도 에러 없이 넘어감)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)

# 2. Streamlit Secrets(클라우드) 우선 조회 -> 없으면 로컬 환경변수(os.getenv) 조회
WEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", os.getenv("OPENWEATHER_API_KEY"))
EXCHANGE_API_KEY = st.secrets.get("EXCHANGERATE_API_KEY", os.getenv("EXCHANGERATE_API_KEY"))

# Streamlit 기본 설정
st.set_page_config(
    page_title="날씨 & 환율 대시보드",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 실시간 날씨 및 환율 정보 서비스")
st.caption("OpenWeatherMap API & ExchangeRate-API 연동")

# 3. 키 확인 및 안내
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("API 키를 불러올 수 없습니다. Streamlit Secrets 또는 .env 파일을 설정해주세요.")
    st.info("""
    **Streamlit Cloud 배포 환경 설정법:**
    1. Streamlit 앱 우측 하단 관리 창에서 **Settings** -> **Secrets** 이동
    2. 아래 내용을 추가 후 저장:
    ```toml
    OPENWEATHER_API_KEY = "발급받은_날씨_키"
    EXCHANGERATE_API_KEY = "발급받은_환율_키"
    ```
    """)
    st.stop()