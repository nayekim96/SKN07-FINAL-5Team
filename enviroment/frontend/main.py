import streamlit as st
from interview.mng1 import app as page1_app  # 이력서 업로드 페이지
from common.rec1 import app as page2_app  # 추천공고 랜덤 
from common.rec2 import app as page3_app  # 추천공고 맞춤춤
from interview.itv1 import app as ocr1_app  # 모의면접 - 옵션선택
from interview.itv2 import app as ocr2_app  # 모의면접 - 장비 테스트
from interview.itv3 import app as ocr3_app  # 모의면접 - 시작화면
from interview.itv4 import app as ocr4_app  # 모의면접 - 시작 타이머
from interview.itv5 import app as ocr5_app  # 모의면접 - 실전 면접
from history.his1 import app as his1_app  # 히스토리
from history.his2 import app as his2_app  # 히스토리 - 종합 레포트
from history.his3 import app as his3_app  # 히스토리 - 상세 피드백
import requests
from dotenv import load_dotenv
import os

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
    st.session_state.page = "mng_1"
    st.rerun()
if st.sidebar.button("추천공고"):
    st.session_state.page = "rec_1"
    st.rerun()
if st.sidebar.button("모의면접"):
    st.session_state.page = "itv1"
    st.rerun()
if st.sidebar.button("면접 히스토리"):
    st.session_state.page = "his1"
    st.rerun()

# 페이지 이동 로직
if st.session_state.page == "mng_1":
    page1_app()
elif st.session_state.page == "rec_1":
    page2_app()
elif st.session_state.page == "rec_2":
    page3_app()
elif st.session_state.page == "itv1":
    ocr1_app()
elif st.session_state.page == "itv2":
    ocr2_app()
elif st.session_state.page == "itv3":
    ocr3_app()
elif st.session_state.page == "itv4":
   ocr4_app()
elif st.session_state.page == "itv5":
   ocr5_app()
elif st.session_state.page == "his1":
    his1_app()
elif st.session_state.page == "his2":
    his2_app()
elif st.session_state.page == "his3":
    his3_app()
else:
    st.write("잘못된 페이지입니다.")
