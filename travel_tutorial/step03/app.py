import streamlit as st

st.set_page_config(page_title="세계여행 포털", page_icon="🌍")

# 각 페이지 정의
home_page = st.Page("country/HOME.py", title="홈", icon="🏠", default=True)
usa = st.Page("country/USA.py", title="미국", icon="🇺🇸")
china = st.Page("country/CHINA.py", title="중국", icon="🇨🇳")
japan = st.Page("country/JAPAN.py", title="일본", icon="🇯🇵")

# 네비게이션 메뉴 가동 (사이드바 메뉴 자동 생성)
pg = st.navigation([home_page, usa, china, japan])
pg.run()