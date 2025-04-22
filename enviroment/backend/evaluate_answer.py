import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from prompt.prompts import ev_hum_prompt, ev_eng_prompt, ev_arts_prompt
from generate_question import GenerateQuestion


load_dotenv()

# --------- DIRECTORY PATH SETTING ----------
# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect


# ------- 지원자료 데이터 로드 (이력서, 자기소개서, 포트폴리오) -------
def get_application_mats(user_id):
    question = GenerateQuestion()

    appli_mats = question.get_application_mats_from_db(user_id)

    return appli_mats    

# ------- 면접 데이터 로드 (질문, 답변, 권장답변, 답변시간) -------
def get_interview_data(user_id):
    
    pdb = post_db_connect()

    # interview_process 테이블에서 가장 최신 날짜의 interview id 가져오기
    select_latest_query = f"""
    SELECT interview_id
    FROM interview_process
    WHERE user_id = '{user_id}'
    ORDER BY insert_date DESC
    LIMIT 1;
    """

    latest_itv = pdb.select_one(select_latest_query)
    interview_id = latest_itv['interview_id']

    # interview_id 로 면접 데이터 가져오기
    select_answer_query = """
    SELECT ques_text, answer_user_text, answer_example_text, answer_end_time
    FROM interview_result
    WHERE interview_id = %s
    """

    answer = pdb.select_all_vars(select_answer_query, interview_id)[0]

    print(answer)

    return answer


# ------- 평가지표 세팅 -------
def evaluate_answers(interview_data, application_mats, user_query):
    """
    답변 평가 생성 Agent

    :param interview_data: 면접 데이터 (질문, 유저답변, 권장답변, 답변시간)
    :param appli_mats: 지원자료 데이터
    :param user_query: streamlit session에서 받아올 정보 (회사명, 직무, 경력)
    """
    # 모델 정의
    llm = ChatOpenAI(
        model='gpt-4o-2024-08-06'
    )

    # 지원자료 분리
    if application_mats:
        resume = application_mats['resume_text']
        cover_letter = application_mats['cover_letter_text']
        portfolio = application_mats['popol_text']

    else:
        return "지원 자료 데이터가 존재하지 않습니다."


    # 면접 데이터 분리
    if interview_data:
        question = interview_data['ques_text']
        user_answer = interview_data['answer_user_text']
        answer_time = interview_data['answer_end_time']

    else:
        return "면접 데이터가 존재하지 않습니다."

    user_query = '\n'.join(user_query)

    # 프롬프트
    prompt = ChatPromptTemplate.from_template(
        """
        당신은 AI 면접 평가자입니다.

        순서대로 면접 평가를 진행하세요.

        ** 권장답변 생성**:
        1. 아래의 면접 질문과 사용자 답변을 참고하여 [권장답변 생성규칙]에 따라 먼저 **권장 답변**을 생성하세요.  
        2. 사용자 답변과 권장 답변을 비교하여 각 항목에 대해 자연스러운 문장형 피드백을 작성해주세요.  
        3. 점수는 매기지 말고, 실제 면접관이 해주는 것처럼 진정성 있고 친절하게 작성해주세요.
        
        **면접 답변 평가**:
        1. 아래의 [면접 질문]을 읽고, 질문의 **의도**를 파악한 뒤
        2. [평가 항목] 중에서 질문의 의도에 **적합한 항목만 선택하여 평가**해주세요.
        3. 최종적으로 아래 형식을 참고하여, 각 항목별로 평가를 작성해주세요.

        면접자의 [지원정보]를 분석하여 **지원 직무** 및 **지원 계열**을 판단한 뒤, 해당 계열에 해당하는 규칙을 적용해야 합니다.

        ---
        [지원정보]
        {user_query}

        계열 구분은 다음과 같습니다:
        - 인문 계열: {ev_hum_prompt}
        - 공학 계열: {ev_eng_prompt}
        - 예체능 계열: {ev_arts_prompt}

        면접자의 [지원자료]를 분석해 사용자 직무, 기술/역량, 프로젝트를 파악하고, 권장답변 생성 및 답변평가 시 참고하세요.
        지원자료에서 이름을 찾고, 답변 생성시 사용자를 이름으로 지칭하세요.

        [지원자료]
        - **이력서**  
        {resume}

        - **자기소개서**  
        {cover_letter}

        - **포트폴리오**  
        {portfolio}

        ---
        [면접 질문]:
        {question}

        [사용자 답변]:
        {user_answer}

        [답변 시간]:
        {answer_time}
        ---

        [권장답변 생성규칙]
        1. <지원정보>에서 면접자의 희망 기업, 직무, 경력을 파악해 권장답변 생성에 참고하세요.
        2. 질문에서 의도를 파악해 의도에 부합하는 답변을 생성하세요.
        3. 답변은 <지원정보>와 관련이 있어야 하고, 문장이 논리적이어야 합니다.
        4. 직업명은 보편적으로 사용하는 명칭을 사용하세요.
        ---
        [평가 항목]

        1. 논리성 (Logical Coherence)  
        - 답변이 논리적으로 구성되었는가?  
        - 문장 간의 연결이 자연스러운가?

        2. 질문 이해도 (Question Comprehension)  
        - 질문의 핵심 의도를 정확히 이해하고 답변했는가?

        3. 직무 전문성 (Job-Related Expertise)
        - 직무역량 질문인 경우에만 평가하세요.
        - 직무와 관련된 지식 또는 경험을 구체적으로 언급했는가?

        4. 표현 습관 (Speech Habits)  
        - 반복되는 말버릇, 불필요한 표현 또는 과장된 표현이 있었는가?

        5. 시간 활용력 (Time Management)  
        - 90초 이내에 핵심 내용을 명확히 전달했는가?  
        - 20초 미만이거나 90초를 초과하는 경우 감점 요인

        6. 전달력 (Clarity of Delivery)  
        - 전달하는 내용이 명확하고 이해하기 쉬웠는가?

        7. 자기표현력 (Self-Presentation)
        - 의사소통 능력 질문인 경우에만 평가하세요.  
        - 자신에 대한 표현이 진정성 있고 긍정적이었는가?

        [평가 방식]  
        - 질문에 적합한 항목만 평가
        - 각 항목에 대해 간결한 문장으로 피드백 작성
        ---

        [출력 형식 예시]
        다음 형식의 JSON으로 응답해주세요:

        {{
        "권장답변": "...",
        "피드백": {{
            "논리성": "...",
            "질문 이해도": "...",
            "직무 전문성": "...",
            "표현 습관": "...",
            "시간 활용력": "...",
            "전달력": "...",
            "자기표현력": "..."
        }},
        "총평": "..."
        }}
        ※ 각 피드백 항목은 질문에 적합한 항목에 대해서만 작성해주세요.
        ※ 작성하지 않을 항목은 null 값으로 두어도 됩니다.
        ※ 전체 구조가 JSON으로 유효하게 닫히도록 작성해주세요.

        """
    )

    # output parser
    output_parser = JsonOutputParser()

    # 체인 생성
    chain = prompt | llm | output_parser

    # 요청
    response = chain.invoke({
        'user_query': user_query,
        'ev_hum_prompt': ev_hum_prompt,
        'ev_eng_prompt': ev_eng_prompt,
        'ev_arts_prompt': ev_arts_prompt,
        'resume': resume,
        'cover_letter': cover_letter,
        'portfolio': portfolio,
        'question': question,
        'user_answer': user_answer,
        'answer_time': answer_time
    })

    return response

# 권장 답변 생성하여 RDB 저장
def save_example_answer(response):
    pass


# if __name__ == '__main__':
#     appli_mats = get_application_mats('interview')
#     interview_data = get_interview_data('interview')

#     company_name = '네이버'
#     job_name = 'IT/개발/데이터'
#     experience = '신입'

#     user_queries = [company_name, job_name, experience]

#     results = evaluate_answers(interview_data, appli_mats, user_queries)

#     print(results['피드백'])