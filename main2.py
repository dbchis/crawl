from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import os

def crawl_google_maps_detail(query="cafe near Đà Nẵng"):
    driver = webdriver.Chrome()
    driver.get("https://www.google.com/maps")
    time.sleep(3)

    # Nhập từ khoá tìm kiếm
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    # Lấy HTML sau khi load
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    data = {}

    # Tên quán
    title_tag = soup.find('h1', class_='DUwDvf')
    data['name'] = title_tag.get_text(strip=True) if title_tag else 'N/A'

    # Rating
    rating_tag = soup.find('span', class_='ceNzKf')
    data['rating'] = rating_tag.get('aria-label') if rating_tag else 'N/A'

    # Số lượng đánh giá
    review_tag = soup.find('span', attrs={'aria-label': lambda x: x and 'bài đánh giá' in x})
    data['reviews'] = review_tag.get('aria-label') if review_tag else 'N/A'

    # Địa chỉ
    address_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Địa chỉ:')})
    if address_button:
        address_div = address_button.find('div', class_='Io6YTe')
        data['address'] = address_div.get_text(strip=True) if address_div else 'N/A'
    else:
        data['address'] = 'N/A'

    # Số điện thoại
    phone_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Số điện thoại:')})
    if phone_button:
        phone_div = phone_button.find('div', class_='Io6YTe')
        data['phone'] = phone_div.get_text(strip=True) if phone_div else 'N/A'
    else:
        data['phone'] = 'N/A'

    # Ảnh đại diện
    img_tag = soup.find('button', class_='aoRNLd').find('img') if soup.find('button', class_='aoRNLd') else None
    data['thumbnail'] = img_tag['src'] if img_tag else 'N/A'

    # Giờ mở cửa (dòng trạng thái)
    status_tag = soup.find('span', class_='ZDu9vd')
    data['open_status'] = status_tag.get_text(strip=True) if status_tag else 'N/A'

    # Tạo thư mục data nếu chưa có
    os.makedirs('data', exist_ok=True)

    # Lưu ra file JSON
    with open('data/detail.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('✅ Đã lưu dữ liệu chi tiết vào data/detail.json')
    driver.quit()

if __name__ == "__main__":
    crawl_google_maps_detail()
