import os
import sys
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

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
        job_code_query = """
        SELECT
            public.catch_job_code.job_nm
        FROM 
            job_code_master_tbl AS jcm
        JOIN 
            unnest(string_to_array(jcm.catch_job_code, ',')) AS seperated_job_code ON TRUE
        JOIN 
            public.catch_job_code ON seperated_job_code::int = public.catch_job_code.job_code
        WHERE
            jcm.common_nm = %s
        """

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

        prev_questions = self.select_many_vars(select_query, conditions=(company_name, job_name, recruit_gubun), num=10)

        print(prev_questions)

        return prev_questions

    def generate_question(self, prev_questions, application_mats, user_queries):
        """
        질문 생성 Agent

        :param prev_questions: 면접 기출 질문
        :param application_mats: 지원 자료 
        """
        # 모델 정의
        llm = ChatOpenAI(
            model='gpt-4o-2024-08-06'
        )

        # 지원 자료 추출
        if application_mats:
            all_mats = pd.DataFrame(application_mats, index=[0])
            print(all_mats)
            resume = all_mats['resume_text']
            cover_letter = all_mats['cover_letter_text']
            portfolio = all_mats['popol_text']

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

        # 프롬프트
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
