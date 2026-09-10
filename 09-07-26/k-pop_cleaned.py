"""
k-pop 데이터 필터링, 결측치 정리
Gender(성별)별로 필터링
k-pop_cleaned.csv 로 저장
"""

import pandas as pd
import streamlit as st
import os

st.title('K-POP 아이돌 데이터 필터링 & 결측치 정리')
st.caption('성별 조건으로 필터링 해보고, 결측치를 제거 해 새 csv로 저장합니다.')

upload_file = st.file_uploader('csv 파일을 업로드해주세요.', type='csv')

if upload_file is not None:
    df = pd.read_csv(upload_file)

    st.metric('원본 데이터 해 개수', f'**{len(df)}**행')

    st.subheader('성별 필터링 결과')
    female_df = 
    col1, col2 = st.columns(2)
    with col1:
        st.metric('여성 승객 수', f'{len}')



else:
    st.write('csv 파일을 업로드 하세요.')