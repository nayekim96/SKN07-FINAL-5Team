from pydantic import BaseModel

class ItvProcessSchema(BaseModel):
    user_id:str
    question_list:list
    company_cd:str
    job_cd:int
    experience:str


class ItvResultProcessSchema(BaseModel):
    interview_id:str
    question_list:list
    answer_list:list
    video_path:str


