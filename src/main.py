# src/main.py
import gradio as gr
import fastapi
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from fastapi.responses import FileResponse
import os

from src.rag_chain import create_conversational_rag_chain 
from src.gradio_ui import create_modern_interface


# --- 2. ĐỊNH NGHĨA CÁC HÀM XỬ LÝ MỚI ---
def save_key_and_init_chain(api_key: str, state: dict):
    """Lưu API Key vào state và khởi tạo RAG chain cho phiên này."""
    if not api_key or not "AIza" in api_key:
        state['rag_chain'] = None
        # SỬA LỖI: Trả về Markdown trước, sau đó là state
        return gr.Markdown("<p style='color: #F87171;'>Vui lòng nhập API Key hợp lệ. Hãy truy cập <a href='https://aistudio.google.com/apikey'>AISTUDIO</a> để lấy API key.</p>"), state
    
    print("Đã nhận API Key, bắt đầu khởi tạo RAG chain...")
    try:
        rag_chain = create_conversational_rag_chain(api_key)
        state['rag_chain'] = rag_chain
        print("Khởi tạo RAG chain thành công.")
        # SỬA LỖI: Trả về Markdown trước, sau đó là state
        return gr.Markdown("<p style='color: #34D399;'>✅ Đã lưu API Key thành công!</p>"), state
    except Exception as e:
        print(f"Lỗi khi khởi tạo RAG chain: {e}")
        state['rag_chain'] = None
        # SỬA LỖI: Trả về Markdown trước, sau đó là state
        return gr.Markdown(f"<p style='color: #F87171;'>❌ Lỗi: API Key không hợp lệ hoặc có sự cố. Hãy truy cập <a href='https://aistudio.google.com/apikey'>AISTUDIO</a> để lấy API key.</p>"), state

def add_user_message(message: str, history: list):
    """Bước 1: Thêm tin nhắn người dùng vào lịch sử."""
    if not message or not message.strip():
        return history, gr.update()
    history.append({"role": "user", "content": message})
    return history, ""

def get_bot_response(history: list, state: dict):
    """Bước 2: Gọi chain từ state và thêm câu trả lời của bot."""
    rag_chain = state.get('rag_chain')
    
    if not rag_chain:
        history.append({"role": "assistant", "content": "Vui lòng nhập và lưu API Key hợp lệ ở sidebar trước khi bắt đầu."})
        return history

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
            
    result = rag_chain.invoke({
        "question": user_message, "chat_history": formatted_history
    })
    
    answer = result.get('answer', 'Xin lỗi, tôi gặp sự cố khi tạo câu trả lời.')
    source_documents = result.get('source_documents', [])
    
    if source_documents:
        unique_sources = set()
        for doc in source_documents:
            source_url = doc.metadata.get('source')
            if source_url:
                unique_sources.add(source_url)
        
        if unique_sources:
            source_str = "\n\n---\n**Nguồn tham khảo:**\n"
            for src in sorted(list(unique_sources)):
                source_str += f"- [{src}]({src})\n"
            answer += source_str
    
    history.append({"role": "assistant", "content": answer})
    return history

# --- 3. TẠO API VÀ PHỤC VỤ FILE TĨNH ---
app = fastapi.FastAPI(
    title="Anki RAG Chatbot",
    version="1.0.0",
    favicon="http://127.0.0.1:8000/assets/favicon.ico"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(BASE_DIR, "..", "assets")
app.mount("/assets", StaticFiles(directory=assets_path), name="assets") # Sửa lại để khớp với đường dẫn ảnh

class QueryRequest(BaseModel):
    question: str
@app.post("/ask", summary="Đặt câu hỏi cho chatbot")
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(assets_path, "favicon.ico"))
def ask_question_api(request: QueryRequest):
    return {"answer": "API này cần được cập nhật để nhận API key."}

# --- 4. TẠO VÀ TÍCH HỢP GIAO DIỆN GRADIO ---
gradio_app = create_modern_interface(
    save_key_fn=save_key_and_init_chain,
    user_fn=add_user_message,
    bot_fn=get_bot_response
)
app = gr.mount_gradio_app(app, gradio_app, path="/")

# --- 5. CHẠY APP ---
if __name__ == "__main__":
    print("Khởi chạy máy chủ...")
    print("Giao diện Web: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)