from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import os

driver = webdriver.Chrome()
search_query = "cafe near Đà Nẵng"
driver.get("https://www.google.com/maps")
time.sleep(3)

# Nhập tìm kiếm
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys(search_query)
search_box.send_keys(Keys.ENTER)
time.sleep(5)

# Cuộn xuống để load thêm kết quả
for _ in range(3):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

# Lấy HTML
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")

# Parse kết quả
results = soup.find_all('div', class_='Nv2PK')  # lớp div này chứa từng địa điểm, tùy Google update mà có thể đổi
print(f"Tìm thấy {len(results)} kết quả")

data = []

for r in results:
    try:
        name = r.find('a', class_='hfpxzc').get_text() if r.find('a', class_='hfpxzc') else 'N/A'
        address = r.find('div', class_='rllt__details').get_text() if r.find('div', class_='rllt__details') else 'N/A'
        rating_tag = r.find('span', class_='MW4etd')
        rating = rating_tag.get_text() if rating_tag else 'N/A'
        link_tag = r.find('a', class_='hfpxzc')
        link = "https://www.google.com" + link_tag['href'] if link_tag else 'N/A'

        item = {
            "name": name,
            "address": address,
            "rating": rating,
            "link": link
        }
        data.append(item)
    except Exception as e:
        print(f"❌ Lỗi khi parse 1 kết quả: {e}")

driver.quit()
# Tạo thư mục data nếu chưa tồn tại
os.makedirs("data", exist_ok=True)
# Lưu ra file JSON
with open("data/cafe_list.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Đã lưu dữ liệu vào data/cafe_list.json")
