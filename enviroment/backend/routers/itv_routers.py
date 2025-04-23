# 모의면접 Routers
from fastapi import APIRouter
from db_util.db_utils import post_db_connect
from schemas.itv_process_schemas import ItvProcessSchema, ItvResultProcessSchema 
import re
from dotenv import load_dotenv
import openai
import os
import uuid 
from datetime import datetime
from evaluate_answer import get_application_mats, evaluate_answers 
import psycopg2.extras

load_dotenv()
# OpenAI API 키 설정
openai.api_key = os.environ.get('OPENAI_API_KEY')


router = APIRouter(prefix="/itv")
common_select_text = {"선택해주세요":"None"}

@router.get('/get_company_list', status_code=200)
def get_company_list():
    connect = post_db_connect()
    result = connect.select_all("""select ccmt.common_id as common_id, 
                                          ccmt.common_nm as common_nm
                                   from company_code_master_tbl ccmt;""")
    connect.close()
    return common_select_process(result, 'common_nm', 'common_id', 'company_list')


@router.get('/get_job_list', status_code=200)
def get_job_list():
    connect = post_db_connect()
    result = connect.select_all("""select jcmt.common_id as common_id,
                                          jcmt.common_nm as common_nm
                                   from job_code_master_tbl jcmt;""")
    connect.close()
    return common_select_process(result, 'common_nm', 'common_id', 'job_list')


@router.post('/interview_start', status_code=200)
def interview_start(data: ItvProcessSchema):
    user_id = data.user_id
    question_list = data.question_list
    connect = post_db_connect()
    process_insert_query = """ insert into interview_process (user_id, company_nm  , kewdcdno, person_exp)
                       values (%s, %s, %s, %s)
                       returning interview_id;
                   """
    
    connect.cursor.execute(process_insert_query, (data.user_id, data.company_cd, data.job_cd, data.experience))
    
    interview_id = connect.cursor.fetchone()['interview_id']

    connect.db.commit()
    connect.close()

    convert_question = get_question_text_convert(question_list)
    
    parent_path = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
    now_time = datetime.now()

    
    join_path = f'data/audio/tts/{now_time.year}/{now_time.strftime("%m%d")}/'

    process_id = f'{uuid.uuid1().hex}_{interview_id}'

    root_path = os.path.join(parent_path, join_path)
    create_folder(root_path)
    create_question_tts(convert_question['q_split_list'], root_path, process_id)

    res_data = {'process_id':process_id,
                'q_list' : convert_question['q_list'],
                'audio_path' : join_path}

    return res_data


@router.post('/interview_result_process', status_code=200)
def interview_result_process(data: ItvResultProcessSchema):
    def null_and_exist_check(feedback_dict:dict, key:str):
        if key in feedback_dict:
            if feedback_dict[key] is None:
                return "null"
            else:
                return feedback_dict[key]
        else:
            return "null"
            
    status = ""        

    try:
        connect = post_db_connect()

        user_id_select_query = f""" select user_id 
                                    from interview_process
                                    where interview_id = '{data.interview_id}'
                                """
        
        user_info = connect.select_one(user_id_select_query)
        user_id = user_info['user_id'] 

        user_info_select_query = f"""with base_data as (
                                        select ip.company_nm ,
                                               ip.kewdcdno,
                                               ip.person_exp
                                        from interview_process ip 
                                        where ip.interview_id = '{data.interview_id}'
                                    ), select_company as (
                                        select bd.person_exp,
                                               bd.kewdcdno,
                                               ccmt.common_nm
                                        from base_data  as bd
                                        join  company_code_master_tbl ccmt  
                                        on cast(bd.company_nm as integer) = ccmt.common_id
                                    ), select_job as (
                                        select sc.common_nm as company_name,
                                                sc.person_exp,
                                                jcmt.common_nm as job_name
                                        from select_company as sc
                                        join job_code_master_tbl jcmt 
                                        on sc.kewdcdno = jcmt.common_id
                                    ) 
                                    select *
                                    from select_job;
                                """
        
        user_query_info = connect.select_one(user_info_select_query)

        mats = get_application_mats(user_id)
        
        question_list = data.question_list
        answer_list = data.answer_list
        user_query = [user_query_info['company_name'], user_query_info['job_name'], user_query_info['person_exp']]

        result_insert_query = f""" INSERT INTO interview_result (interview_id, ques_step, ques_text, answer_user_text, answer_example_text, answer_end_time, answer_all_review, answer_logic, q_comp, job_exp, hab_chk, time_mgmt )
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                               """
        eval_insert_list = []
        for idx, question in enumerate(question_list):
            answer = answer_list[idx]
            interview_data = { "ques_text" : question,
                               "answer_user_text" : answer,
                               "answer_end_time" : 90 
                             }

            eval_result = evaluate_answers(interview_data, mats, user_query) 
            feedback = eval_result['피드백']
            answer_logic = null_and_exist_check(feedback, '논리성')
            q_comp = null_and_exist_check(feedback, '질문 이해도')
            job_exp = null_and_exist_check(feedback, '직무 전문성')
            hab_chk = null_and_exist_check(feedback, '표현 습관')
            time_mgmt = null_and_exist_check(feedback, '시간 활용력')
            eval_data = tuple([data.interview_id, (idx+1), question, answer, eval_result['권장답변'], 90, eval_result['총평'], answer_logic, q_comp, job_exp, hab_chk, time_mgmt])
            eval_insert_list.append(eval_data)

        for result_data in eval_insert_list:
            connect.cursor.execute(result_insert_query, result_data)
        
    except Exception as e:
        print(e)
        status = "error"
    finally:
        connect.db.commit()
        connect.close()
        status = "ok"

    res_data = {"status" : status}
    return res_data


def common_select_process(select_list:dict, key:str, value: str, list_nm: str):
    select_box = common_select_text.copy()
    sum_dict = {i[key] : i[value] for i in select_list}
    select_box.update(sum_dict)
    del sum_dict
    return {list_nm: select_box, 'labels': list(select_box.keys())}

def get_question_text_convert(question: str):
    p1 = re.compile('[^0-9\.][0-9a-zA-Z가-힣\.,?]+')
    q_list = question.split('\n\n')
    q_split_list = [''.join(p1.findall(i.split('\n')[0])).lstrip() for i in q_list]
    return { 'q_list' : q_list , 'q_split_list' : q_split_list }


def create_question_tts(q_list: list, root_path:str, file_nm:str):
    client = openai.OpenAI()
   
    for idx, q in enumerate(q_list):
        response = client.audio.speech.create(
            model="tts-1",
            input=q,
            voice="alloy",
            response_format="mp3",
            speed=1.0,
        )

        file_root = f'{root_path}{file_nm}_{idx}.mp3'
        response.write_to_file(file_root)
    

def create_folder(path:str):
    if os.path.exists(path) == False:
        os.makedirs(path)

