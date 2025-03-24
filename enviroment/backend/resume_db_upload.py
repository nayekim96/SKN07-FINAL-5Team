import os
import openai
import chromadb
import fitz  # PDF에서 텍스트 추출
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URL = os.getenv("DATABASE_URL")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# 데이터베이스 설정
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 이력서, 자기소개서, 포트폴리오 저장 테이블 모델 정의
class ResumePopolHistory(Base):
    __tablename__ = "resume_popol_history"
    user_id = Column(String(20), primary_key=True, index=True)
    resume = Column(String(20))
    resume_text = Column(Text)
    cover_letter = Column(String(20))
    cover_letter_text = Column(Text)
    popol = Column(String(20))
    popol_text = Column(Text)
    insert_date = Column(TIMESTAMP, default=datetime.utcnow)

# ChromaDB 초기화
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="resume_embeddings")

# FastAPI 앱 초기화
app = FastAPI()

# PDF에서 텍스트 추출하는 함수
def extract_text_from_pdf(pdf_file: bytes) -> str:
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

# OpenAI Embedding 생성 함수
def get_embedding(text: str):
    openai.api_key = OPENAI_API_KEY
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response["data"][0]["embedding"]

# 파일 처리 함수 (이력서, 자기소개서, 포트폴리오 처리)
def process_files(user_id: str, resume_bytes: bytes = None, cover_letter_bytes: bytes = None, popol_bytes: bytes = None):
    db = SessionLocal()
    
    resume_text = extract_text_from_pdf(resume_bytes) if resume_bytes else ""
    cover_letter_text = extract_text_from_pdf(cover_letter_bytes) if cover_letter_bytes else ""
    popol_text = extract_text_from_pdf(popol_bytes) if popol_bytes else ""
    
    resume_entry = ResumePopolHistory(
        user_id=user_id,
        resume="resume.pdf" if resume_bytes else None,
        resume_text=resume_text,
        cover_letter="cover_letter.pdf" if cover_letter_bytes else None,
        cover_letter_text=cover_letter_text,
        popol="popol.pdf" if popol_bytes else None,
        popol_text=popol_text,
    )
    
    db.add(resume_entry)
    db.commit()
    db.refresh(resume_entry)
    db.close()
    
    # 임베딩 저장 (이력서만 저장)
    if resume_text:
        embedding = get_embedding(resume_text)
        collection.add(
            documents=[resume_text],
            embeddings=[embedding],
            ids=[str(resume_entry.user_id)]
        )
    
    return {"message": "파일 처리 완료", "user_id": user_id}

# 파일 업로드 API 엔드포인트
@app.post("/upload_files")
async def upload_files(user_id: str, resume: UploadFile = None, cover_letter: UploadFile = None, popol: UploadFile = None):
    resume_bytes = await resume.read() if resume else None
    cover_letter_bytes = await cover_letter.read() if cover_letter else None
    popol_bytes = await popol.read() if popol else None
    
    return process_files(user_id, resume_bytes, cover_letter_bytes, popol_bytes)