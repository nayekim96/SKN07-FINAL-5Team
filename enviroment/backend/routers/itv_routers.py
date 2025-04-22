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
    pass


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

