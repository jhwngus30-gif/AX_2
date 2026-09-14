# RAG : 검색 증강 생성(RAG, Retrieval-Augmented Generation)은 대규모 언어 모델(LLM)이 응답을 생성하기 전 외부 데이터베이스나 문서에서 관련 정보를 먼저 검색하고, 
# 이를 바탕으로 정확한 답변을 만들도록 지원하는 AI 프레임워크입니다.
# 랭체인(LangChain)과 랭그래프(LangGraph) : 거대 언어 모델(LLM) 기반 응용 프로그램을 만들기 위한 핵심 프레임워크이나, 
# 처리 방식과 구조적 철학에서 뚜렷한 차이가 있습니다. *랭체인-대화 기억

# 대화 기록을 기억하는 멀티턴 챗봇
# st.session_state에 대화 기록을 저장해서, 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 streamlit의 채팅 전용 위제을 사용합니다.
# stream=True 옵션으로 답변이 실시간으로 타이핑되듯 출력됩니다.
# 실행방법 : streamlit run 09-11_3.py

# 시스템 메시지를 사용자가 설정 하도록
# 대화 기록 초기화 버튼


import streamlit as st
from openai import OpenAI

st.set_page_config(page_title='나의 멀티턴 챗봇', page_icon='🤖')
st.title('🤖 멀티턴 AI 챗봇')
st.caption('스트리밍 답변과 실시간 토큰 사용량을 함께 확인하는 챗봇입니다.')

# ----------------- 사이드바 설정 -----------------
with st.sidebar:
    st.header('설정')
    api_key = st.text_input('OpenAI API Key', type='password', help='sk-로 시작하는 키를 입력하세요.')
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o'], index=0)
    
    st.divider()
    
    system_prompt = st.text_area(
        '시스템 메시지 (AI 역할 설정)',
        value="당신은 사용자를 '주인님'이라 부르며 항상 공손하고 친절하게 답변하는 AI 비서입니다. 모든 답변을 '주인님, '으로 시작하세요."
    )
    
    if st.button('대화 기록 초기화', use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- 대화 기록 초기화 및 렌더링 -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 렌더링 (저장된 토큰 메트릭이 있다면 함께 표시)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "usage" in msg:
            u = msg["usage"]
            st.caption(f"📊 프롬프트: {u['prompt']} | 완료: {u['completion']} | 총 토큰: {u['total']}")

# ----------------- 채팅 입력 및 스트리밍 처리 -----------------
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    if not api_key:
        st.info("먼저 사이드바에 OpenAI API Key를 입력해주세요.")
        st.stop()

    # 사용자 질문 화면 표시 및 세션 기록
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        client = OpenAI(api_key=api_key)

        api_messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            # 1. include_usage 옵션 활성화
            response_stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=True,
                stream_options={"include_usage": True}
            )

            # 토큰 정보를 담을 딕셔너리
            token_info = {}

            # 2. 텍스트를 실시간 양도(yield)하면서 마지막 usage를 낚아채는 제너레이터
            def generate_chunks():
                for chunk in response_stream:
                    # 텍스트 추출 및 화면 전송
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                    
                    # 스트림 마지막에 들어오는 usage 정보 포획
                    if chunk.usage:
                        token_info["prompt"] = chunk.usage.prompt_tokens
                        token_info["completion"] = chunk.usage.completion_tokens
                        token_info["total"] = chunk.usage.total_tokens

            # 스트리밍 출력
            response_text = st.write_stream(generate_chunks())

            # 3. 토큰 사용량 화면 표시
            if token_info:
                st.caption(f"📊 프롬프트: {token_info['prompt']} | 완료: {token_info['completion']} | 총 토큰: {token_info['total']}")

        # 4. 세션 기록에 텍스트와 토큰 정보 함께 저장
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "usage": token_info
        })

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")