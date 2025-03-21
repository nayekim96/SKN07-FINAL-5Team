# PPT - 5
# 모의면접 - 옵션선택

import streamlit as st  # Streamlit 라이브러리 불러오기

def app():
    # 페이지 제목
    st.title("기업 / 직무 / 경력 입력")

    # 기업 리스트 (예시) — 추후 DB나 API로 확장 가능
    company_list = [
        "삼성전자", "삼성SDI", "삼성물산", 
        "현대자동차", "현대모비스", "현대건설", 
        "LG전자", "LG화학", "LG에너지솔루션", 
        "네이버", "카카오", "SK텔레콤", "SK하이닉스"
    ]

    # 기업명 입력 (자동완성 기능용 키워드 입력)
    keyword = st.text_input("기업명을 입력하세요", "")

    # 입력된 키워드와 일치하는 기업명 필터링
    filtered = [name for name in company_list if keyword.lower() in name.lower()] if keyword else []

    # 검색 결과 셀렉트박스로 보여주기
    if filtered:
        company_name = st.selectbox("검색 결과에서 선택하세요", filtered)
    else:
        company_name = None

    # 직무 선택
    job_title = st.selectbox("지원 직무 선택", ["선택해주세요", "데이터 분석", "백엔드 개발", "프론트엔드 개발", "AI 엔지니어"])

    # 경력 선택
    experience_years = st.selectbox("경력", ["신입", "경력"])

    # "입력 완료" 버튼 클릭 시 itv2 페이지로 이동
    if st.button("입력 완료"):
        if company_name:
            st.session_state["company"] = company_name
            st.session_state["job_title"] = job_title
            st.session_state["experience"] = experience_years
            st.session_state["page"] = "itv2"  # 다음 페이지(장비 테스트)로 이동
            st.rerun()
        else:
            st.warning("기업명을 선택해주세요.")
