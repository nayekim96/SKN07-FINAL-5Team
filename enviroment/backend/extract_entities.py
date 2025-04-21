import re
import os
import sys
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect

class ExtractEntities(post_db_connect):
    """
    특성 추출 - 이력서, 자기소개서, 포트폴리오
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

    def get_job_opening_from_db(self):
        """
        채용공고 데이터 로드, CSV 저장
        """

        select_query = f"""
        SELECT rec_idx, jd_text
        FROM saramin_recruit_detail;
        """
        job_opening = self.select_all(select_query)

        pd.DataFrame(job_opening).to_csv('./data/job_opening_3.csv')

    def get_entities(self, application_mats):
        """
        지원 자료 특성 추출

        :param application_mats: 지원자료 원본 데이터
        """

        # LLM 모델 초기화
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0
        )

        # 지원 자료 추출
        if application_mats:
            resume = application_mats['resume_text']
            cover_letter = application_mats['cover_letter_text']
            portfolio = application_mats['popol_text']

        else:
            return "지원 자료 데이터가 존재하지 않습니다."

        # 프롬프트 정의
        prompt = ChatPromptTemplate.from_template(
            """
            당신은 문서를 분석해 특징을 추출하는 AI 문서 분석기입니다. 
            아래의 [이력서], [자기소개서], [포트폴리오]를 분석해 명시된 [특징]을 [출력 규칙]에 따라 추출해주세요.

            ### [특징]:
            1. 주요 직무 키워드 (예: 데이터 분석, 백엔드 개발, AI 모델링)
            2. 산업군/도메인 (예: IT, 제조업, 생산업)
            3. 기술, 스킬
            4. 최종 학력, 경력 여부
            5. 진행 했던 프로젝트 경험 내용 전체

            ### [출력 규칙]:
            1. 직무 키워드:
            2. 산업군/도메인:
            3. 기술/스킬:
            4. 학력/경력:
            5. 프로젝트 경험: 줄바꿈 없이 출력하세요.

            ### [이력서]:
            {resume}

            ### [자기소개서]:
            {cover_letter}

            ### [포트폴리오]:
            {portfolio}
            """
        )

        output_parser = StrOutputParser()

        # 체인 생성
        chain = prompt | llm | output_parser
        
        # invoke 호출
        response = chain.invoke({
            "resume": resume,
            "cover_letter": cover_letter,
            "portfolio": portfolio
        })

        result = response.split('\n')

        # print(keyword)

        return result

# if __name__ == '__main__':
#     ex_entities = ExtractEntities()

#     appli_mats = ex_entities.get_application_mats_from_db('interview2')
#     entities = ex_entities.get_entities(appli_mats)

#     # 특징 분류
#     # job_code = entities[0]
#     # domain = entities[1]
#     # skill = entities[2]
#     # career = entities[3]
#     # place = entities[4]

#     # job_code = re.sub(r"[^\w\s]", "", job_code)
#     print(entities)


