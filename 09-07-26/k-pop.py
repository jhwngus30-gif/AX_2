import pandas as pd
import streamlit as st

st.title('K-POP 아이돌 데이터셋 기초 탐색')
st.caption('Pandas의 head/tail/shape/info/columns을 데이터셋 기본 정보를 확인합니다.')

upload_file = st.file_uploader('csv 파일을 업로드해주세요.', type='csv')

if upload_file is not None:
    df = pd.read_csv(upload_file)

    st.subheader('1) head() : 데이터의 앞부분 10개 행 미리보기')
    st.dataframe(df.head(10),use_container_width=True)

    st.subheader('2) tail() : 데이터의 뒷부분 10개 행 미리보기')
    st.dataframe(df.tail(10),use_container_width=True)

    st.subheader('3) shape() : (행 개수, 열 개수)')
    col1, col2 = st.columns(2)
    with col1 :
        st.metric('행 개수', f'{df.shape[0]}개')
    with col2 :
        st.metric('열 개수', f'{df.shape[1]}개')

    st.subheader('4) columns : 전체 열(컬럼) 이름 목록')
    st.write(list(df.columns))

    st.subheader('5) info() : 각 열의 자료형과 결측치 여부 요약')
    info_df = pd.DataFrame({
        "타입" : df.dtypes,
        "결측치 아닌 개수" : df.notna().sum(),
        "결측치 개수" : df.isna().sum(),

    })    
    st.dataframe(info_df, use_container_width=True)
    
    st.success('기초 정보 확인 끝났습니다.')

else:
    st.write('파일을 업로드 하세요.')