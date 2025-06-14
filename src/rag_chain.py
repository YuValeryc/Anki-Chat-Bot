# src/rag_chain.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from src.config import EMBEDDING_MODEL, LLM_MODEL, GOOGLE_API_KEY # Import các hằng số

# --- Prompt để tạo câu trả lời cuối cùng từ tài liệu ---
QA_PROMPT_TEMPLATE = """Bạn là một trợ lý AI hữu ích chuyên về Anki. Nhiệm vụ của bạn là trả lời câu hỏi của người dùng dựa trên ngữ cảnh được cung cấp.
Hãy trả lời câu hỏi một cách chi tiết, chính xác và thân thiện bằng tiếng Việt.
Sử dụng các tài liệu được cung cấp trong phần "NGỮ CẢNH" để trả lời.
Sau khi trả lời, hãy trích dẫn nguồn mà bạn đã sử dụng.

Nếu bạn không tìm thấy câu trả lời trong ngữ cảnh, hoặc câu hỏi không liên quan đến Anki, hãy trả lời một cách lịch sự rằng bạn không biết, ví dụ: "Tôi xin lỗi, kiến thức của tôi chỉ giới hạn trong các tài liệu về Anki. Tôi không thể trả lời câu hỏi này." Đừng cố bịa ra câu trả lời.

NGỮ CẢNH:
{context}

CÂU HỎI:
{question}

TRẢ LỜI:
"""
QA_PROMPT = PromptTemplate(
    template=QA_PROMPT_TEMPLATE, input_variables=["context", "question"]
)

def load_vector_store():
    """Tải FAISS index từ đĩa. Cần một API key để tạo model embedding."""
    if not os.path.exists("data/vectorstore"):
        raise FileNotFoundError("Thư mục 'data/vectorstore' không tồn tại. Vui lòng chạy script 'run_preprocessing.py' trước.")
    
    print("Đang tải FAISS index từ bộ nhớ...")
    # Dùng key từ .env chỉ cho việc tải embedding này
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=GOOGLE_API_KEY)
    vector_store = FAISS.load_local("data/vectorstore", embeddings, allow_dangerous_deserialization=True)
    print("Tải FAISS index thành công.")
    return vector_store

# SỬA ĐỔI: Hàm này bây giờ nhận api_key làm tham số
def create_conversational_rag_chain(api_key: str):
    """
    Tạo một Conversational RAG chain với API key được người dùng cung cấp.
    """
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 6, 'fetch_k': 20}
    )
    
    # Sử dụng api_key được truyền vào để tạo LLM
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL, 
        google_api_key=api_key, # Dùng key được truyền vào
        temperature=0.3,
        top_p=0.8,
        top_k=40,
        convert_system_message_to_human=True, 
    )
    
    conversational_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
        verbose=False
    )
    
    return conversational_chain