# PPT - 8
# 모의면접 - 시작 타이머

import streamlit as st

def app():
    st.title("실전 면접")

import streamlit as st
import time
import os

def app():
    # 페이지 제목 설정
    st.title("로딩중..")

    with st.spinner("Wait for it...", show_time=True):
        time.sleep(3)
    st.success("Done!")
    st.button("Rerun")

    # 로딩이 끝난 후 화면 전환
    st.session_state.page = "itv5" # 다음 페이지 (실전 면접접)으로 이동
    st.rerun()