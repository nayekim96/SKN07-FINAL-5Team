import os
import sys
import streamlit as st
from datetime import datetime # 나중에 datetime 쓸거 같아서 넣어놓음
from sidebar import show_sidebar

# --------- IMPORT CLASS FROM OTHER DIRS ----------
# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 최상위 디렉토리 (/enviroment/frontend)
env_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if env_dir not in sys.path:
    sys.path.append(env_dir)

# 면접 질문 생성 class import
from backend.evaluate_answer import get_application_mats, get_interview_data, evaluate_answers
from backend.create_total_report import get_all_reviews, total_report


st.set_page_config(layout="wide")
show_sidebar()

# Remove whitespace from the top of the page and sidebar
st.markdown(
    """
        <style>
                .stAppHeader {
                    background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
                    visibility: visible;  /* Ensure the header is visible */
                }

            .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
                [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
    unsafe_allow_html=True,
)

# 페이지 제목
st.title("면접 히스토리")

# 데이터
interviews = [
    {"title": "종합 레포트 / 질문 별 면접", "date": "2025.03.06", "company": "기업", "role": "데이터 분석", "level": "신입"},
    {"title": "종합 레포트 / 실전 면접", "date": "2025.03.13", "company": "기업", "role": "PM", "level": "신입"},
    {"title": "종합 레포트 / 실전 면접", "date": "2014.03.19", "company": "기업", "role": "데이터 엔지니어", "level": "경력"},
]

# 면접 히스토리 리스트
for interview in interviews:
    with st.expander(f"📄 {interview['title']} ({interview['date']})"):
        st.write(f"**기업:** {interview['company']}")
        st.write(f"**직무:** {interview['role']}")
        st.write(f"**경력:** {interview['level']}")

        # 페이지 이동을 위한 버튼
        btn_key = f"btn_{interview['date']}"
        if st.button("📊 면접 결과 분석", key=btn_key):
            st.session_state['selected_interview'] = interview

            # -------- 답변 평가 생성 --------
            # 질문별 피드백 (user_id 동적으로 받도록 수정 필요 !!)
            appli_mats = get_application_mats(user_id='interview')
            interview_data = get_interview_data(user_id='interview')

            company_name = interview['company']
            job_name = interview['role']
            experience = interview['level']

            user_queries = [company_name, job_name, experience]

            evals = evaluate_answers(interview_data, appli_mats, user_queries)

            st.session_state['evaluations'] = evals

            # 종합 피드백
            reviews = get_all_reviews('interview')
            total_evals = total_report(reviews)

            st.session_state['total_evaluations'] = total_evals

            st.switch_page("pages/his2.py")   # 페이지 이동

