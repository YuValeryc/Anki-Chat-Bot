import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# --- API Key ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Không tìm thấy GOOGLE_API_KEY. Hãy tạo file .env và điền key.")

# --- Paths ---
# Giả định script được chạy từ thư mục gốc của dự án
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(ROOT_DIR, "data", "raw")
VECTOR_STORE_PATH = os.path.join(ROOT_DIR, "data", "vectorstore")

# --- Model Configs ---
EMBEDDING_MODEL = "models/embedding-001"
LLM_MODEL = "gemini-2.0-flash"