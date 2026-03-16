import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DIR = "chroma_db"   # folder for storing vector database

def load_pdf(pdf_path):
    """Loads PDF and splits into chunks."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # ~1000 symbols in chunk
        chunk_overlap=200,    # overlap to preserve context
        length_function=len
    )
    chunks = splitter.split_documents(pages)
    print(f"PDF loaded: {len(pages)} pages → {len(chunks)} chunks")
    return chunks

def build_vectorstore(chunks, api_key):
    """Creates vector database from chunks and saves to disk."""
    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print(f"Vector database created: {len(chunks)} chunks saved")
    return vectorstore

def load_vectorstore(api_key):
    """Loads existing vector database from disk."""
    embeddings = OpenAIEmbeddings(api_key=api_key)
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

def search(vectorstore, query, k=4):
    """Looks up similar chunks in vector database for a given query."""
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n---\n\n".join([d.page_content for d in docs])

def vectorstore_exists():
    """Checks if vector database already exists on disk."""
    return os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR)