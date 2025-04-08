import pdfplumber
from db_util.db_utils import post_db_connect

# DB Connect
pdb = post_db_connect()
    
# 이력서 파싱
path = "./data/빅데이터AI_이력서.pdf"
doc = pdfplumber.open(path).pages
resume_text = "\n".join([page.extract_text() for page in doc])
print(resume_text)

# 자소서 파싱
path = "./data/빅데이터AI_자기소개서.pdf"
doc = pdfplumber.open(path).pages
cover_letter_text= "\n".join([page.extract_text() for page in doc])
print(cover_letter_text)

# 포트폴리오 파싱
path = "./data/빅데이터AI_포트폴리오.pdf"
doc = pdfplumber.open(path).pages
popol_text= "\n".join([page.extract_text() for page in doc])
print(popol_text)

# DB Insert
user_id = 'interview'

def insert_data(user_id, resume_text, cover_letter_text, popol_text):
    insert_query = """
    INSERT INTO resume_popol_history (user_id, resume_text, cover_letter_text, popol_text)
    VALUES (%s, %s, %s, %s);
    """
    pdb.insert_many_vars(insert_query, conditions=(user_id, resume_text, cover_letter_text, popol_text))


# insert 실행
insert_data(user_id, resume_text, cover_letter_text, popol_text)
    