# 면접히스토리 Routers
import os
import sys
from fastapi import APIRouter
# --------- IMPORT CLASS FROM OTHER DIRS ----------
# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/enviroment/frontend)
main_dir = os.path.abspath(os.path.join(current_dir, ".."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from schemas.history_schemas import HisBoardSchema
from db_util.db_utils import post_db_connect 
import math


router = APIRouter(prefix="/his")
PAGE_SIZE = 10


@router.post("/get_history")
def get_history(data:HisBoardSchema):
    print(data)
    try:
        connect = post_db_connect()

        count_query = f""" SELECT count(1) as cnt
                           FROM interview_process
                           WHERE user_id = '{data.user_id}'
                       """
        total = connect.select_one(count_query)['cnt']
        
        total_page = math.trunc(total / PAGE_SIZE)

        if (total / PAGE_SIZE) > 0:
            total_page += 1

        
        page_where_query = ""

        if data.page_num == 1:
            page_where_query = """ WHERE num >= 1
                                   AND num <= 10
                               """
        else:
            page_where_query = f""" WHERE num > {(data.page_num -1) * PAGE_SIZE}
                                   AND num <= {data.page_num * PAGE_SIZE}
                               """
        print(page_where_query) 

        paging_query = f""" with base_data as (
                                select *
                                from ( select row_number() over (order by ip.insert_date desc) as num,
                                              ip.interview_id ,
                                              ip.company_nm,
                                              ip.kewdcdno,
                                              ip.insert_date,
                                              ip.person_exp
                                       from interview_process ip 
                                       where user_id = '{data.user_id}' ) as a
                                {page_where_query}
                            ), select_company as (
                                select bd.insert_date,
                                       ccmt.common_nm,
                                       bd.kewdcdno,
                                       bd.person_exp,
                                       bd.interview_id
                                from base_data  as bd
                                join  company_code_master_tbl ccmt  
                                on cast(bd.company_nm as integer) = ccmt.common_id
                            ), select_job as (
                                select sc.interview_id ,
                                       sc.common_nm as company_name,
                                       jcmt.common_nm as job_name,
                                       sc.person_exp,
                                       sc.insert_date
                                from select_company as sc
                                join job_code_master_tbl jcmt 
                                on sc.kewdcdno = jcmt.common_id
                            ) 
                            select interview_id ,
                                   company_name,
                                   job_name,
                                   person_exp,
                                   to_char(insert_date, 'YYYY.MM.DD') as insert_date
                            from select_job;
                        """
        res_data = {'history_data' : connect.select_all(paging_query),
                    'total_page' : total_page}
        return res_data
    except Exception as e:
        print(e)
    finally:
        connect.close()
    
