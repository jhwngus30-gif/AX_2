# 인코딩 자동 감지 + 한글 폰트 막대그래프
# 여러 인코딩 방법('UTF-8-sig','cp949','euc-k') 순서대로 시도
# 내가 쓸 폰트 같은 경로에 있어야 함
# 객실 등급별 생존율 막대그래프 생성 후 그림으로 저장 -> chart.png(확장자:png)
# 실행방법 : streamlit run 09-07_3.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

csv_path = os.path.join(os.path.dirname(__file__), 'titanic_cleaned.csv')
font_path = os.path.join(os.path.dirname(__file__),'..','font','온글잎 콘콘체.ttf')

st.title('📊인코딩 자동 감지 + 한글 폰트 막대그래프(Titanic 연습)')
st.caption('여러 인코딩을 순서대로 시도해서 파일을 열고, 객실등급별 생존율을 그래프로  시각화합니다. ')

def read_csv_wih_auto_encoding(file_source):
    """'utf-8-sig', 'cp949',
    'euc-kr' 순서로 인코딩을 시도하여 CSV를 읽어오는 함수
    """
    encodings = ['utf-8-sig', 'cp949', 'euc-kr']

    for enc in encodings:
        try:
            # Streamlit 파일 객체인 경우 이전 시도에서 읽은 커서를 맨 앞으로 초기화
            if hasattr(file_source, 'seek'):
                file_source.seek(0)

            df = pd.read_csv(file_source, encoding=enc)
            return df, enc
        except (UnicodeDecodeError, LookupError):
            continue

    # 모든 인코딩이 실패했을 경우 예외 발생
    raise ValueError(
        '지원하는 인코딩(utf-8-sig, cp949, euc-kr)으로 파일을 읽을 수 없습니다.'
    )

#인코딩 자동 감지로 csv읽기
st.subheader('1) 인코딩 자동 감지')
df, used_encoding = read_csv_wih_auto_encoding(csv_path)
st.success(f'✅ 감지된 인코딩: **{used_encoding}**')

st.markdown('---')

# 객실등급(Pclass) 별 생존율 집계
# Survived 사망 0 / 생존 1 -> 등급별 평균을 내면 그대로가 등급의 생존비율이 된다.
# 10명 남3 여7
# 전체인원 1000, 생존300 => 300/1000=30%

pclass_survival_rate = df.groupby('Pclass')['Survived'].mean().sort_index()
#mean().sort_index() : ???
st.dataframe((pclass_survival_rate * 100).round(1).rename('생존율(%)'))
# round : 반올림

st.markdown('---')

# 차트 그리기 & 글꼴 지정
st.subheader('3) 객실등급별 생존율 막대그래프')
try:
    font_prop = font_manager.FontProperties(fname=font_path)
    # matplotlib font_manager에 폰트를 등록하고, 전역 폰트로 설정
    font_manager.fontManager.addfont(font_path)
    font_name = font_prop.get_name()
    plt.rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False
    ## 마이너스(-) 부호 깨짐 방지
    st.write('내 글꼴은 온글잎 콘콘체 폰트를 적용했습니다.')
    # 폰트 파일이 없으면 FileNotFoundError
except FileNotFoundError:
    st.warning('폰트 파일을 찾을 수가 없습니다.')

fig, ax = plt.subplots(figsize=(8,5))
(pclass_survival_rate * 100).plot(kind='bar',color='#D9E5FF')
# 16진수 컬러테이블에서 확인 후 컬러 선택
ax.set_title('객실 등급별 생존율')
ax.set_xlabel('객실등급(Pclass)')
ax.set_ylabel('생존율(%)')

st.pyplot(fig)

output_png = os.path.join(os.path.dirname(__file__),'chart.png')
fig.savefig(output_png)

#제미나이 -> '메플로이에서 쓸 수 있는 차트 종류 알려줘' 로 질문