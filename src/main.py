# src/main.py
import gradio as gr
import fastapi
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os

from src.rag_chain import create_conversational_rag_chain 
from src.gradio_ui import create_modern_interface

# --- 1. KHỞI TẠO CÁC THÀNH PHẦN (giữ nguyên) ---
print("Đang khởi tạo Conversational RAG chain...")
try:
    rag_chain = create_conversational_rag_chain()
    print("Khởi tạo Conversational RAG chain thành công.")
except FileNotFoundError as e:
    print(f"LỖI: {e}\nVui lòng chạy 'python run_preprocessing.py' trước.")
    exit()

# --- 2. ĐỊNH NGHĨA CÁC HÀM XỬ LÝ MỚI ---
def add_user_message(message: str, history: list):
    """Bước 1: Thêm tin nhắn người dùng vào lịch sử."""
    if not message or not message.strip():
        return history, ""
    history.append({"role": "user", "content": message})
    return history, ""

def get_bot_response(history: list):
    """
    Bước 2: Gọi chain, xử lý nguồn và thêm câu trả lời của bot.
    """
    if not history or history[-1]["role"] != "user":
        return history

    user_message = history[-1]["content"]
    past_conversations = history[:-1]
    
    formatted_history = []
    for i in range(0, len(past_conversations), 2):
        if i + 1 < len(past_conversations):
            user_msg = past_conversations[i]['content']
            bot_msg = past_conversations[i+1]['content']
            formatted_history.append((user_msg, bot_msg))
            
    print(f"Đang gọi chain với câu hỏi: '{user_message}'")
    
    result = rag_chain.invoke({
        "question": user_message,
        "chat_history": formatted_history
    })
    
    # --- SỬA LỖI Ở ĐÂY: THÊM LẠI LOGIC XỬ LÝ NGUỒN ---
    answer = result.get('answer', 'Xin lỗi, tôi gặp sự cố khi tạo câu trả lời.')
    source_documents = result.get('source_documents', [])
    
    if source_documents:
        unique_sources = set()
        for doc in source_documents:
            source_url = doc.metadata.get('source')
            if source_url:
                unique_sources.add(source_url)
        
        if unique_sources:
            # Tạo chuỗi Markdown để hiển thị link nguồn
            source_str = "\n\n---\n**Nguồn tham khảo:**\n"
            for src in sorted(list(unique_sources)):
                source_str += f"- [{src}]({src})\n"
            
            # Ghép chuỗi nguồn vào cuối câu trả lời
            answer += source_str

    print(f"Câu trả lời cuối cùng (bao gồm nguồn): {answer}")
    
    # Thêm câu trả lời HOÀN CHỈNH (đã có nguồn) vào lịch sử
    history.append({"role": "assistant", "content": answer})
    
    return history

# --- 3. TẠO API VÀ PHỤC VỤ FILE TĨNH ---
app = fastapi.FastAPI(
    title="Anki RAG Chatbot API (Stateless)",
    version="1.0.0"
)

# Đảm bảo phần này tồn tại và đúng
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_path = os.path.join(BASE_DIR, "assets")

app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

class QueryRequest(BaseModel):
    question: str
@app.post("/ask", summary="Đặt câu hỏi cho chatbot")
def ask_question_api(request: QueryRequest):
    result = rag_chain.invoke({"question": request.question, "chat_history": []})
    return {"answer": result['answer']}

# --- 4. TẠO VÀ TÍCH HỢP GIAO DIỆN GRADIO ---
gradio_app = create_modern_interface(add_user_message, get_bot_response)
app = gr.mount_gradio_app(app, gradio_app, path="/")

# --- 5. CHẠY APP ---
if __name__ == "__main__":
    print("Khởi chạy máy chủ...")
    print("Giao diện Web: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)