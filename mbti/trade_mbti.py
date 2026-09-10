import base64
import math
import os
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. Page Configuration (반응형 와이드 레이아웃 적용)
# -------------------------------------------------------------
st.set_page_config(
    page_title="무역 직무 MBTI 진단 테스트",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# 2. Local Font Loader & 하이브리드 반응형 CSS
# -------------------------------------------------------------
def get_custom_font_css():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_extensions = [".ttf", ".otf", ".woff", ".woff2"]
    
    font_path = None
    font_format = "truetype"

    try:
        for fname in os.listdir(current_dir):
            ext = os.path.splitext(fname)[1].lower()
            if ext in font_extensions:
                font_path = os.path.join(current_dir, fname)
                if ext == ".otf":
                    font_format = "opentype"
                elif ext == ".woff":
                    font_format = "woff"
                elif ext == ".woff2":
                    font_format = "woff2"
                else:
                    font_format = "truetype"
                break

        if font_path and os.path.exists(font_path):
            with open(font_path, "rb") as f:
                font_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            font_face = f"""
            @font-face {{
                font-family: 'CustomTradeFont';
                src: url('data:font/{font_format};charset=utf-8;base64,{font_b64}') format('{font_format}');
                font-weight: normal;
                font-style: normal;
            }}
            """
            font_family_rule = "'CustomTradeFont', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
        else:
            font_face = ""
            font_family_rule = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    except Exception:
        font_face = ""
        font_family_rule = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

    return f"""
    <style>
        {font_face}

        :root {{
            --primary: #8A79D6;
            --primary-dark: #6E5BB8;
            --bg-color: #F9F8FD;
            --card-bg: #FFFFFF;
            --accent-tint: #F1EFFF;
            --text-primary: #2D283E;
            --text-muted: #6E6A7C;
            --border-color: #E5E0F8;
            --app-font: {font_family_rule};
        }}

        html, body, [class*="css"], .stApp, p, h1, h2, h3, h4, h5, h6, span, div, label, button, input {{
            font-family: var(--app-font) !important;
        }}

        body, .stApp {{
            background-color: var(--bg-color);
            color: var(--text-primary);
        }}

        /* 전체 중앙 컨테이너 크기 */
        .block-container {{
            max-width: 1020px !important;
            padding-top: 1.8rem !important;
            padding-bottom: 3.5rem !important;
            margin: 0 auto !important;
        }}

        .main-header {{
            text-align: center;
            padding: 1.2rem 0.5rem 1.4rem;
        }}
        .main-header h1 {{
            color: var(--primary-dark);
            font-weight: 800;
            font-size: 2.1rem;
            margin-bottom: 0.4rem;
        }}
        .main-header p {{
            color: var(--text-muted);
            font-size: 1.05rem;
        }}

        .trade-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 16px rgba(138, 121, 214, 0.08);
            margin-bottom: 20px;
        }}

        .hero-card {{
            background: linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 100%);
            border: 2px solid #8A79D6;
            border-radius: 18px;
            padding: 28px;
            box-shadow: 0 8px 24px rgba(138, 121, 214, 0.16);
            margin-bottom: 24px;
        }}

        .rank-badge {{
            display: inline-block;
            background-color: var(--primary);
            color: #FFFFFF;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .hero-title {{
            color: var(--primary-dark);
            font-size: 1.7rem;
            font-weight: 800;
            margin: 6px 0 10px;
        }}

        .hashtag {{
            display: inline-block;
            background-color: #EBE6FA;
            color: var(--primary-dark);
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 4px;
        }}

        .match-box {{
            border-radius: 14px;
            padding: 18px;
            height: 100%;
        }}
        .match-best {{
            background-color: #F3EFFE;
            border-left: 4px solid #8A79D6;
        }}
        .match-warn {{
            background-color: #FFF6F3;
            border-left: 4px solid #FF8C70;
        }}

        /* -----------------------------------------------------------
           💻 데스크톱 / 노트북 환경 (화면 폭 641px 이상)
        ----------------------------------------------------------- */
        @media (min-width: 641px) {{
            div[role="radiogroup"] {{
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                justify-content: space-between !important;
                gap: 10px !important;
                width: 100% !important;
                margin-top: 8px !important;
                margin-bottom: 18px !important;
            }}

            div[role="radiogroup"] > label {{
                flex: 1 1 0px !important;
                width: 100% !important;
                min-width: 0 !important;
                background-color: #FFFFFF !important;
                padding: 12px 6px !important;
                border-radius: 12px !important;
                border: 1.5px solid #E5E0F8 !important;
                margin: 0 !important;
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                box-sizing: border-box !important;
                transition: all 0.2s ease !important;
            }}

            div[role="radiogroup"] > label:hover {{
                border-color: #8A79D6 !important;
                background-color: #F6F4FF !important;
                transform: translateY(-1px) !important;
            }}

            div[role="radiogroup"] > label > div:first-child {{
                margin-right: 6px !important;
                flex-shrink: 0 !important;
            }}

            div[role="radiogroup"] > label p {{
                font-size: 0.88rem !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                margin: 0 !important;
                color: #2D283E !important;
                font-weight: 600 !important;
            }}

            /* 노트북에서는 보조 설명이 선택지 자체에 있으므로 가이드 바 숨김 */
            .scale-guide {{
                display: none !important;
            }}
        }}

        /* -----------------------------------------------------------
           📱 스마트폰 / 모바일 환경 (화면 폭 640px 이하)
        ----------------------------------------------------------- */
        @media (max-width: 640px) {{
            .block-container {{
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }}

            div[role="radiogroup"] {{
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                justify-content: space-between !important;
                gap: 6px !important;
                width: 100% !important;
                margin-top: 6px !important;
                margin-bottom: 4px !important;
            }}

            div[role="radiogroup"] > label {{
                flex: 1 1 0px !important;
                width: 100% !important;
                min-width: 0 !important;
                background-color: #FFFFFF !important;
                padding: 13px 0 !important;
                border-radius: 10px !important;
                border: 1.5px solid #E5E0F8 !important;
                margin: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                transition: all 0.15s ease !important;
            }}

            /* 모바일에서는 동그라미 아이콘을 숨기고 깔끔한 숫자 터치 카드로 렌더링 */
            div[role="radiogroup"] > label > div:first-child {{
                display: none !important;
            }}

            /* 박스 안의 텍스트 중 긴 설명 괄호 부분은 숨겨서 깨짐 방지 */
            div[role="radiogroup"] > label p {{
                font-size: 1.15rem !important;
                font-weight: 800 !important;
                color: var(--primary-dark) !important;
                margin: 0 !important;
            }}

            /* 터치 시 색상 반전 */
            div[role="radiogroup"] > label:has(input:checked) {{
                background-color: var(--primary) !important;
                border-color: var(--primary) !important;
            }}
            div[role="radiogroup"] > label:has(input:checked) p {{
                color: #FFFFFF !important;
            }}

            /* 모바일에서만 노출되는 직관적인 좌우 가이드 */
            .scale-guide {{
                display: flex !important;
                justify-content: space-between !important;
                font-size: 0.78rem !important;
                color: #8C879B !important;
                font-weight: 600 !important;
                padding: 4px 6px 20px !important;
            }}
        }}

        .stButton>button {{
            background-color: var(--primary) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            box-shadow: 0 4px 14px rgba(138, 121, 214, 0.25) !important;
            transition: all 0.2s ease;
        }}
    </style>
    """

st.markdown(get_custom_font_css(), unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. Data Definition
# -------------------------------------------------------------
QUESTIONS = [
    {"id": 1, "axis": "R", "part": "Part 1. 대인 지향 vs 데이터 지향", "text": "해외 바이어나 파트너와 직접 대화하고 관계를 맺는 일에서 큰 에너지를 얻는다."},
    {"id": 2, "axis": "R", "part": "Part 1. 대인 지향 vs 데이터 지향", "text": "무역 박람회에서 처음 보는 참관객에게 먼저 다가가 제품을 소개하는 것이 즐겁다."},
    {"id": 3, "axis": "R", "part": "Part 1. 대인 지향 vs 데이터 지향", "text": "상대를 설득할 때 수치 데이터보다 인간적인 유대감과 스토리텔링이 더 강력하다고 믿는다."},
    {"id": 4, "axis": "R", "part": "Part 1. 대인 지향 vs 데이터 지향", "text": "하루 종일 사람과의 소통 없이 서류나 엑셀 작업만 하면 쉽게 피로해진다."},
    {"id": 5, "axis": "R", "part": "Part 1. 대인 지향 vs 데이터 지향", "text": "파트너십에서 계약서의 세부 문구 검토보다 상호 신뢰 형성을 위한 미팅이 더 중요하다."},

    {"id": 6, "axis": "D", "part": "Part 2. 도전 돌파 vs 안정 관리", "text": "안정된 기존 거래선을 유지하는 것보다 미개척 신흥 시장을 개척하는 것이 더 매력적이다."},
    {"id": 7, "axis": "D", "part": "Part 2. 도전 돌파 vs 안정 관리", "text": "조건이 까다롭고 납기가 촉박하더라도 매출 규모가 크다면 일단 수주를 추진하고 본다."},
    {"id": 8, "axis": "D", "part": "Part 2. 도전 돌파 vs 안정 관리", "text": "리스크를 감수하더라도 경쟁사를 제치고 대형 거래를 성사시킬 때 가장 보람을 느낀다."},
    {"id": 9, "axis": "D", "part": "Part 2. 도전 돌파 vs 안정 관리", "text": "단가를 크게 낮출 수 있다면 약간의 품질·납기 리스크는 감수하고 시도해 볼 가치가 있다."},
    {"id": 10, "axis": "D", "part": "Part 2. 도전 돌파 vs 안정 관리", "text": "안전한 무사고 관리보다 다소 마찰이 있더라도 공격적인 거래 성사를 선호한다."},

    {"id": 11, "axis": "F", "part": "Part 3. 유연 순발력 vs 치밀 원칙", "text": "선적 지연이나 포트 혼잡 등 돌발 상황이 터졌을 때 즉각적인 순발력으로 대안을 찾아내는 편이다."},
    {"id": 12, "axis": "F", "part": "Part 3. 유연 순발력 vs 치밀 원칙", "text": "정해진 타임라인과 체크리스트에 얽매이기보다 상황 변화에 따라 유연하게 일정을 바꾼다."},
    {"id": 13, "axis": "F", "part": "Part 3. 유연 순발력 vs 치밀 원칙", "text": "서류의 사소한 오탈자나 디테일 검증보다는 전체 거래의 흐름을 신속히 빼는 것이 더 중요하다."},
    {"id": 14, "axis": "F", "part": "Part 3. 유연 순발력 vs 치밀 원칙", "text": "바이어의 갑작스러운 스펙 변경 요구에도 매뉴얼에 얽매이지 않고 임기응변으로 조율해 낸다."},
    {"id": 15, "axis": "F", "part": "Part 3. 유연 순발력 vs 치밀 원칙", "text": "공식적인 가이드라인이 모호하더라도 내 직관과 현장 판단을 믿고 빠르게 결정을 내린다."},

    {"id": 16, "axis": "G", "part": "Part 4. 글로벌 현장 vs 오피스 시스템", "text": "잦은 해외 출장이나 시차 적응의 피로가 있어도 현지 시장을 직접 누비는 출장을 선호한다."},
    {"id": 17, "axis": "G", "part": "Part 4. 글로벌 현장 vs 오피스 시스템", "text": "완벽한 서면 기록보다 다소 거칠더라도 통화나 메신저로 실시간 부딪히며 소통하는 게 편하다."},
    {"id": 18, "axis": "G", "part": "Part 4. 글로벌 현장 vs 오피스 시스템", "text": "본사 SCM 시스템 고도화보다 해외 법인 주재원이나 현지 지사 파견 근무를 지망한다."},
    {"id": 19, "axis": "G", "part": "Part 4. 글로벌 현장 vs 오피스 시스템", "text": "깔끔하게 정돈된 오피스 데스크보다 물류 창고, 선적 포트, 전시회 같은 현장감이 더 활기차다."},
    {"id": 20, "axis": "G", "part": "Part 4. 글로벌 현장 vs 오피스 시스템", "text": "환율 변동이나 규제 개정 데이터 분석보다 현지 소비자·바이어의 체감 반응 관찰에 먼저 눈이 간다."},
]

JOB_PROFILES = {
    "해외영업": {
        "en": "Overseas Sales",
        "vector": [8, 7, 6, 9],
        "character": "불가능을 가능케 하는 글로벌 개척자",
        "description": "탁월한 글로벌 대인 소통 능력과 강한 추진력으로 해외 신시장을 개척하고 수주를 이끌어내는 프런티어입니다.",
        "tags": ["#바이어_밀당의_신", "#해외전시회_주인공", "#네고_장인", "#글로벌_개척자"],
        "partner_best": ("무역영업관리", "내가 공격적으로 따온 계약을 오차 없는 서류와 일정 관리로 든든하게 받쳐줍니다."),
        "partner_warn": ("수출입 통관 / 관세", "속도감과 예외 조율을 중시하는 나와 원칙주의 관세 규정이 부딪힐 수 있어 사전 확인이 필수입니다."),
        "cert": "국제무역사 1급, 무역영어 1급, 토익스피킹/OPIc (AL 이상)",
        "skills": "해외 시장조사, 바이어 리드 발굴, Incoterms 조건 협상, 영문 이메일/PT",
    },
    "무역영업관리": {
        "en": "Trade Operation",
        "vector": [-8, -8, -9, -8],
        "character": "1원, 1초의 오차도 허용 않는 오피스 관제탑",
        "description": "치밀한 데이터 분석력과 체계적인 관리로 L/C 개설부터 선적 서류, 수금까지 전 과정을 완벽히 통제하는 오퍼레이션의 핵심입니다.",
        "tags": ["#엑셀_마스터", "#인코텀즈_정석", "#오차율0%", "#오피스_관제탑"],
        "partner_best": ("해외영업", "열정적인 영업팀이 벌려놓은 거래를 체계적인 프로세스로 안정화시켜 주는 완벽한 파트너입니다."),
        "partner_warn": ("포워딩 / 국제물류", "급변하는 운송 변수 속에서 서류 수정 요구가잦아 소통 피로도가 발생할 수 있습니다."),
        "cert": "국제무역사 1급, 외환전문역, 무역영어, 컴퓨터활용능력 1급",
        "skills": "ERP(SAP) 수주 등록, L/C 네고 및 신용장 검토, B/L 대조, 무역 정산",
    },
    "포워딩 / 국제물류": {
        "en": "Forwarding & Logistics",
        "vector": [2, 6, 9, 3],
        "character": "꼬인 운송 라인도 풀어내는 실시간 해결사",
        "description": "글로벌 공급망에서 발생하는 포트 혼잡, 선적 지연 등 돌발 변수를 특유의 순발력과 네트워크로 돌파하는 물류 조율사입니다.",
        "tags": ["#위기_탈출_넘버원", "#부킹_마법사", "#실시간_해결사", "#물류_네트워크"],
        "partner_best": ("수출입 통관 / 관세", "화물의 국경 이동 시 신속한 통관 프로세스를 맞춰주는 필수불가결한 동반자입니다."),
        "partner_warn": ("무역영업관리", "선박 지연과 서류 변경 등 불가피한 변수로 인해 일정 조율 시 긴밀한 양해가 필요합니다."),
        "cert": "물류관리사, 유통관리사, 국제무역사",
        "skills": "선사/항공사 운임 부킹, 모달 시프트(해상/항공 연계), 복합운송 B/L 발행",
    },
    "수출입 통관 / 관세": {
        "en": "Customs & Trade Compliance",
        "vector": [-9, -9, -10, -7],
        "character": "법률과 규정으로 회사를 지키는 무역 수호자",
        "description": "복잡한 관세법, HS Code 분류, FTA 원산지 규정을 철저히 준수하여 통관 보류와 관세 리스크를 차단하는 원칙주의 전문가입니다.",
        "tags": ["#HS코드_백과사전", "#FTA_마스터", "#원칙주의자", "#무역_수호자"],
        "partner_best": ("글로벌 소싱 / 구매", "해외 원자재 및 완제품 도입 시 관세 절감(FTA 특혜세율) 최적안을 도출해 줍니다."),
        "partner_warn": ("해외영업", "영업팀의 급박한 수출 일정 속에서 원산지 증빙 및 필수 검역 절차를 타협 없이 관철해야 합니다."),
        "cert": "원산지관리사, 보세사, 관세사 (1차/전문직)",
        "skills": "품목분류(HS Code), FTA 원산지결정기준(PSR) 판정, 요건승인 및 검역 관리",
    },
    "글로벌 소싱 / 구매": {
        "en": "Global Sourcing & Procurement",
        "vector": [-4, 6, -6, 7],
        "character": "최적의 단가와 공급망을 발굴하는 네고 헌터",
        "description": "국내외 경쟁력 있는 제조 공장과 원자재 공급선을 발굴하고 치밀한 원가 분석으로 최상의 구매 조건을 만들어내는 협상가입니다.",
        "tags": ["#원가_절감_헌터", "#공급망_탐험가", "#단가_네고_달인", "#스마트_소싱"],
        "partner_best": ("수출입 통관 / 관세", "해외 직수입 시 발생할 수 있는 덤핑방지관세나 수입 요건을 사전에 함께 점검합니다."),
        "partner_warn": ("크로스보더 e-커머스", "마케팅팀의 빠른 트렌드 전환 속도와 MOQ(최소주문수량)/리드타임의 현실 사이 조율이 필요합니다."),
        "cert": "CPIM(공급망관리사), 물류관리사, 무역영어",
        "skills": "해외 공급업체 감사(Audit), 단가 원가분석(Cost Breakdown), OEM/ODM 계약",
    },
    "크로스보더 e-커머스 / 해외마케팅": {
        "en": "Cross-Border E-Commerce",
        "vector": [6, 8, 5, -6],
        "character": "트렌드를 읽고 글로벌 장바구니를 채우는 전략가",
        "description": "아마존, 쇼피, 틱톡샵 등 글로벌 e커머스 플랫폼에서 현지 소비자 데이터를 분석하고 최적의 디지털 마케팅으로 매출을 극대화합니다.",
        "tags": ["#글로벌_장바구니_털이", "#아마존_셀러", "#데이터_마케터", "#트렌드_세터"],
        "partner_best": ("해외영업", "온라인 e커머스와 오프라인 B2B 유통 채널 간의 글로벌 브랜드 인지도를 동반 성장시킵니다."),
        "partner_warn": ("글로벌 소싱 / 구매", "인기 품목의 급격한 품절과 공급망 리드타임 병목을 극복하기 위해 긴밀한 재고 협업이 요구됩니다."),
        "cert": "검색광고마케터, Google Analytics(GA4), 전자상거래관리사",
        "skills": "글로벌 마켓플레이스 운영(Shopee/Amazon), ROAS 광고 최적화, 풀필먼트(FBA) 관리",
    },
}

# 기본 라벨 (노트북에서는 풀 라벨로 보이고, 모바일에서는 CSS가 숫자만 집중 표기)
SCALE_OPTIONS = {
    1: "1점 (전혀 아니다)",
    2: "2점 (대체로 아니다)",
    3: "3점 (보통이다)",
    4: "4점 (대체로 그렇다)",
    5: "5점 (매우 그렇다)",
}

# -------------------------------------------------------------
# 4. Helper Functions
# -------------------------------------------------------------
def calculate_user_vector(answers):
    scores = {"R": 0, "D": 0, "F": 0, "G": 0}
    for q in QUESTIONS:
        user_val = answers.get(q["id"], 3)
        scores[q["axis"]] += (user_val - 3)
    return [scores["R"], scores["D"], scores["F"], scores["G"]]

def calculate_fit(user_vec, target_vec):
    dist = math.sqrt(sum((u - t) ** 2 for u, t in zip(user_vec, target_vec)))
    d_max = 40.0
    fit = max(0.0, (1.0 - (dist / d_max)) * 100.0)
    return round(fit, 1)

def create_radar_chart(user_vec):
    categories = ["관계 지향 (R)", "도전 돌파 (D)", "유연 순발력 (F)", "글로벌 현장 (G)"]
    r_values = [((v + 10) / 20.0) * 100.0 for v in user_vec]
    r_values.append(r_values[0])
    cats = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=cats,
        fill="toself",
        name="내 성향 점수",
        line=dict(color="#8A79D6", width=2.5),
        fillcolor="rgba(138, 121, 214, 0.35)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                linecolor="#E5E0F8",
                gridcolor="#EBE6FA",
            ),
            angularaxis=dict(
                linecolor="#E5E0F8",
                gridcolor="#EBE6FA",
                tickfont=dict(size=12, color="#2D283E"),
            ),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
        showlegend=False,
        margin=dict(l=35, r=35, t=25, b=25),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# -------------------------------------------------------------
# 5. Session State
# -------------------------------------------------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "final_answers" not in st.session_state:
    st.session_state.final_answers = {q["id"]: 3 for q in QUESTIONS}

# -------------------------------------------------------------
# 6. UI Rendering
# -------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🌐 무역 직무 MBTI 진단 테스트</h1>
    <p>글로벌 무역 실무에서 나의 잠재력과 성향이 가장 빛나는 직무를 찾아보세요!</p>
</div>
""", unsafe_allow_html=True)

# ----------------- RESULT VIEW -----------------
if st.session_state.submitted:
    user_vec = calculate_user_vector(st.session_state.final_answers)

    rankings = []
    for job_name, info in JOB_PROFILES.items():
        fit_score = calculate_fit(user_vec, info["vector"])
        rankings.append((job_name, fit_score, info))
    rankings.sort(key=lambda x: x[1], reverse=True)

    top_job_name, top_fit, top_info = rankings[0]

    tags_html = " ".join([f'<span class="hashtag">{t}</span>' for t in top_info["tags"]])
    st.markdown(f"""
    <div class="hero-card">
        <span class="rank-badge">🏆 BEST MATCH · 적합도 {top_fit}%</span>
        <div class="hero-title">{top_job_name} ({top_info['en']})</div>
        <p style="font-size:1.15rem; font-weight:700; color:#4B3F8A; margin-bottom: 8px;">
            "{top_info['character']}"
        </p>
        <p style="color:#555066; line-height:1.65; margin-bottom:12px;">
            {top_info['description']}
        </p>
        <div class="tag-container">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="trade-card" style="height:100%;">
            <h3 style="font-size:1.15rem; color:#2D283E; margin-bottom:12px;">📊 나의 4대 업무 성향 밸런스</h3>
        """, unsafe_allow_html=True)
        fig = create_radar_chart(user_vec)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
            <div style="font-size:0.85rem; color:#6E6A7C; text-align:center;">
                관계({user_vec[0]:+d}) · 도전({user_vec[1]:+d}) · 유연({user_vec[2]:+d}) · 현장({user_vec[3]:+d})
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="trade-card" style="height:100%;">
            <h3 style="font-size:1.15rem; color:#2D283E; margin-bottom:16px;">🏆 6대 무역 직무 적합도 랭킹</h3>
        """, unsafe_allow_html=True)
        for i, (j_name, j_fit, _) in enumerate(rankings):
            c_left, c_right = st.columns([3, 1])
            with c_left:
                st.markdown(f"**{i+1}. {j_name}**")
            with c_right:
                st.markdown(f"<span style='color:#6E5BB8; font-weight:700;'>{j_fit}%</span>", unsafe_allow_html=True)
            st.progress(j_fit / 100.0)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h3 style='color:#2D283E; margin: 24px 0 14px;'>🤝 직무 케미스트리 (협업 궁합)</h3>", unsafe_allow_html=True)
    chem_col1, chem_col2 = st.columns(2)

    with chem_col1:
        st.markdown(f"""
        <div class="match-box match-best">
            <h4 style="color:#6E5BB8; margin-top:0; margin-bottom:6px;">💜 환상의 짝꿍: {top_info['partner_best'][0]}</h4>
            <p style="color:#4B3F8A; font-size:0.92rem; line-height:1.55; margin:0;">
                {top_info['partner_best'][1]}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with chem_col2:
        st.markdown(f"""
        <div class="match-box match-warn">
            <h4 style="color:#E05638; margin-top:0; margin-bottom:6px;">⚠️ 조율이 필요한 파트너: {top_info['partner_warn'][0]}</h4>
            <p style="color:#7A4336; font-size:0.92rem; line-height:1.55; margin:0;">
                {top_info['partner_warn'][1]}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="trade-card" style="margin-top: 24px;">
        <h3 style="font-size:1.15rem; color:#2D283E; margin-bottom:14px;">🎓 {top_job_name} 커리어 치트키</h3>
        <p style="margin-bottom:8px;">
            <b>📜 추천 자격증:</b> <span style="color:#6E5BB8; font-weight:600;">{top_info['cert']}</span>
        </p>
        <p style="margin-bottom:8px;">
            <b>🛠️ 필수 실무 스킬:</b> {top_info['skills']}
        </p>
        <p style="margin-bottom:0; color:#6E6A7C; font-size:0.92rem; line-height:1.6;">
            💡 <b>실무 팁:</b> 직무 적합도 점수가 높더라도 실무에서는 상반된 성향의 타 부서와 끊임없이 소통하게 됩니다. 상대 직무의 핵심 관심사(리스크 vs 속도)를 먼저 파악하는 것이 프로 무역인의 핵심 역량입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    share_text = f"[무역 직무 MBTI 진단 결과]\\n대표 직무: {top_job_name} ({top_info['character']})\\n적합도: {top_fit}%\\n환상의 짝꿍: {top_info['partner_best'][0]}\\n너도 어떤 무역 직무가 맞는지 테스트해 봐! 🌐"

    st.markdown("<h3 style='color:#2D283E; margin: 28px 0 14px; text-align: center;'>💌 친구에게 내 결과 자랑하기</h3>", unsafe_allow_html=True)

    share_component_html = f"""
    <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 12px;">
        <button id="shareBtn" style="
            background: linear-gradient(135deg, #8A79D6 0%, #6E5BB8 100%);
            color: #FFFFFF;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(138, 121, 214, 0.3);
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: inherit;
        ">
            🔗 결과 복사 및 공유하기
        </button>
    </div>
    <div id="toastMsg" style="
        display: none;
        text-align: center;
        color: #6E5BB8;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 6px;
    ">
        ✨ 결과 내용이 클립보드에 복사되었습니다! 카톡이나 SNS에 붙여넣어 공유하세요.
    </div>

    <script>
        const shareData = {{
            title: '무역 직무 MBTI 결과',
            text: "{share_text}",
            url: window.location.href
        }};

        const btn = document.getElementById('shareBtn');
        const toast = document.getElementById('toastMsg');

        btn.addEventListener('click', async () => {{
            if (navigator.share) {{
                try {{
                    await navigator.share(shareData);
                }} catch (err) {{
                    copyFallback();
                }}
            }} else {{
                copyFallback();
            }}
        }});

        function copyFallback() {{
            const textToCopy = "{share_text}\\n테스트 링크: " + window.location.href;
            navigator.clipboard.writeText(textToCopy).then(() => {{
                toast.style.display = 'block';
                setTimeout(() => {{
                    toast.style.display = 'none';
                }}, 3500);
            }}).catch(() => {{
                alert('복사에 실패했습니다. 브라우저 권한을 확인해주세요.');
            }});
        }}
    </script>
    """
    components.html(share_component_html, height=90)

    st.markdown("<div style='text-align: center; margin-top: 10px;'>", unsafe_allow_html=True)
    if st.button("🔄 테스트 다시 하기", use_container_width=True):
        st.session_state.submitted = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- QUESTIONNAIRE VIEW -----------------
else:
    st.markdown("""
    <div style="background-color:#FFFFFF; border: 1px solid #E5E0F8; border-radius:14px; padding:16px 20px; margin-bottom:24px; color:#555066; font-size:0.95rem;">
        📝 <b>진단 안내</b>: 총 20개 문항입니다. 각 문항을 읽고 나의 실제 성향이나 업무 방식에 가장 가까운 척도(1~5점)를 선택해 주세요.
    </div>
    """, unsafe_allow_html=True)

    with st.form("trade_mbti_form"):
        form_answers = {}
        current_part = None
        for q in QUESTIONS:
            if q["part"] != current_part:
                current_part = q["part"]
                st.markdown(f"""
                <div style="margin-top:28px; margin-bottom:14px; padding-bottom:6px; border-bottom: 2px solid #E5E0F8;">
                    <h3 style="font-size:1.2rem; color:#6E5BB8; margin:0;">{current_part}</h3>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"<p style='font-size: 1.05rem; font-weight: 700; margin-bottom: 8px; line-height: 1.45;'>Q{q['id']:02d}. {q['text']}</p>", unsafe_allow_html=True)
            
            val = st.radio(
                label=f"Q{q['id']}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: SCALE_OPTIONS[x],
                index=2,  # 기본값 3점
                horizontal=True,
                key=f"q_{q['id']}",
                label_visibility="collapsed",
            )
            form_answers[q["id"]] = val
            
            # 모바일 환경에서만 노출되는 직관적 3구간 가이드
            st.markdown("""
            <div class="scale-guide">
                <span>◀ 전혀 아니다</span>
                <span>보통이다</span>
                <span>매우 그렇다 ▶</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='text-align: center; margin-top: 32px;'>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("✨ 나의 무역 MBTI 결과 확인하기", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submit_btn:
            st.session_state.final_answers = form_answers
            st.session_state.submitted = True
            st.rerun()