import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from prompt.prompts import ev_score_rule, ev_total_list

load_dotenv()

# --------- DIRECTORY PATH SETTING ----------
# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect


def get_all_reviews(user_id):
    """
    면접 평가 데이터 로드 - 평가기준별 피드백, 총평 전체

    :param user_id: 면접자 ID
    """

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

    # interview_id 로 질문별 피드백, 총평 전체 가져오기
    # ques_step를 내림차순 정렬하여 null이 아닌 데이터 10개 추출
    select_answer_query = """
    SELECT *
    FROM (
        SELECT ques_step, answer_logic, q_comp, job_exp, hab_chk, time_mgmt, answer_all_review
        FROM interview_result
        WHERE interview_id = 99 and answer_all_review is not null
        ORDER BY ques_step DESC
        LIMIT 10
    ) AS sub
    ORDER BY ques_step ASC;
    """

    reviews = pdb.select_all_vars(select_answer_query, interview_id)

    return reviews

def total_report(reviews):
    """
    종합 레포트 생성

    """

    llm = ChatOpenAI(
        model='gpt-4o-2024-08-06',
        temperature=0
    )

    if reviews:
        # 논리성
        answer_logic = [review['answer_logic'] for review in reviews]
        # 질문 이해도
        q_comp = [review['q_comp'] for review in reviews]
        # 직무 전문성
        job_exp = [review['job_exp'] for review in reviews]
        # 습관체크
        hab_chk = [review['hab_chk'] for review in reviews]
        # 시간 활용력
        time_mgmt = [review['time_mgmt'] for review in reviews]
        # 총평
        answer_all_review = [review['answer_all_review'] for review in reviews]

        answer_logic = "\n\n".join(answer_logic)
        q_comp = "\n\n".join(q_comp)
        job_exp = "\n\n".join(job_exp)
        hab_chk = "\n\n".join(hab_chk)
        time_mgmt = "\n\n".join(time_mgmt)

        answer_all_review = "\n\n".join(answer_all_review)

    else:
        return "평가 데이터가 존재하지 않습니다."

    prompt = ChatPromptTemplate.from_template(
        """
        당신은 AI 면접 평가자입니다.
        아래 10개 면접 질문에 대한 [평가 총평]과 [평가 기준별 피드백]을 기반으로 **종합적인 면접 평가 리포트**를 작성해야 합니다.
        아래의 평가 목적과 평가 방식에 따라 리포트를 작성하고, 출력 형식에 맞춰 출력하세요. 

        ## 평가 목적:
        - 면접자의 전체적인 답변 성향과 강약점을 파악하여
        - 각 평가 기준별 **점수화**와 **요약 피드백**을 제공합니다.

        ## 평가 방식:
        - [평가 총평]을 기반으로 [평가 항목 및 기준]에 따라 점수화하고, 종합적으로 평가하여 총평을 간단한 문장으로 작성 하세요.
        - [평가 기준별 피드백]을 항목별로 요약해 요약 피드백을 간결하게 작성하세요. 
        - 요약 피드백 작성 시, 면접자가 자신의 약점을 파악할 수 있도록 작성하세요.
        - 이해하기 쉬운 문장으로 작성하고, 친절하고 부드러운 말투로 작성하세요.

        ---

        [평가 총평]
        {answer_all_review}

        [평가 기준별 피드백]
        1. 논리성: 
        {answer_logic}
        2. 질문 이해도:
        {q_comp}
        3. 직무 전문성:
        {job_exp}
        4. 표현 습관:
        {hab_chk}
        5. 시간 활용력:
        {time_mgmt}

        ---

        [평가 항목 및 기준]
        - 평가 기준:
        {ev_score_rule}

        - 평가 항목:
        {ev_total_list}

        ---

        [출력 형식 예시]
        다음 형식의 JSON으로 응답해주세요:
        용어의 의미를 참고해서 알맞게 출력해주세요.
        - answer_all_review: 총평
        - score: 점수
        - qs_relevance: 질문 적합성
        - clarity: 논리성과 구체성
        - job_relevance: 직무 연관성
        - answer_logic : 논리성
        - q_comp : 질문 이해도
        - job_exp : 직무 전문성
        - hab_chk : 표현 습관
        - time_mgmt : 시간 활용력

        {{
            "answer_all_review": "면접자는 전반적으로 명확하고 논리적인 답변을 전달하려 노력했으며, 일부 질문에서 직무 연관성이 부족한 점이 보였지만, 팀워크와 학습 태도는 긍정적으로 드러났습니다. 특정 질문에서 반복적으로 질문 요지를 벗어난 부분은 개선이 필요합니다.",
            "score": {{
                "qs_relevance": 83,
                "clarity": 78,
                "job_relevance": 70
            }},
            "answer_logic": "...",
            "q_comp": "...",
            "job_exp": "...",
            "hab_chk": "...",
            "time_mgmt": "..."
        }}
        """
    )
    output_parser = JsonOutputParser()

    chain = prompt | llm | output_parser

    response = chain.invoke({
        "answer_all_review": answer_all_review,
        "answer_logic": answer_logic,
        "q_comp": q_comp,
        "job_exp": job_exp,
        "hab_chk": hab_chk,
        "time_mgmt": time_mgmt,
        "ev_score_rule": ev_score_rule,
        "ev_total_list": ev_total_list
    })

    return response


# if __name__ == '__main__':
#     reviews = get_all_reviews('interview')
#     feedbacks = total_report(reviews)

#     print(feedbacks)

    
