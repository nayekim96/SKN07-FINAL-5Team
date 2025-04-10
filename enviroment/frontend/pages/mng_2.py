import streamlit as st
import os
import sys
from sidebar import show_sidebar

# --------- IMPORT CLASS FROM OTHER DIRS ----------
# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/enviroment/frontend)
main_dir = os.path.abspath(os.path.join(current_dir, ".."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

# 모의 면접 URL class import
from utils.mock_interview import Mock_interview
interview = Mock_interview()

# 최상위 디렉토리 (/enviroment)
top_dir = os.path.abspath(os.path.join(main_dir, ".."))
if top_dir not in sys.path:
    sys.path.append(top_dir)

# 면접 질문 생성 class import
from backend.generate_question import GenerateQuestion
question = GenerateQuestion()

# --------- sidebar 호출 ---------
st.set_page_config(layout="wide")
show_sidebar()

# --------- CSS (상단 여백 제거) ---------
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

def set_company_job_info():
    """
    기업/직무/경력 정보 세션 저장
    """
    st.session_state['company_name'] = company_name
    st.session_state['job_name'] = job_title
    st.session_state['experience'] = experience_years
    if experience_years == '경력':
        st.session_state['experience_year'] = experience_placeholder

# --------- streamlit 구현부 ---------
st.title("기업 / 직무 / 경력 입력")

common_select_text = "선택해주세요"

# 기업 리스트 조회
# 첫번째 문구는 "선택해주세요" 로 나오게 추가
company_info = interview.get_company_list()
company_list = company_info['company_list']
# 직무 리스트 조회
# 첫번째 문구는 "선택해주세요" 로 나오게 추가
job_info = interview.get_job_list()
job_list = job_info['job_list']


# 기업 입력
company_name = st.selectbox("기업 선택", company_info['labels']) 
# 비어 있는 컨테이너 생성
company_placeholder = st.empty()

# 직무 입력 
job_title = st.selectbox("지원 직무 선택", job_info['labels']) 
# 비어 있는 컨테이너 생성
job_placeholder = st.empty()

# 경력 입력
experience_years = st.selectbox("경력", ["신입", "경력"])
# 비어 있는 컨테이너 생성
experience_placeholder = st.empty()

# 버튼을 거의 붙여서 정렬
col1, col2 = st.columns([5, 5])

# 이전, 다음 페이지 이동
# with col1:
#     if st.button("이전"):
#         st.session_state["page"] = "mng_1" # 포트폴리오 업로드 페이지 이동
#         st.rerun()

if experience_years == '경력':
    experience_placeholder.number_input('연차를 입력하세요', value=1, step=1, min_value=1, max_value=50, format="%d")
else:
    experience_placeholder.empty()

with col2:
    if st.button("입력 완료"):
        # 기업 확인
        if company_name == common_select_text:
            company_placeholder.warning('기업을 선택해주세요!' , icon="⚠️")
        # 직무 확인
        if job_title == common_select_text:
            job_placeholder.warning('직무를 선택해주세요!' , icon="⚠️")
        # 기업, 직무 골랐을 시 면접 질문 생성 및 장비테스트 페이지 이동
        if company_name != common_select_text and \
           job_title != common_select_text:
            set_company_job_info()

            # -------- 면접 질문 생성 --------
            # session내 기업/직무/경력 정보 변수 선언

            company_nm = st.session_state['company_name']
            job_nm = st.session_state['job_name']
            experience = st.session_state['experience']

            user_queries = [company_nm, job_nm, experience]

            # 지원자료, 면접 후기 데이터 로드
            applications = question.get_application_mats_from_db(user_id='interview')
            prev_questions = question.get_prev_questions_from_db(company_nm, job_nm, experience)

            # 질문 생성 후 session에 저장
            st.session_state['new_questions'] = question.generate_question(prev_questions, applications, user_queries)

            #장비테스트 페이지 이동
            st.switch_page("pages/equipment_test.py")








