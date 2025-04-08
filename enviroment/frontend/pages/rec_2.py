import streamlit as st
from sidebar import show_sidebar
st.set_page_config(layout="wide")
show_sidebar()
# Remove whitespace from the top of the page and sidebar
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

st.subheader("추천 공고")

# 사용자가 이력서를 업로드했는지 확인
if "uploaded_resume" not in st.session_state:
    # 이력서가 업로드되지 않았다면 경고 메시지 출력
    st.warning("회원님의 이력서를 기반으로 추천하는 공고입니다.")
else:
    # 맞춤 추천 공고 리스트 (샘플 데이터)
    tailored_jobs = [
        {"기업": "LG CNS", "직무": "데이터 엔지니어", "링크": "https://lgcns.com"},
        {"기업": "쿠팡", "직무": "머신러닝 엔지니어", "링크": "https://coupang.com"},
        {"기업": "SK텔레콤", "직무": "AI 연구원", "링크": "https://sktelecom.com"},
    ]

    # 스타일 적용
    st.markdown("""
        <style>
            .job-box {
                border: 2px solid #ddd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            .job-title {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            .apply-link {
                font-size: 14px;
                color: black; /* 링크 색상을 기본값(검정)으로 설정 */
                text-decoration: underline;
            }
            .apply-link:hover {
                color: gray; /* 마우스 올리면 색상이 변하도록 설정 */
            }
        </style>
    """, unsafe_allow_html=True)

    # 리스트에 있는 맞춤 공고를 하나씩 출력
    for job in tailored_jobs:
        st.markdown(f"""
            <div class="job-box">
                <p class="job-title">{job['기업']} - {job['직무']}</p>
                <a href="{job['링크']}" class="apply-link" target="_blank">공고 보기</a>
            </div>
        """, unsafe_allow_html=True)
