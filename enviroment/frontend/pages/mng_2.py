import streamlit as st
from sidebar import show_sidebar
from ...backend.db_util.db_utils import post_db_connect


# --------- DB 연결 정의 ----------
pdb = post_db_connect()

# --------- Data Load ----------
def get_company_master_tbl_from_db():
    """
    기업 마스터 테이블 데이터 로드
    """
    select_query = f"""
    SELECT common_id, common_nm
    FROM company_code_master_tbl;
    """
    company_master = pdb.select_one(select_query)

    return company_master

def get_job_master_tbl_from_db():
    """
    직무 마스터 테이블 데이터 로드
    """
    select_query = f"""
    SELECT common_id, common_nm
    FROM company_code_master_tbl;
    """
    company_master = pdb.select_one(select_query)

    return company_master


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

st.title("기업 / 직무 / 경력 입력")

# 기업 입력
company_name = st.selectbox("기업명 선택", ["선택해주세요"])

# 직무 입력 
job_title = st.selectbox("지원 직무 선택", ["선택해주세요"])

# 경력 입력
experience_years = st.selectbox("경력", ["신입", "경력"])

# 버튼을 거의 붙여서 정렬
col1, col2 = st.columns([1, 1])

# 이전, 다음 페이지 이동
with col1:
    if st.button("이전"):
        st.session_state["page"] = "mng_1" # 포트폴리오 업로드 페이지 이동
        st.rerun()

with col2:
    if st.button("입력 완료"):
        st.session_state["page"] = "rec_1"  # 추천 공고 페이지 이동
        st.rerun()