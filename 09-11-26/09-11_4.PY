# 파일 업로드 박스를 만들고
# 파일을 읽었으면 업로드한 문서미리보기 부분을 만들어줘 (원문(앞부분))
# 밑에 요약하기 버튼 추가
# 파일 없으면 error로  파일 업로드하세요.
# 왼쪽 사이드바에 요약 옵션 추가(짧게(3줄),보통(5~7줄),자세히)
# 요약스타일(전문가적인 말투, 날카로운 말투, 초등학생)을 셀렉박스 형태로

import streamlit as st
from openai import OpenAI

# ----------------- 페이지 설정 및 제목 -----------------
st.set_page_config(page_title='파일 업로드 문서 요약 앱', page_icon='📄')
st.title('예제3) 파일 업로드 문서 요약 앱')
st.caption('텍스트파일을 업로드 하면 OpenAI API가 원하는 스타일로 요약해줍니다.')

# ----------------- 사이드바 설정 -----------------
with st.sidebar:
    st.header('설정 및 요약 옵션')
    
    # API 키 및 모델 선택
    api_key = st.text_input('OpenAI API Key', type='password', help='sk-로 시작하는 키를 입력하세요.')
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o'], index=0)
    
    st.divider()
    
    # 요약 옵션 설정 (길이 및 스타일)
    length_option = st.selectbox(
        '요약 길이 선택',
        ['짧게(3줄)', '보통(5~7줄)', '자세히'],
        index=0
    )
    
    style_option = st.selectbox(
        '요약 스타일 선택',
        ['전문가적인 말투', '날카로운 말투', '초등학생'],
        index=0
    )

# ----------------- 파일 업로드 및 미리보기 -----------------
uploaded_file = st.file_uploader(
    "요약할 텍스트 파일(.txt)을 업로드하세요.",
    type=["txt"]
)

file_text = ""

if uploaded_file is not None:
    try:
        # 파일 내용 읽기 (UTF-8 인코딩 처리)
        file_text = uploaded_file.read().decode("utf-8")
        
        # 원문 미리보기 (앞 500자)
        st.subheader("📄 업로드한 문서 미리보기 (원문 앞부분)")
        preview_text = file_text[:500] + ("..." if len(file_text) > 500 else "")
        st.text_area("문서 미리보기", preview_text, height=180, disabled=True)
        
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

# ----------------- 요약하기 버튼 및 실행 로직 -----------------
if st.button("요약하기", type="primary", use_container_width=True):
    # 1. 파일 업로드 여부 검증
    if uploaded_file is None or not file_text.strip():
        st.error("파일을 업로드하세요.")
        st.stop()
    
    # 2. API Key 입력 여부 검증
    if not api_key:
        st.warning("사이드바에 OpenAI API Key를 입력해주세요.")
        st.stop()
        
    # 요약 프롬프트 구성
    system_prompt = (
        f"당신은 전문 문서 요약가입니다. 다음 요구사항을 반드시 준수하여 문서를 요약하세요:\n"
        f"1. 분량: {length_option}\n"
        f"2. 어조 및 스타일: {style_option} 스타일로 작성할 것."
    )
    
    user_prompt = f"다음 문서를 주어진 조건에 맞게 요약해주세요:\n\n{file_text}"
    
    try:
        client = OpenAI(api_key=api_key)
        
        with st.chat_message("assistant"):
            st.markdown("### 📋 요약 결과")
            
            # 스트리밍 및 토큰 정보 가져오기
            response_stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
                stream_options={"include_usage": True}
            )
            
            token_info = {}
            
            def generate_chunks():
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                    
                    # 스트림 마지막에 들어오는 usage 정보 포획
                    if chunk.usage:
                        token_info["prompt"] = chunk.usage.prompt_tokens
                        token_info["completion"] = chunk.usage.completion_tokens
                        token_info["total"] = chunk.usage.total_tokens

            # 실시간 스트리밍 출력
            st.write_stream(generate_chunks())
            
            # 토큰 사용량 메트릭 출력
            if token_info:
                st.caption(f"📊 프롬프트: {token_info['prompt']} | 완료: {token_info['completion']} | 총 토큰: {token_info['total']}")
                
    except Exception as e:
        st.error(f"요약 생성 중 오류가 발생했습니다: {e}")