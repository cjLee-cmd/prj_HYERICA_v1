import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")

# API 키가 설정되지 않은 경우 오류 메시지 출력
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# 클라이언트에 API 키 전달
client = OpenAI(api_key=api_key)

# 어시스턴트 ID
#ASSISTANT_ID = "asst_YfPptwUj4Jky7AVIfd0hPR7X"
ASSISTANT_ID = "asst_o8bfAyGKf7mx6zYdrMXsIEFT"

# 세션 상태 초기화
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 스트림릿 앱 제목
st.title("한양대학교 ERICA 인공지능 매뉴얼")

# 대화 내용 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 새로운 메시지 처리 함수
def process_input():
    if st.session_state.user_input:
        user_input = st.session_state.user_input
        
        # 새 스레드 생성 (처음 질문할 때만)
        if not st.session_state.thread_id:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        # 사용자 메시지 추가
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # 실행 생성
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID
        )

        # 실행 완료 대기
        with st.spinner('답변을 생성 중입니다...'):
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break

        # 메시지 가져오기
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # 메시지 업데이트
        st.session_state.messages = []
        for msg in reversed(messages.data):
            role = "사용자" if msg.role == "user" else "AI"
            content = msg.content[0].text.value
            st.session_state.messages.append({"role": role, "content": content})

        # 입력 필드 초기화
        st.session_state.user_input = ""

# 사용자 입력 (화면 하단에 위치)
st.text_input("질문을 입력하세요:", key="user_input", on_change=process_input)
