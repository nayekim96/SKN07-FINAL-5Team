import os
import sys
import pandas as pd
import chromadb
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# TextLoader를 사용하여 파일을 로드합니다.
loader = TextLoader("./data/job_opening.csv")

# 문서를 로드합니다.
documents = loader.load()

# 문자 기반으로 텍스트를 분할하는 CharacterTextSplitter를 생성합니다. 청크 크기는 300이고 청크 간 중복은 없습니다.
text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=0)

# 로드된 문서를 분할합니다.
split_docs = text_splitter.split_documents(documents)

# OpenAI 임베딩을 생성합니다.
# embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")


print(len(split_docs))

# client = chromadb.HttpClient(host='43.202.186.183', port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))

# collection = client.create_collection(name="my_collection")


# print(client.count_collections())