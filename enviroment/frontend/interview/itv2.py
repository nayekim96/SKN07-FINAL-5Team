# PPT - 6
# 모의면접 - 장비 테스트

import streamlit as st
import time

def app():
    st.title("장비 테스트")

    # 면접 시작 버튼
    if st.button("테스트 완료"):
        st.session_state["page"] = "itv3"  # 다음 페이지 (시작 화면)으로 이동
        st.rerun()