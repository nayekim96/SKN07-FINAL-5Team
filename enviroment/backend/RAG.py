from typing import Union
from fastapi import FastAPI, status, File, UploadFile
from pydantic import BaseModel
import os
import fitz
import pandas as pd
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnableMap
from langchain_core.output_parsers import StrOutputParser
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import ElasticsearchStore
from langchain.retrievers import EnsembleRetriever
from s3_util import download_pdf_as_bytes
import uuid

from s3_util import get_latest_file_key
from pdf_util import extract_text_from_pdf


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ELASTICSEARCH_HOST_PORT = os.getenv("ELASTICSEARCH_HOST_PORT")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

app = FastAPI()

latest_key = get_latest_file_key()
if latest_key:
    st.info(f"최신 파일: {latest_key}")
    pdf_bytes = download_pdf_as_bytes(latest_key)
    text = extract_text_from_pdf(pdf_bytes)


# chroma DB 설정
chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(allow_reset=True, anonymized_telemetry=False)
)
collection = chroma_client.get_collection(name=COLLECTION_NAME)

chroma_db = Chroma(
    collection_name="job_position",
    embedding_function=embeddings,
    client=chroma_client
)

# Elasticsearch 연결 설정
es_client = Elasticsearch(ELASTICSEARCH_HOST_PORT, basic_auth=(USER, PASSWORD))

elasticsearch_store = ElasticsearchStore(
    es_connection=es_client,
    index_name="job_position",
    embedding=embeddings,
)

# 리트리버 만들기
chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
es_retriever = elasticsearch_store.as_retriever(search_kwargs={"k": 5})

hybrid_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, es_retriever],
    weights=[0.7, 0.3],
)

prompt = PromptTemplate.from_template(
    """
    당신은 인재매칭 AI 어시스턴트입니다. 사용자 이력서에 기반하여 채용공고를 5개 추천해주세요.

    - 반드시 이력서에 기반할 것.
    - 출력 시 채용공고의 양식을 사용할 것.
    - 출력 시 지역은 상세하게 출력 할 것.
    - 채용공고 추천 이유를 한줄로 설명할 것.
    - 같은 공고 번호가 중복될 경우 단 1개만 추천할 것.
    - 채용공고 전체 내용을 기반하여 분석할 것. 제목만 보고 판단하지 말 것.
    - page_content의 전체 텍스트를 기준으로 판단할 것.

    #이력서:
    {question}
    #채용공고:
    {context}

    #출력형태
    - 기업명, 공고명, [경력]
    - 직무, 지역
    """
)

llm = ChatOpenAI(model_name="gpt-4o", temperature=0.8)

hybrid_chain = (
    {"context": hybrid_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

@app.post("/recommend_jobs")
async def recommend_jobs(file: UploadFile = File(...)):
    """
    이력서 PDF 파일을 업로드 받아 채용 공고를 추천합니다.
    """
    try:
        resume_text = ""
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)
        doc = fitz.open("temp.pdf")
        for page in doc:
            resume_text += page.get_text()
        doc.close()
        os.remove("temp.pdf")

        response = hybrid_chain.invoke(resume_text)
        return {"recommendations": response}
    except Exception as e:
        return {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

file = fitz.open()    

if file:
    try:
        resume = fitz.open()
    except:
        pass