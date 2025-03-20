import streamlit as st
import requests
from dotenv import load_dotenv
import os
st.set_page_config(layout="wide")
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

# 환경파일 로드
load_dotenv()

# 백엔드 연동 테스트
try:
    test_req = requests.get(os.environ.get('API_URL'))
    user_info = requests.get(os.environ.get('API_URL') + "/get_user_info")
except requests.exceptions.RequestException as e:
    test_req, user_info = None, None
    st.error(f"백엔드 연결 실패: {e}")

# 세션 상태 초기화 (기본값 설정)
if "page" not in st.session_state:
    st.session_state.page = "mng_1"  # 기본적으로 첫 번째 페이지에서 시작

# 사이드바 메뉴 추가
st.sidebar.title("메뉴")
if st.sidebar.button("면접관리"):
    st.session_state.switch_page = "mng_1"
    st.rerun()
if st.sidebar.button("추천공고"):
    st.session_state.page = "rec_1"
    st.rerun()
if st.sidebar.button("모의면접"):
    st.session_state.page = "itv1"
    st.rerun()
if st.sidebar.button("면접 히스토리"):
    st.session_state.page = "his1"
    st.switch_page("pages/his1.py")



# st.switch_page 사용

