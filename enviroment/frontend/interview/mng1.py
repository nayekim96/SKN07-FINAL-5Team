# PPT - 2
# 면접관리 - 문서 업로드

import streamlit as st

def app():
    st.markdown("""
        <h1 style='text-align: center; font-size: 36px;'>이력서 / 자소서 / 포트폴리오</h1>
        <h2 style='text-align: center; font-size: 30px;'>업로드</h2>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color: #333;'>이력서</h4>", unsafe_allow_html=True)
    resume_file = st.file_uploader("이력서를 업로드하세요 (PDF)", type=["pdf"])

    st.markdown("<h4 style='color: #333;'>자소서</h4>", unsafe_allow_html=True)
    cover_letter_file = st.file_uploader("자소서를 업로드하세요 (PDF)", type=["pdf"])

    st.markdown("<h4 style='color: #333;'>포트폴리오</h4>", unsafe_allow_html=True)
    portfolio_file = st.file_uploader("포트폴리오를 업로드하세요 (PDF)", type=["pdf"])

    # 🔘 버튼은 항상 보이게 하고, 클릭 시 메시지만 출력
    if st.button("입력 완료"):
        st.success("업로드가 완료되었습니다.")