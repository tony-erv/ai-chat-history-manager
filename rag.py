import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DIR = "chroma_db"   # папка где хранится векторная база

def load_pdf(pdf_path):
    """Загружает PDF и разбивает на чанки."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # ~250 слов на чанк
        chunk_overlap=200,    # перекрытие — чтобы не терять контекст на границах
        length_function=len
    )
    chunks = splitter.split_documents(pages)
    print(f"PDF загружен: {len(pages)} страниц → {len(chunks)} чанков")
    return chunks

def build_vectorstore(chunks, api_key):
    """Создаёт embeddings и сохраняет векторную базу на диск."""
    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print(f"Векторная база создана: {len(chunks)} чанков сохранено")
    return vectorstore

def load_vectorstore(api_key):
    """Загружает существующую базу с диска."""
    embeddings = OpenAIEmbeddings(api_key=api_key)
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

def search(vectorstore, query, k=4):
    """Ищет k наиболее релевантных чанков по вопросу."""
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n---\n\n".join([d.page_content for d in docs])

def vectorstore_exists():
    """Проверяет есть ли уже созданная база."""
    return os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR)