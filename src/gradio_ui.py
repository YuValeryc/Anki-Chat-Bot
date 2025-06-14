# src/gradio_ui.py
import gradio as gr

# CSS giữ nguyên bố cục, chỉ thay đổi bảng màu
custom_css = """
/* Bảng màu từ hình ảnh bạn cung cấp */
:root {
    --bg-main: #f0f4f8;
    --bg-sidebar: #111827;
    --bg-chat-window: #ffffff;
    --bg-chat-bubble-user: #3b82f6;
    --bg-chat-bubble-bot: #1f2937;
    --bg-input: #ffffff;
    --text-color-sidebar: #d1d5db;
    --text-color-primary: #1f2937;
    --text-color-user-bubble: #ffffff;
    --border-color: #e5e7eb;
}

body, html {
    padding: 0;
    margin: 0;
    height: 100%;
    width: 100%;
    overflow: hidden;
}

gradio-app {
    height: 100vh !important;
    width: 100vw !important;
}

#main-container {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
    background-color: var(--bg-main);
    color: var(--text-color-primary);
}

.gradio-container {
    flex: 1;
    display: flex;
    flex-direction: row;
    overflow: hidden;
}

#sidebar {
    background-color: var(--bg-sidebar);
    padding: 16px;
    width: 250px;
    flex-shrink: 0;
    color: var(--text-color-sidebar);
    overflow-y: auto;
    border-right: 1px solid var(--border-color);
}

#chat-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    height: 100vh;
    overflow: hidden;
    background-color: var(--bg-chat-window);
    padding: 1rem;
}

#chatbot {
    flex-grow: 1;
    overflow-y: auto;
    padding-right: 0.5rem;
    min-height: 0; /* QUAN TRỌNG để không đẩy input xuống */
}
#chatbot .user, #chatbot .bot {
    border-radius: 8px;
    border: none;
    box-shadow: none;
}
#chatbot .user {
    background-color: var(--bg-chat-bubble-user);
    color: var(--text-color-user-bubble);
}
#chatbot .bot {
    background-color: var(--bg-chat-bubble-bot);
    color: var(--text-color-primary);
}

#input-container {
    display: flex;
    flex-shrink: 0; /* Ngăn bị ẩn khi thiếu chỗ */
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background-color: var(--bg-input);
    margin: 0 auto;
    max-width: 800px;
    width: 100%;
    padding: 0.5rem;
    box-sizing: border-box;
}

#input-textbox {
    flex: 1;
    background-color: transparent;
    border: none;
    box-shadow: none;
    color: var(--text-color-primary);
    font-size: 1rem;
}

#send-button {
    background-color: var(--bg-chat-bubble-user);
    color: var(--text-color-user-bubble);
    border: none;
    border-radius: 8px;
    padding: 0 16px;
    margin-left: 8px;
    height: 40px;
}
#send-button:hover {
    background-color: #2563eb;
}

#new-chat-button:hover{
    background-color: #2563eb;
}
#save-key-button {
    background-color: #22c55e;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem;
    margin-top: 0.5rem;
}
#save-key-button:hover {
    background-color: #16a34a;
}

.error { color: #ef4444; }
.success { color: #22c55e; }

@media screen and (max-width: 1024px) {
    #sidebar {
        width: 200px;
    }
    #input-container {
        max-width: 95%;
    }
}
"""

# HÀM create_modern_interface VÀ CÁC THÀNH PHẦN BÊN TRONG GIỮ NGUYÊN 100%
def create_modern_interface(save_key_fn, user_fn, bot_fn):
    """Tạo giao diện giống ChatGPT với ô nhập API Key."""
    
    with gr.Blocks(theme="soft", css=custom_css, elem_id="main-container", title="Anki Chat Bot") as interface:
        # State để lưu RAG chain cho mỗi phiên người dùng
        session_state = gr.State({})

        with gr.Row(equal_height=True):
            with gr.Column(scale=1, min_width=250, elem_id="sidebar"):
                gr.Markdown("<h1 style='color: white;'>Anki RAG Bot</h1>")
                
                # --- PHẦN THÊM VÀO ---
                with gr.Column():
                    api_key_textbox = gr.Textbox(
                        label="Google Gemini API Key",
                        placeholder="Dán API Key của bạn vào đây...",
                        type="password", lines=1, elem_id="api-key-textbox"
                    )
                    save_key_button = gr.Button("Lưu & Kích hoạt Key", elem_id="save-key-button")
                    status_display = gr.Markdown("<p style='color: orange;'>Vui lòng nhập API Key để bắt đầu.</p>")
                
                gr.Markdown("<hr style='border-color: #374151;'>")
                new_chat_btn = gr.Button("+ Đoạn chat mới", elem_id="new-chat-button")

            with gr.Column(scale=4, elem_id="chat-container"):
                chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    type='messages',
                    container=False,
                    show_label=False,
                    avatar_images=(None, "http://127.0.0.1:8000/assets/images/chatbot.png"),
                    bubble_full_width=False,
                )
                
                with gr.Row(elem_id="input-container"):
                    textbox = gr.Textbox(
                        show_label=False,
                        placeholder="Hỏi bất cứ điều gì về Anki...",
                        container=False, scale=7, elem_id="input-textbox"
                    )
                    send_btn = gr.Button("⬆️", scale=1, elem_id="send-button")

        # --- ĐỊNH NGHĨA HÀNH VI MỚI ---
        save_key_button.click(
            fn=save_key_fn,
            inputs=[api_key_textbox, session_state],
            outputs=[status_display, session_state]
        )

        send_btn.click(
            fn=user_fn, inputs=[textbox, chatbot], outputs=[chatbot, textbox]
        ).then(
            fn=bot_fn, inputs=[chatbot, session_state], outputs=[chatbot]
        )
        
        textbox.submit(
            fn=user_fn, inputs=[textbox, chatbot], outputs=[chatbot, textbox]
        ).then(
            fn=bot_fn, inputs=[chatbot, session_state], outputs=[chatbot]
        )

        new_chat_btn.click(lambda: [], None, [chatbot])
        
    return interface