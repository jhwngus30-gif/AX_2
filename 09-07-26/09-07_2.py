"""
타이타닉 데이터 필터링, 결측치 정리
age(나이)가 35 이상인 승객 필터링
Sex(성별)별로 필터링
titanic_cleaned.csv로 저장
실행방법 : streamlit run 09-04_2.py
"""

import pandas as pd
import streamlit as st
import os

st.title('🚢타이타닉 데이터 필터링 & 결측치 정리')
st.caption('나이/성별 조건으로 필터링 해보고, 결측치를 제거해 새 csv 로 저장합니다.')

csv_path = os.path.join(os.path.dirname(__file__), "..", 'csv_file', 'Titanic.csv')

try : 
    df = pd.read_csv(csv_path)
except FileNotFoundError :
    st.error('❌titanic.csv 파일을 찾을 수 없습니다.')

else :
    st.metric('원본 데이터 행 개수', f'{len(df)}행')

    st.markdown('---')

    # Age 35세 이상 필터링
    st.subheader('1) 나이 35세 이상 승객')

    df_age = df[df['Age']>=35]
    #df[df[]] : df 조건을 만족하면 df에 넣어라...?
    st.write(f'나이 35세 이상 승객 수: **{len(df_age)}**명')
    st.dataframe(df_age[['Name','Sex','Age']].head(),use_container_width=True)
    #여러 열을 선택할 때는 열 이름들을 파이썬 리스트([...]) 형태로 묶어서 전달해야 합니다. 즉, 대괄호를 두 겹([[...]])으로 감싸주어야 합니다.

    st.markdown('---')

    # 성별 여자 남자 필터링 2컬럼 사용
    st.subheader('2) 성별 필터링 결과')
    female_df = df[df['Sex'] == 'female']
    male_df = df[df['Sex'] == 'male']
    col1, col2 = st.columns(2)
    with col1:
        st.metric('여성 승객 수', f'**{len(female_df)}**명')
    with col2:
        st.metric('남성 승객 수', f'**{len(male_df)}**명')

    st.markdown('---')

    #  두 조건을 동시에 만족하는 행(35세 이상 여성)
    st.subheader('3) 35세 이상 & 여성 승객 ')
    df_and = df[(df['Age'] >= 35) & (df['Sex'] == 'female')]
    st.write(f'35세 이상인 여성 승객의 수: **{len(df_and)}**명')

    st.markdown('---')

    # 나이의 결측치(NaN) 확인 및 dropna 처리
    st.subheader('4) Age 결측치 처리')
    missing_age_count = df['Age'].isna().sum() #isna()는 결측치면 True롤 반환, sum() 누적합을 나타낸다
    st.write(f'Age 열의 결측치 개수: **{missing_age_count}**개')

    # subset=['Age'] : Age 열의 결측치인 행만 골라서 제거한다.
    df_clean = df.dropna(subset=['Age'])
    col1, col2 = st.columns(2)
    with col1:
        st.metric('제거 전', f'**{len(df)}**행')
    with col2:
        st.metric('제거 후', f'**{len(df_clean)}**행')

    st.markdown('---')

    # 정리된 데이터를 csv 파일로 저장
    output_path = 'titanic_cleaned.csv'
    df_clean.to_csv(output_path, index=False)

    st.success('파일을 저장했습니다.')
    st.dataframe(df_clean.head(),use_container_width=True)
