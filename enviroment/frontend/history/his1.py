import streamlit as st
import streamlit as st
from datetime import datetime # 나중에 datetime 쓸거 같아서 넣어놓음

def app():
    
    # 페이지 제목 및 스타일 설정
    st.title("면접 히스토리")

    # 샘플 면접 데이터 (DB 연동 가능)
    interviews = [
        {"title": "종합 레포트 / 질문 별 면접", "date": "2025.03.06", "company": "기업", "role": "데이터 분석", "level": "신입"},
        {"title": "종합 레포트 / 실전 면접", "date": "2025.03.13", "company": "기업", "role": "PM", "level": "신입"},
        {"title": "종합 레포트 / 실전 면접", "date": "2014.03.19", "company": "기업", "role": "데이터 엔지니어", "level": "경력"},
    ]

    # 면접 히스토리 리스트
    for interview in interviews:
        with st.expander(f"📄 {interview['title']} ({interview['date']})"):
            st.write(f"**기업:** {interview['company']}")
            st.write(f"**직무:** {interview['role']}")
            st.write(f"**경력:** {interview['level']}")

            # 페이지 이동을 위한 버튼
            btn_key = f"btn_{interview['date']}"
            if st.button("📊 면접 결과 분석", key=btn_key):
                st.session_state['selected_interview'] = interview
                st.switch_page("pages/interview_analysis")  # 페이지 이동

    # 체크 포인트


    ## 면접 데이터 샘플 / 나중에 실제 데이터 삽입 예정
    #interviews = [
    #    {"title": "종합 레포트 / 질문 별 면접", "date": "2025.03.06", "company": "기업", "role": "데이터 분석", "level": "신입"},
    #    {"title": "종합 레포트 / 실전 면접", "date": "2025.03.13", "company": "기업", "role": "PM", "level": "신입"},
    #    {"title": "종합 레포트 / 실전 면접", "date": "2014.03.19", "company": "기업", "role": "데이터 엔지니어", "level": "경력"},
    #]
    #
    ## 면접 히스토리 출력 
    #for interview in interviews:
    #    with st.expander(f"{interview['title']} ({interview['date']})"):
    #        st.write(f"**기업:** {interview['company']}")
    #        st.write(f"**직무:** {interview['role']}")
    #        st.write(f"**경력:** {interview['level']}")
    #        if st.button(f"면접 결과 분석 ({interview['date']})"):
    #            st.write("면접 결과 분석 페이지로 이동합니다.")
    