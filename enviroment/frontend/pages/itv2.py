import streamlit as st
import time
import os
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
# 페이지 제목 설정
st.title("로딩중입니다 기다려!")

st.markdown("![Alt Text](https://blog.kakaocdn.net/dn/tToNP/btsvPnc77bN/0P5cqJMFM8hpaQcrIbK6v1/img.gif)")
time.sleep(2)

# 로딩이 끝난 후 화면 전환
st.switch_page("page/itv3.py")
