import streamlit as st
import time

# 7페이지: 모의면접 - 시작 화면

st.title("모의면접 시작")

# 안내 문구
st.write("면접 준비가 되었으면 아래 버튼을 눌러 면접을 시작해주십시오.")

# 면접 시작 버튼
if st.button("면접 시작"):
    st.session_state["page"] = "itv2"  # 다음 페이지 (로딩 화면)으로 이동
    st.rerun()