import streamlit as st
import openai
import pandas as pd
from db_util.db_utils import post_db_connect
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage


# --------- 모델 정의 ----------

llm = ChatOpenAI(
    model='gpt-4o-2024-08-06'
)

# --------- DB 연결 정의 ----------
pdb = post_db_connect()

# --------- 지원 자료 데이터 가져오기 ----------
def get_application_mats_from_db(user_id):
    # 사용자의 지원 자료를 가져옴.
    select_query = f"""
    SELECT resume_text, cover_letter_text, popol_text
    FROM resume_popol_history
    WHERE user_id = '{user_id}';
    """
    application_mats = pdb.select_one(select_query)

    return application_mats


# --------- 기업/직무/경력에 기반한 면접 후기 데이터 가져오기 ----------
def get_prev_questions_from_db(company_name, job_name, recruit_gubun):
    # query에서 사용자가 면접 전 선택한 기업/직무/경력 정보와 join 한 면접 질문 가져옴.
    select_query = """
    SELECT interview_eval, interview_tip, interview_qa
    FROM interview_review
    WHERE company_nm LIKE %s AND job_code_nm LIKE %s AND recruit_gubun LIKE %s LIMIT 10;
    """

    # 사용자 입력값
    company_name = f"%{company_name}%"
    job_name = f"%{job_name}%"
    recruit_gubun = f"%{recruit_gubun}%"

    prev_questions = pdb.select_many_vars(select_query, conditions=(company_name, job_name, recruit_gubun), num=10)

    print(prev_questions)

    return prev_questions


# --------- 질문 생성 ----------
def generate_question(prev_questions, application_mats):

    # 지원 자료 추출
    if application_mats:
        all_mats = pd.DataFrame(application_mats).transpose()
        print(all_mats)
        resume = all_mats[0]
        cover_letter = all_mats[1]
        portfolio = all_mats[2]

    else:
        return "지원 자료 데이터가 존재하지 않습니다."

    # 면접 기출 질문 추출
    if prev_questions:
        all_results = pd.DataFrame(prev_questions)
        print(all_results)
        evals = "\n".join([f"{row[0]}" for _, row in all_results.iterrows()])
        tips = "\n".join([f"{row[1]}" for _, row in all_results.iterrows()])
        qas = "\n".join([f"{row[2]}" for _, row in all_results.iterrows()])
        
    else:
        return "면접 기출 질문 데이터가 존재하지 않습니다."

    user_queries = []

    prompt_content = f"""
    당신은 AI 면접 질문 생성기입니다.
    아래의 **질문 생성 규칙**과 **참고 자료**를 바탕으로 **면접 예상 질문 10개**를 생성해주세요.

    ## [질문 생성 규칙]
        1. 참고 자료의 면접 기출 질문을 참고하여 질문을 생성하세요.

        2. 기출 질문과 완전히 동일한 질문은 피하고, 새로운 질문으로 변형하세요.

        3. 참고 자료의 면접 팁과 평가 기준을 고려해, 질문 의도로 설정하세요.

        4. 지원 자료가 있는 경우, 자료를 분석해 진행한 프로젝트를 추출하고 진행한 프로젝트에 관한 질문을 생성하세요. 질문 하단에 추출한 프로젝트를 명시하세요.

        5. 지원 자료가 있는 경우, 자료를 분석해 희망 직무, 기술스택을 추출하고 기술 관련 질문 생성 시 참고하세요. 질문 하단에 추출한 직무, 기술스택을 명시하세요.

        6. 참고 자료의 면접자 정보에 적합한 질문을 생성하세요.

        7. 각 질문의 질문 의도는 중복되어선 안 되고, 의미가 비슷한 질문은 제외하세요.

        8. 아래 항목에 맞춰 질문 수를 분배하세요:

        * 인성/적성 질문: 2개

        * 기술 관련 질문: 3개

        * 이력서 또는 포트폴리오 기반 질문: 3개

        * 업무 스킬 질문: 2개

        9. 참고 자료를 분석해 해당 기업이 중요하게 생각하는 가치관을 추출하고, 해당 가치관에 적합한 사람인지 판단하는 질문을 생성하세요. 

        10. 질문 내용 하단에 어떤 기출 질문을 참고했는지 명시해주세요.
        
        11. 질문은 아래 형식에 맞춰 출력해주세요:
            1. 질문 내용
            2. 질문 내용
            ...
            10. 질문 내용


    ## [참고 자료]
    ### 면접 기출 질문:
        {qas}

    ### 면접 팁:
        {tips}

    ### 면접 평가 기준:
        {evals}

    ### 지원 자료
    * 이력서:
        {resume}
    
    * 자기소개서:
        {cover_letter}

    * 포트폴리오:
        {portfolio}

    ### 면접자 정보:
        {', '.join(user_queries)}

    """

    response = llm([HumanMessage(content=prompt_content)])
    return response.content

# ---------- Streamlit 구현

st.set_page_config(page_title="AI 맞춤 면접 질문 생성기", layout="wide", initial_sidebar_state="collapsed")
st.title("✒️맞춤 면접 질문을 생성해드려요.")

st.markdown(
    """
    <style>
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: inline-block;
    }
    .human-message {
        background-color: #F0F8FF; 
        text-align: left;
        color: black;
    }
    .ai-message {
        background-color: #E6E6FA; 
        text-align: left;
        color: black;
    }
    .stButton > button {
        background-color: yellow; 
        border: none;
        color: black;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .stButton > button:hover {
        background-color: #ffcc00; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.form("지원 정보를 입력해주세요."):
    company_name = st.text_input("지원 기업명:")
    job_name = st.text_input("지원 직무:")
    recruit_gubun = st.text_input("경력 구분:")

    user_queries = [company_name, job_name, recruit_gubun]
    
    submitted = st.form_submit_button("질문 생성")

if submitted:
    prev_questions = get_prev_questions_from_db(company_name, job_name, recruit_gubun)
    application_mats = get_application_mats_from_db(user_id='interview')

    response = generate_question(prev_questions, application_mats)

    # 대화 기록 출력
    st.markdown(f"<div class='chat-message human-message'>{', '.join(user_queries)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><strong>예상 질문</strong><br/><div class='chat-message ai-message'>{response}</div></div>", unsafe_allow_html=True)

if submitted and not user_queries:
    st.warning("지원 정보를 입력해주세요.")
