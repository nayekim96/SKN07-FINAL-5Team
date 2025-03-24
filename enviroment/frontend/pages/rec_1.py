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

# 랜덤 추천 공고를 보여주는 함수
st.title("추천 공고")
st.write("이력서를 등록해 보세요! 내 이력에 맞는 공고를 추천해드릴게요.")

# 랜덤 추천 공고 섹션 제목
st.subheader("🎲 랜덤 추천 공고")

# 랜덤 추천 공고 리스트 (샘플 데이터)
random_jobs = [
    {"기업": "삼성전자", "직무": "데이터 분석가", "링크": "https://samsung.com"},
    {"기업": "네이버", "직무": "백엔드 개발자", "링크": "https://naver.com"},
    {"기업": "카카오", "직무": "프론트엔드 개발자", "링크": "https://kakao.com"},
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

# 리스트에 있는 공고들을 하나씩 출력
for job in random_jobs:
    st.markdown(f"""
        <div class="job-box">
            <p class="job-title">{job['기업']} - {job['직무']}</p>
            <a href="{job['링크']}" class="apply-link" target="_blank">공고 보기</a>
        </div>
    """, unsafe_allow_html=True)