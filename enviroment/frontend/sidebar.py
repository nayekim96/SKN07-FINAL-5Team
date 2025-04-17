import streamlit as st

def show_sidebar():
    st.sidebar.title("메뉴")

    if st.sidebar.button("메인페이지"):
        st.switch_page("pages/main_page.py")

    if st.sidebar.button("면접관리"):
        st.switch_page("pages/mng_1.py")

    if st.sidebar.button("채용공고"):
        st.switch_page("pages/recruit.py") # 여기 눌렀을때 api 호출출

    if st.sidebar.button("모의면접"):
        st.switch_page("pages/mng_1.py")

    if st.sidebar.button("면접 히스토리"):
        st.switch_page("pages/his1.py")

