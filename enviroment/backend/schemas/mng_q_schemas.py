from pydantic import BaseModel

class MngQuestionSchema(BaseModel):
    company_nm:str
    job_nm:str
    experience:str
