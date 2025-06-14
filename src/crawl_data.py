import requests
from bs4 import BeautifulSoup
import time
import os
import re
from urllib.parse import urlparse, urljoin

# --- CẤU HÌNH ---
TARGET_SITES = [
    {
        'name': 'Anki Manual',
        'toc_url': 'https://docs.ankiweb.net/toc.html',
        'base_url': 'https://docs.ankiweb.net/',
        'output_dir': 'data/raw/anki_manual_docs'
    },
    {
        'name': 'Anki FAQs',
        'toc_url': 'https://faqs.ankiweb.net/toc.html',
        'base_url': 'https://faqs.ankiweb.net/',
        'output_dir': 'data/raw/anki_faqs_docs'
    }
]

# --- CÁC HÀM CRAWL VÀ TIỀN XỬ LÝ ---

def preprocess_content(text):
    """
    Hàm tiền xử lý nội dung văn bản để làm sạch cho RAG.
    """
    # 1. Thay thế nhiều dòng trống liên tiếp bằng một dòng trống duy nhất
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    lines = text.split('\n')
    processed_lines = []
    
    # 2. Nối các dòng bị ngắt không tự nhiên
    # Logic: Nếu một dòng không kết thúc bằng dấu câu hoặc không phải là một mục trong danh sách (list item)
    # thì có khả năng nó là một phần của câu trước đó.
    # Đây là một heuristic đơn giản nhưng hiệu quả.
    for i in range(len(lines)):
        current_line = lines[i].strip()
        if not current_line:
            # Giữ lại các dòng trống để phân tách đoạn văn
            if processed_lines and processed_lines[-1] != "":
                processed_lines.append("")
            continue
            
        # Kiểm tra xem dòng trước đó có nên được nối với dòng hiện tại không
        if (i > 0 and 
            processed_lines and 
            processed_lines[-1] and 
            # Dòng trước không kết thúc bằng dấu câu phổ biến
            not processed_lines[-1].endswith(('.', ':', '?', '!', ')', '>', '`')) and
            # Dòng trước không phải là một tiêu đề (heuristic: không kết thúc bằng #)
            not processed_lines[-1].strip().endswith('#') and
            # Dòng hiện tại bắt đầu bằng chữ thường (dấu hiệu của một câu tiếp diễn)
            current_line[0].islower()):
            
            # Nối dòng
            processed_lines[-1] += ' ' + current_line
        else:
            processed_lines.append(current_line)
            
    # Nối lại các dòng đã xử lý thành một chuỗi duy nhất
    return '\n'.join(processed_lines)


def fetch_toc_links(toc_url, base_url):
    # ... (Hàm này giữ nguyên như cũ)
    print(f"Đang truy cập mục lục tĩnh: {toc_url}")
    try:
        response = requests.get(toc_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href and href.endswith('.html') and not href.startswith(('http://', 'https://')):
                full_url = urljoin(base_url, href)
                title = a_tag.get_text(" ", strip=True).replace("❱", "").strip()
                links.append({'title': title, 'url': full_url})
        
        unique_links = list({link['url']: link for link in links}.values())
        print(f"=> Đã tìm thấy {len(unique_links)} liên kết hợp lệ từ mục lục.")
        return unique_links
        
    except requests.exceptions.RequestException as e:
        print(f"[LỖI] Không thể tải mục lục tĩnh: {e}")
        return None

def crawl_page_content(url):
    # ... (Hàm này giữ nguyên như cũ)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        main_content = BeautifulSoup(response.content, 'lxml').find('main')
        if main_content:
            # Lấy văn bản thô
            raw_text = main_content.get_text(separator='\n', strip=True)
            # **GỌI HÀM TIỀN XỬ LÝ Ở ĐÂY**
            processed_text = preprocess_content(raw_text)
            return processed_text
        else:
            print(f"  [CẢNH BÁO] Không tìm thấy thẻ <main> trong URL: {url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  [LỖI] Không thể truy cập trang {url}: {e}")
        return None

def process_site(config):
    # ... (Hàm này giữ nguyên như cũ, chỉ gọi các hàm đã cập nhật)
    name, toc_url, base_url, output_dir = config['name'], config['toc_url'], config['base_url'], config['output_dir']
    
    print(f"\n{'='*50}")
    print(f"BẮT ĐẦU XỬ LÝ: {name.upper()}")
    print(f"{'='*50}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Đã tạo thư mục: '{os.path.abspath(output_dir)}'")

    links_to_crawl = fetch_toc_links(toc_url, base_url)
    if not links_to_crawl:
        print(f"Không lấy được link nào cho trang '{name}'. Bỏ qua...")
        return

    success_count, fail_count = 0, 0

    for i, link_info in enumerate(links_to_crawl):
        url, title = link_info['url'], link_info['title']
        print(f"\n[{i+1}/{len(links_to_crawl)}] Đang xử lý: {title}")
        print(f"  URL: {url}")
        
        content = crawl_page_content(url) # Hàm này giờ đã bao gồm tiền xử lý
        if content:
            base_filename = os.path.basename(urlparse(url).path)
            safe_filename = "".join([c for c in base_filename if c.isalpha() or c.isdigit() or c in ('.', '_', '-')]).rstrip()
            txt_filename = os.path.splitext(safe_filename)[0] + '.txt'
            filepath = os.path.join(output_dir, txt_filename)
            
            file_content = f"Source URL: {url}\nTitle: {title}\n----------------------------------------\n\n{content}"
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                print(f"  => Đã lưu thành công vào: {filepath}")
                success_count += 1
            except IOError as e:
                print(f"  [LỖI] Không thể ghi file {filepath}: {e}")
                fail_count += 1
        else:
            fail_count += 1
        time.sleep(0.5)

    print("\n----------------------------------------")
    print(f"HOÀN TẤT XỬ LÝ TRANG: {name}")
    print(f"Tổng số tệp đã lưu thành công: {success_count}")
    print(f"Tổng số tệp bị lỗi: {fail_count}")

def main():
    for site_config in TARGET_SITES:
        process_site(site_config)
    
    print(f"\n{'*'*50}")
    print("TOÀN BỘ QUÁ TRÌNH CRAWL VÀ TIỀN XỬ LÝ ĐÃ HOÀN TẤT!")
    print(f"{'*'*50}")

if __name__ == '__main__':
    main()