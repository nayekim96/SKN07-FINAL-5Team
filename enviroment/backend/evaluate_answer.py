import os
import sys
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

# --------- DIRECTORY PATH SETTING ----------
# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect


# ------- 면접 데이터 로드 (질문, 답변, 권장답변, 답변시간) -------
pdb = post_db_connect()

# interview_process 테이블에서 가장 최근 interview id를 가져와야 함
select_query = f"""
SELECT 
"""


# ------- 평가지표 세팅 -------


# ------- 답변 평가 LLM Agent -------