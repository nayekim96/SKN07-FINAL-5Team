import os
import sys
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .prompt.prompts import qa_hum_prompt, qa_eng_prompt, qa_arts_prompt


load_dotenv()

# --------- DIRECTORY PATH SETTING ----------
# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect


class GenerateQuestion(post_db_connect):
    """
    면접 질문 생성
    """

    def __init__(self):
        super().__init__()

    # 지원 자료 특성 추출
    def get_application_mats_from_db(self, user_id):
        """
        지원 자료 데이터 로드 - 이력서, 포트폴리오, 자소서

        :param user_id: 데이터 로드 대상 user id
        """

        select_query = f"""
        SELECT resume_text, cover_letter_text, popol_text
        FROM resume_popol_history
        WHERE user_id = '{user_id}';
        """
        application_mats = self.select_one(select_query)

        return application_mats

    def get_prev_questions_from_db(self, company_name, job_name, recruit_gubun):
        """
        면접 후기 데이터 로드

        :param company_name: 기업명
        :param job_name: 직무명
        :param recruit_gubun: 경력 구분 (신입/경력)
        """

        # master table에서 입력 받은 직무코드명과 일치하는 캐치에서 사용되는 직무명 반환
        job_code_query = f"""
        SELECT
            public.catch_job_code.job_nm
        FROM 
            job_code_master_tbl AS jcm
        JOIN 
            unnest(string_to_array(jcm.catch_job_code, ',')) AS seperated_job_code ON TRUE
        JOIN 
            public.catch_job_code ON seperated_job_code::int = public.catch_job_code.job_code
        WHERE
            jcm.common_nm = '{job_name}'
        """
        actual_job_code = self.select_all(job_code_query)
        
        # RealDictRow형태로 반환된 job_nm을 리스트 형태로 변경 (변경해줘야 쿼리에서 처리 가능)
        code_names = [row['job_nm'] for row in actual_job_code]

        # code 수만큼 %s 생성    
        if code_names:
            job_names_placeholder = ','.join(['%s'] * len(code_names))
        else:
            job_names_placeholder = '%s'
            code_names = ['']

        # query에서 사용자가 면접 전 선택한 기업/직무/경력 정보와 join 한 면접 질문 가져옴.
        select_query = f"""
        SELECT interview_eval, interview_tip, interview_qa
        FROM interview_review
        WHERE company_nm LIKE %s AND job_code_nm in ({job_names_placeholder}) AND recruit_gubun LIKE %s LIMIT 10;  
        """
        company_name = f"%{company_name}%"
        recruit_gubun = f"%{recruit_gubun}%"
        conditions = (company_name, *code_names, recruit_gubun) # 리스트로 반환된 code_names를 unpack

        prev_questions = self.select_many_vars(select_query, conditions=conditions, num=10)

        return prev_questions

    def generate_question(self, prev_questions, application_mats, user_queries):
        """
        질문 생성 Agent

        :param prev_questions: 면접 기출 질문
        :param application_mats: 지원 자료 
        """
        # 모델 정의
        llm = ChatOpenAI(
            model='gpt-4o-2024-08-06',
            temperature=0
        )

        if application_mats:
            resume = application_mats['resume_text']
            cover_letter = application_mats['cover_letter_text']
            portfolio = application_mats['popol_text']

        else:
            return "지원 자료 데이터가 존재하지 않습니다."

        # 면접 기출 질문 추출
        if prev_questions:
            evals = '\n'.join([question['interview_eval'] for question in prev_questions])
            tips = '\n'.join([question['interview_tip'] for question in prev_questions])
            qas = '\n'.join([question['interview_qa'] for question in prev_questions])

            # 불필요한 문장 기호 삭제
            evals = re.sub(r'[\[\]\'\",]', '', evals)
            tips = re.sub(r'[\[\]\'\",]', '', tips)
            qas = re.sub(r'[\[\]\'\",]', '', qas)

            user_queries = '\n'.join(user_queries)
            
        else:
            return "면접 기출 질문 데이터가 존재하지 않습니다."

        # ------- 프롬프트 -------
        # 분야별 질문 생성 규칙

        prompt_content = ChatPromptTemplate.from_template(
            """
            당신은 AI 면접 질문 생성기입니다.  
            아래의 **질문 생성 규칙**과 **참고 자료**를 바탕으로, 면접자의 지원 계열에 맞는 규칙을 적용하여 **면접 예상 질문 10개**를 생성해주세요.

            면접자의 지원 자료를 분석해 **지원 직무** 및 **지원 계열**을 판단한 뒤, 해당 계열에 해당하는 질문 생성 규칙을 적용해야 합니다.

            계열 구분은 다음과 같습니다:
            - 인문 계열: {qa_hum_prompt}
            - 공학 계열: {qa_eng_prompt}
            - 예체능 계열: {qa_arts_prompt}

            ## [참고자료]
            ### 1. 면접 기출 질문
            {qas}

            ### 2. 면접 팁
            {tips}

            ### 3. 면접 평가 기준
            {evals}

            ### 4. 지원자료

            - **이력서**  
            {resume}

            - **자기소개서**  
            {cover_letter}

            - **포트폴리오**  
            {portfolio}

            ### 5. 면접자 정보
            {user_queries}
            """
        )

        # response.content 파싱
        output_parser = StrOutputParser()

        chain = prompt_content | llm | output_parser

        response = chain.invoke({
            "qa_hum_prompt": qa_hum_prompt,
            "qa_eng_prompt": qa_eng_prompt,
            "qa_arts_prompt": qa_arts_prompt,
            "qas": qas,
            "tips": tips,
            "evals": evals,
            "resume": resume,
            "cover_letter": cover_letter,
            "portfolio": portfolio,
            "user_queries": user_queries
        })

        return response

    
