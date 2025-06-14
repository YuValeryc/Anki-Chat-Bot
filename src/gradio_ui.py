# src/gradio_ui.py
import gradio as gr

# CSS giữ nguyên bố cục, chỉ thay đổi bảng màu
custom_css = """
/* Bảng màu từ hình ảnh bạn cung cấp */
:root {
    --bg-main: #f0f4f8;             /* Màu nền xám nhạt bên ngoài cùng */
    --bg-sidebar: #111827;          /* Màu nền sidebar xanh đen */
    --bg-chat-window: #ffffff;      /* Màu nền cửa sổ chat trắng */
    --bg-chat-bubble-user: #3b82f6;  /* Màu bong bóng chat của người dùng, xanh dương */
    --bg-chat-bubble-bot: #1f2937;   /* Màu bong bóng chat của bot, xám nhạt */
    --bg-input: #ffffff;            /* Màu nền của ô input */
    --text-color-sidebar: #d1d5db;   /* Màu chữ trên sidebar */
    --text-color-primary: #1f2937;   /* Màu chữ chính (đen) */
    --text-color-user-bubble: #ffffff; /* Màu chữ trong bong bóng user */
    --border-color: #e5e7eb;
}


/* --- Các style được cập nhật màu sắc --- */
body {
    padding: 0 !important;
    margin: 0 !important;
}
gradio-app {
    height: 100vh !important;
    overflow: hidden;
}
#main-container {
    background-color: var(--bg-main) !important; /* Đổi màu nền chính */
    color: var(--text-color-primary) !important;
    height: 100%;
    width: 100%;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
}
.gradio-container {
    background-color: transparent !important;
}

#sidebar {
    background-color: var(--bg-sidebar) !important; /* Đổi màu sidebar */
    padding: 8px;
    height: 100%;
    min-height: 100vh;
    border-right: 1px solid var(--border-color) !important; /* Đổi màu đường viền */
}
#new-chat-button {
    background-color: var(--bg-chat-bubble-user) !important; /* Đổi màu nút */
    color: var(--text-color-user-bubble) !important;
    border: none !important;
}
#new-chat-button:hover {
    background-color: #2563eb !important; /* Màu hover đậm hơn */
}

#chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1rem;
    background-color: var(--bg-chat-window) !important; /* Đổi màu nền cửa sổ chat */
}
#chatbot {
    flex-grow: 1;
    overflow-y: auto !important;
    background-color: transparent !important; /* Chatbot trong suốt trên nền trắng */
}
#chatbot .user, #chatbot .bot {
    border-radius: 8px;
    border: none;
    box-shadow: none;
}
#chatbot .user {
    background-color: var(--bg-chat-bubble-user) !important; /* Đổi màu bong bóng user */
    color: var(--text-color-user-bubble) !important;
}
#chatbot .bot {
     background-color: var(--bg-chat-bubble-bot) !important; /* Đổi màu bong bóng bot */
     color: var(--text-color-primary) !important;
}

#input-container {
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important; /* Đổi màu viền input */
    background-color: var(--bg-input) !important; /* Đổi màu nền input */
    margin: 0 auto;
    max-width: 768px;
    width: 100%;
    padding: 0.5rem;
}
#input-textbox {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-color-primary) !important;
}

#send-button {
    background-color: var(--bg-chat-bubble-user) !important; /* Đổi màu nút gửi */
    color: var(--text-color-user-bubble) !important;
    border: none !important;
    min-width: 40px !important;
    border-radius: 8px !important;
}
#send-button:hover {
    background-color: #2563eb !important;
}
"""

# HÀM create_modern_interface VÀ CÁC THÀNH PHẦN BÊN TRONG GIỮ NGUYÊN 100%
# NHƯ FILE BAN ĐẦU BẠN GỬI
def create_modern_interface(user_fn, bot_fn):
    """Tạo giao diện hiện đại giống ChatGPT bằng gr.Blocks."""
    
    with gr.Blocks(theme="soft", css=custom_css, elem_id="main-container") as interface:
        with gr.Row():
            with gr.Column(scale=1, elem_id="sidebar"):
                new_chat_btn = gr.Button("+ Đoạn chat mới", elem_id="new-chat-button")

            with gr.Column(scale=4, elem_id="chat-container"):
                chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    label="Anki RAG Chatbot",
                    avatar_images=(None, "http://127.0.0.1:8000/assets/images/chatbot.png"),
                    bubble_full_width=False,
                    type='messages',
                    show_label=False,
                    container=False,
                    height=120
                )
                
                with gr.Row(elem_id="input-container"):
                    textbox = gr.Textbox(
                        show_label=False,
                        placeholder="Hỏi bất cứ điều gì về Anki...",
                        container=False,
                        scale=7,
                        elem_id="input-textbox"
                    )
                    send_btn = gr.Button("⬆️", scale=1, elem_id="send-button")

        # --- ĐỊNH NGHĨA CHUỖI SỰ KIỆN ---
        action_event = send_btn.click(
            fn=user_fn,
            inputs=[textbox, chatbot],
            outputs=[chatbot, textbox]
        ).then(
            fn=bot_fn,
            inputs=chatbot,
            outputs=chatbot
        )
        
        submit_event = textbox.submit(
            fn=user_fn,
            inputs=[textbox, chatbot],
            outputs=[chatbot, textbox]
        ).then(
            fn=bot_fn,
            inputs=chatbot,
            outputs=chatbot
        )

        # Xử lý nút "Đoạn chat mới"
        new_chat_btn.click(lambda: [], None, [chatbot])
        
    return interface