from src.data_loader import load_docs_from_directory, split_documents
from src.embedding import create_and_save_vector_store

def main():
    """Chạy toàn bộ quy trình tiền xử lý dữ liệu."""
    # 1. Tải và trích xuất metadata từ file
    docs = load_docs_from_directory()
    
    # 2. Chia nhỏ tài liệu
    split_docs = split_documents(docs)
    
    # 3. Tạo và lưu vector store
    create_and_save_vector_store(split_docs)

if __name__ == "__main__":
    print("--- Bắt đầu quá trình tiền xử lý dữ liệu từ file local ---")
    main()
    print("--- Hoàn tất quá trình tiền xử lý! ---")