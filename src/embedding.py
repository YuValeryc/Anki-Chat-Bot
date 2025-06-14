import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import GOOGLE_API_KEY, EMBEDDING_MODEL, VECTOR_STORE_PATH

def create_and_save_vector_store(split_docs):
    """Tạo vector store từ các document đã chia nhỏ và lưu vào đĩa."""
    if not os.path.exists(VECTOR_STORE_PATH):
        os.makedirs(VECTOR_STORE_PATH)
        
    print("Đang tạo embeddings và xây dựng FAISS index...")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=GOOGLE_API_KEY)
    vector_store = FAISS.from_documents(split_docs, embeddings)
    
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Vector store đã được lưu thành công tại: {VECTOR_STORE_PATH}")

def load_vector_store():
    """Tải FAISS index từ đĩa."""
    if not os.path.exists(VECTOR_STORE_PATH):
        raise FileNotFoundError(f"Thư mục vector store không tồn tại tại: {VECTOR_STORE_PATH}.")
        
    print("Đang tải FAISS index từ bộ nhớ...")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=GOOGLE_API_KEY)
    vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    print("Tải FAISS index thành công.")
    return vector_store