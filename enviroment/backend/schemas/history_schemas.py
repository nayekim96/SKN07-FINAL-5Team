from pydantic import BaseModel

class HisBoardSchema(BaseModel):
    user_id:str 
    page_num:int
