import streamlit as st
import time
import os

def app():
    # 페이지 제목 설정
    st.title("로딩중..")

    with st.spinner("Wait for it...", show_time=True):
        time.sleep(5)
    st.success("Done!")
    st.button("Rerun")

    # 로딩이 끝난 후 화면 전환
    st.session_state.page = "itv3"
    st.rerun()

    # # 이미지 경로 설정
    # image_path = os.path.join("images", "Loading_icon.gif")

    # # 로딩 이미지 표시 (st.empty()를 사용해 동적으로 변경 가능)
    # image_placeholder = st.empty()
    # image_placeholder.image(image_path, use_column_width=True)

    # # 카운트다운 텍스트 리스트
    # countdown_text = ["3", "2", "1", "START"]

    # # 텍스트 표시할 공간 생성
    # text_placeholder = st.empty()

    # # 카운트다운 실행
    # for text in countdown_text:
    #     text_placeholder.markdown(f"<h1 style='text-align: center;'>{text}</h1>", unsafe_allow_html=True)
    #     time.sleep(1)  # 1초 대기