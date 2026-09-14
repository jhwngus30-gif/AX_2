import streamlit as st
from pathlib import Path
from PIL import Image
from src.data.country_info import COUNTRIES_DATA

st.set_page_config(
    page_title="글로벌 여행 정보 포털",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 현재 파일(app.py) 기준 assets 폴더 경로 설정
CURRENT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = CURRENT_DIR / "assets"

# 사이드바 국가 네비게이션
st.sidebar.title("🌏 여행지 선택")
country_options = list(COUNTRIES_DATA.keys())
selected_country = st.sidebar.radio(
    "탐색할 국가를 선택하세요:",
    country_options,
    index=0  # 기본값: 대한민국 (홈)
)

country = COUNTRIES_DATA[selected_country]

# 헤더 영역
badge = "📍 HOME" if country.get("is_home", False) else "✈️ DESTINATION"
st.caption(badge)
st.title(f"{selected_country} ({country['eng_name']})")

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("개요")
    st.write(country["description"])
    
    st.markdown("---")
    st.markdown("**공식 관광 포털**")
    st.link_button(
        label=f"🔗 {country['site_name']} 바로가기",
        url=country["site_url"],
        use_container_width=True
    )

with col2:
    # 이미지 렌더링 (Pathlib 기반 절대/상대 안전 경로)
    image_path = ASSETS_DIR / country["image_name"]
    
    if image_path.is_file():
        image = Image.open(image_path)
        st.image(image, caption=f"{selected_country} 대표 풍경", use_container_width=True)
    else:
        st.warning(f"⚠️ 이미지를 찾을 수 없습니다: `{image_path.name}`")
        st.info(f"💡 `assets/{country['image_name']}` 위치에 이미지를 추가해 주세요.")

# 상세 스펙 테이블 카드
st.markdown("---")
st.subheader("📌 기본 여행 정보")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="수도", value=country["capital"])
with m2:
    st.metric(label="사용 통화", value=country["currency"])
with m3:
    st.metric(label="공용어", value=country["language"])