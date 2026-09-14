import streamlit as st

st.set_page_config(page_title="세계여행 포털", page_icon="🌍")

home_page = st.page('view/HOME.py',title ='홈',icon='',default=True)
usa_page = st.page('view/USA.PY', title = '미국', icon='', default=True)
china_page = st.page('view/CHINA.PY', title = '중국', icon='', default=True)
japan_page = st.page('view/JAPAN.PY', title = '일본', icon='', default=True)

pg = st.navigation([home_page,usa_page,china_page,japan_page])
pg.run()