import streamlit as st
from interview.page1 import app as page1_app
from common.page2 import app as page2_app
from common.create_q import app as create_q_app
from common.image_ocr import app as ocr_app
import requests
from dotenv import load_dotenv
import os 
import random 

# 환경파일 로드
load_dotenv()

# 백엔드 연동 테스트
test_req = requests.get(os.environ.get('API_URL'))
user_info = requests.get(os.environ.get('API_URL') + "/get_user_info")

# st.sidebar.title(test_req.json()['Hello'])
# page = st.sidebar.radio("Go to", ("Page 1", "Page 2", "zz", "질문 생성", "이미지 OCR"))


def change_page(page):
    st.session_state.page = page

if st.sidebar.button("면접관리"):
    page1_app()
if st.sidebar.button("추천공고"):
    page2_app()
if st.sidebar.button("모의면접"):
    ocr_app()
if st.sidebar.button("면접 히스토리"):
    create_q_app()

# Using "with" notation
with st.sidebar:
    add_radio = st.button(
        "Choose"
    )

# if page == "Page 1":
#     page1_app()
# elif page == "Page 2":
#     page2_app()  
# elif page == "질문 생성":
#     create_q_app()
# elif page == "이미지 OCR":
#     ocr_app()


