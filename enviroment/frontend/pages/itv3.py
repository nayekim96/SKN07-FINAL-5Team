import streamlit as st

st.title("실전 면접")

st.markdown(
    """
    <style>
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: inline-block;
    }
    .ai-message {
        background-color: #E6E6FA; 
        text-align: left;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'new_questions' in st.session_state:
    print(st.session_state['new_questions'])  # 질문 내용 출력

response = st.session_state['new_questions']

# 대화 기록 출력
st.markdown(f"<div><strong>예상 질문</strong><br/><div class='chat-message ai-message'>{response}</div></div>", unsafe_allow_html=True)
