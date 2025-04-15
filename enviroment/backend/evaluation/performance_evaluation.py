import os
import sys
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain


current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect

pdb = post_db_connect()

def get_application_mats_from_db(user_id):
    """
    지원 자료 데이터 로드 - 이력서, 포트폴리오, 자소서

    :param user_id: 데이터 로드 대상 user id
    """

    select_query = f"""
    SELECT resume_text, cover_letter_text, popol_text
    FROM resume_popol_history
    WHERE user_id = '{user_id}';
    """
    application_mats = pdb.select_one(select_query)

    return application_mats

def get_job_opening_from_db():
    """
    채용공고 데이터 로드
    """

    select_query = f"""
    SELECT rec_idx, CONCAT(jd_text, ',', recruit_title) AS jd_text_set
    FROM saramin_recruit_detail;
    """
    application_mats = pdb.select_one(select_query)

    return application_mats

def get_entities():
    # LLM 모델 초기화
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0
    )

    # 지원 자료 데이터 로드
    user_data = get_application_mats_from_db('interview')

    resume = user_data['resume_text']
    cover_letter = user_data['cover_letter_text']
    portfolio = user_data['popol_text']

    # 프롬프트 정의
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        """
        당신은 문서를 분석해 특징을 추출하는 AI 문서 분석기입니다. 
        아래의 [이력서], [자기소개서], [포트폴리오]를 분석해 명시된 [특징]을 [출력 규칙]에 따라 추출해주세요.

        ### [특징]:
        1. 주요 직무 키워드 (예: 데이터 분석, 백엔드 개발, AI 모델링)
        2. 산업군/도메인 (예: IT, 제조업, 생산업)
        3. 기술, 스킬
        4. 경력 여부, 최종 학력
        5. 활동 지역

        ### [출력 규칙]:
        1. 직무 키워드:
        2. 산업군/도메인:
        3. 기술/스킬:
        4. 경력/학력:
        5. 지역:

        ### [이력서]:
        {resume}

        ### [자기소개서]:
        {cover_letter}

        ### [포트폴리오]:
        {portfolio}
        """
    )

    chat_prompt_template = ChatPromptTemplate.from_messages([human_message_prompt])

    # 체인 생성
    chain = LLMChain(llm=llm, prompt=chat_prompt_template)

    # invoke 호출
    response = chain.invoke({
        "resume": resume,
        "cover_letter": cover_letter,
        "portfolio": portfolio
    })

    print(response['text'])

    result = response['text'].split('\n')

    keyword = [ sentence.split(': ')[1] for sentence in result ]

    print(keyword)

    return keyword





