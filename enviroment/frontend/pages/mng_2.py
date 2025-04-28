import streamlit as st
from sidebar import show_sidebar

st.set_page_config(layout="wide")
show_sidebar()
# 페이지 상단 공백 제거 markdown
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

# --------- streamlit 구현부 ---------
st.title("기업 / 직무 / 경력 입력")

common_select_text = "선택해주세요"

# 기업 리스트 조회
company_info = interview.get_company_list()
company_list = company_info['company_list']

# 직무 리스트 조회
job_info = interview.get_job_list()
job_list = job_info['job_list']

# 기업 입력
company_name = st.selectbox("기업 선택", company_info['labels']) 
company_placeholder = st.empty()

# 직무 입력 
job_title = st.selectbox("지원 직무 선택", job_info['labels']) 
job_placeholder = st.empty()

# 경력 입력
experience_years = st.selectbox("경력", ["신입", "경력"])
experience_placeholder = st.empty()

# 🟢 연차 슬라이더: '경력' 선택 시에만 활성화
if experience_years == '경력':
    experience_slider = experience_placeholder.slider(
        '연차를 선택하세요 (1~10년)', min_value=1, max_value=10, value=1, step=1)
else:
    experience_placeholder.empty()
    experience_slider = 0  # 신입은 0년

# 버튼 정렬
col1, col2 = st.columns([5, 5])

# 기업/직무/경력 정보 세션 저장 함수
def set_company_job_info():
    st.session_state['company_name'] = company_name
    st.session_state['company_cd'] = company_list[company_name]
    st.session_state['job_name'] = job_title
    st.session_state['job_cd'] = job_list[job_title]
    st.session_state['experience'] = experience_years  # "신입" 또는 "경력"
    st.session_state['experience_year'] = experience_slider  # 0 또는 1~40

with col2:
    if st.button("입력 완료"):
        st.session_state["page"] = "rec_1"  # 추천 공고 페이지 이동
        st.rerun()