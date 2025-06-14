# src/rag_chain.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from src.embedding import load_vector_store
from src.config import GOOGLE_API_KEY, LLM_MODEL

# --- Prompt để cô đọng câu hỏi ---
# Prompt này giúp LLM biến câu hỏi mới và lịch sử thành một câu hỏi độc lập.
# Chúng ta sẽ dùng prompt mặc định của LangChain vì nó khá tốt.
# Nếu muốn tùy chỉnh, bạn có thể tạo một PromptTemplate ở đây.

# --- Prompt để tạo câu trả lời cuối cùng từ tài liệu ---
# Đây là phần chúng ta cần tinh chỉnh.
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

def create_conversational_rag_chain():
    """
    Tạo một Conversational RAG chain có khả năng sử dụng lịch sử chat.
    """
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 6, 'fetch_k': 20}
    )
    
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL, 
        google_api_key=GOOGLE_API_KEY, 
        temperature=0.3
    )
    
    conversational_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        # Sử dụng prompt tùy chỉnh của chúng ta để tạo câu trả lời cuối cùng
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
        verbose=False
    )
    
    return conversational_chain