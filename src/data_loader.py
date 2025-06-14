import os
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import RAW_DATA_PATH

def load_docs_from_directory():
    """
    Tải tất cả các file .txt từ thư mục data/raw và các thư mục con,
    trích xuất metadata từ 2 dòng đầu tiên.
    """
    documents = []
    print(f"Bắt đầu quét thư mục: {RAW_DATA_PATH}")
    for root, _, files in os.walk(RAW_DATA_PATH):
        for file_name in files:
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                        source_url = lines[0].replace("Source URL:", "").strip()
                        title = lines[1].replace("Title:", "").strip()
                        content = "".join(lines[3:])
                        
                        doc = Document(
                            page_content=content,
                            metadata={"source": source_url, "title": title}
                        )
                        documents.append(doc)
                except Exception as e:
                    print(f"Lỗi khi xử lý file {file_path}: {e}")
                    
    print(f"Đã tải thành công {len(documents)} tài liệu từ file local.")
    return documents

def split_documents(documents: list[Document]):
    """Chia nhỏ các tài liệu đã tải."""
    print("Đang chia nhỏ văn bản...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Đã chia thành {len(split_docs)} đoạn văn bản (chunks).")
    return split_docs