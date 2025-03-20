import streamlit as st

def app():
    st.title("면접 히스토리")
    # 면접 데이터 샘플 / 나중에 실제 데이터 삽입 예정
    interviews = [
        {"title": "종합 레포트 / 질문 별 면접", "date": "2025.03.06", "company": "기업", "role": "데이터 분석", "level": "신입"},
        {"title": "종합 레포트 / 실전 면접", "date": "2025.03.13", "company": "기업", "role": "PM", "level": "신입"},
        {"title": "종합 레포트 / 실전 면접", "date": "2014.03.19", "company": "기업", "role": "데이터 엔지니어", "level": "경력"},
    ]

    # 면접 히스토리 출력
    for interview in interviews:
        with st.expander(f"{interview['title']} ({interview['date']})"):
            st.write(f"**기업:** {interview['company']}")
            st.write(f"**직무:** {interview['role']}")
            st.write(f"**경력:** {interview['level']}")
            if st.button(f"면접 결과 분석 ({interview['date']})"):
                st.write("면접 결과 분석 페이지로 이동합니다.")
    