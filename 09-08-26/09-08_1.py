# raw_trade_data.csv 파일 활용
# [HS코드가 85로 시작하는 (반도체류)
# + 국가명 : 미국 또는 베트남
# + 수출금액 0 보다 큰 수(실제 수출실적이 있는)]
# 다중 조건으로 필터링 한 뒤, 수출금액 상위 10건을 화면에 보여주고 report.csv 로 저장
#streamlit 사용

# -*- coding: utf-8 -*-

#dkdkdkdkdkdkd
#dkdkdk
#dd

import os
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="반도체 수출 실적 분석기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>📈 반도체(HS코드 85) 미국/베트남 수출 실적 분석 및 보고서</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>raw_trade_data.csv 파일을 분석하여 다중 조건 필터링 후, 수출금액 상위 10건의 리포트를 생성합니다.</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 지정해주신 절대 경로 반영 (Raw String r"..." 사용)
# ----------------------------------------------------
DATA_FILE = csv_path = os.path.join(os.path.dirname(__file__), "..", "csv_file", "raw_trade_data.csv")

# 저장될 리포트 경로 (동일한 폴더에 저장하려면 아래 주석 해제)
# REPORT_FILE = r"C:\Users\user\AX_2\csv_file\report.csv"
REPORT_FILE = "report.csv"

@st.cache_data
def load_data(file_path):
    """CSV 데이터를 로드합니다."""
    if not os.path.exists(file_path):
        return None
    try:
        # UTF-8 시도 후 실패 시 한글 인코딩(CP949/EUC-KR) 처리
        return pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="cp949")
    except Exception as e:
        st.error(f"데이터 파일 로드 중 오류 발생: {e}")
        return None

# Load data
df = load_data(DATA_FILE)

if df is not None:
    # ----------------------------------------------------
    # 데이터 필터링 수행
    # 1. HS코드가 85로 시작하는 품목
    # 2. 국가명이 미국 또는 베트남
    # 3. 수출금액 > 0
    # ----------------------------------------------------
    cond_hs = df['hs_code'].astype(str).str.strip().str.startswith('85')
    cond_country = df['국가명'].isin(['미국', '베트남'])
    cond_amount = pd.to_numeric(df['수출금액'], errors='coerce').fillna(0) > 0

    filtered_df = df[cond_hs & cond_country & cond_amount]
    top_10_df = filtered_df.sort_values(by='수출금액', ascending=False).head(10)

    # Sidebar - 필터 요약
    st.sidebar.header("🔍 분석 조건 정보")
    st.sidebar.markdown(f"""
    - **파일 경로**: `{DATA_FILE}`
    - **품목 카테고리**: 반도체류 (HS코드 85XX)
    - **대상 국가**: 미국 (USA), 베트남 (Vietnam)
    - **실적 조건**: 수출금액 > 0
    - **정렬 기준**: 수출금액 내림차순 (상위 10건)
    """)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 전체 데이터 요약")
    st.sidebar.write(f"- 전체 데이터 행 수: {len(df):,}개")
    st.sidebar.write(f"- 조건 필터링 통과 행 수: {len(filtered_df):,}개")

    if top_10_df.empty:
        st.warning("⚠️ 지정한 조건에 부합하는 데이터가 존재하지 않습니다.")
    else:
        # report.csv 저장
        try:
            top_10_df.to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')
            st.sidebar.success(f"💾 로컬 파일 저장 완료: `{REPORT_FILE}`")
        except Exception as e:
            st.sidebar.error(f"⚠️ report.csv 저장 오류: {e}")

        # ----------------------------------------------------
        # KPI 메트릭 섹션
        # ----------------------------------------------------
        st.subheader("📊 주요 실적 지표 (상위 10건 기준)")
        col1, col2, col3 = st.columns(3)
        col1.metric("💵 총 수출 금액", f"${top_10_df['수출금액'].sum():,.0f}")
        col2.metric("📈 평균 수출 금액", f"${top_10_df['수출금액'].mean():,.0f}")
        col3.metric("🏆 최대 단일 수출액", f"${top_10_df['수출금액'].max():,.0f}")

        st.markdown("---")

        # ----------------------------------------------------
        # 데이터프레임 표시 섹션
        # ----------------------------------------------------
        st.subheader("📋 수출금액 상위 10건 리스트")
        st.dataframe(
            top_10_df,
            column_config={
                "날짜": st.column_config.TextColumn("수출 날짜"),
                "hs_code": st.column_config.TextColumn("HS 코드"),
                "품목명": st.column_config.TextColumn("품목명"),
                "국가명": st.column_config.TextColumn("수출 대상국"),
                "수출금액": st.column_config.NumberColumn("수출금액 ($)", format="$%,d"),
                "중량": st.column_config.NumberColumn("중량 (kg)", format="%,.2f")
            },
            hide_index=True,
            use_container_width=True
        )

        # 다운로드 버튼
        csv_data = top_10_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 보고서 다운로드 (report.csv)",
            data=csv_data,
            file_name="report.csv",
            mime="text/csv"
        )

        st.markdown("---")

        # ----------------------------------------------------
        # 시각화 차트 섹션
        # ----------------------------------------------------
        st.subheader("📊 시각화 분석")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### 🌍 국가별 상위 10건 수출금액 합계")
            country_chart_df = top_10_df.groupby('국가명', as_index=False)['수출금액'].sum()
            st.bar_chart(
                data=country_chart_df,
                x='국가명',
                y='수출금액',
                use_container_width=True
            )

        with chart_col2:
            st.markdown("#### 📅 시계열 수출금액 추이 (상위 10건)")
            time_chart_df = top_10_df.sort_values(by='날짜')
            st.line_chart(
                data=time_chart_df,
                x='날짜',
                y='수출금액',
                color='국가명',
                use_container_width=True
            )
else:
    st.error(f"❌ 데이터 파일을 찾을 수 없습니다:\n`{DATA_FILE}`")
    st.info("파일 경로와 파일명에 오탈자가 없는지, 해당 위치에 파일이 실제로 존재하는지 다시 한번 확인해 주세요.")

