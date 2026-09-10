import streamlit as st

# st.title('내용') 은 페에지에서 가장 크고 굵은 제목을 만든다.(h1 느낌)
# streamlit run 09-03.py : 실행방법

st.title('무역데이터 부트캠프 자기소개')

# st.header('내용') 은 title보다 한 단계 작은 큰 제목(h2 느낌)
st.header('안녕하세요!🫩 streamlit으로 만든 첫 페이지입니다.')

# st.subheader('내용') 은 header보다 한 단계 작은 큰 제목(h3 느낌)
st.subheader('오늘 배운 내용 : 텍스트 화면에 예쁘게 보여주는 방법')

# st.text('내용') 은 꾸밈이 전혀 없는 순수 텍스트를 그대로 출력
st.text('피곤해 피곤해 피곤해')

# st.caption('내용') 은 아주 작은 글씨로 보조설명을 넣을 때
st.caption('집에 너무 가고싶어....')

# st.markdown("")  :  마크다운 문법 굵게, 기울림, 링크, 목록 등
# st.markdown("---")  :  마크다운 문법
st.markdown(
    """
    ### 📌 마크다운으로 작성한 자기소개
    - **이름** : 홍길동
    - **관심분야** : *데이터분석*, 무역데이터  시각화
    - **목표** : 나만의 대시보드 만들기
    - 참고링크 : [네이버] http://www.naver.com
"""
)
st.markdown('---')

st.subheader('오늘 배운 한 줄 코드')
st.code(
    """
    st.title('hello streamlit!')
"""
)