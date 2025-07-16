from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import os

def crawl_google_maps(query, scroll_times=3, wait_time=2):
    driver = webdriver.Chrome()
    driver.get("https://www.google.com/maps")
    time.sleep(3)

    # Nhập tìm kiếm
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    # Cuộn xuống để load thêm kết quả
    for _ in range(scroll_times):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(wait_time)

    # Parse HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")
    results = soup.find_all('div', class_='Nv2PK')
    print(f"🔍 Tìm thấy {len(results)} kết quả cho: {query}")

    data = []

    for r in results:
        try:
            link_tag = r.find('a', class_='hfpxzc')
            if link_tag:
                raw_name = link_tag.get('aria-label', '').strip()
                name = raw_name.split('·')[0].strip() if raw_name else 'N/A'
                link = link_tag.get('href', 'N/A')
            else:
                name = 'N/A'
                link = 'N/A'

            address_tag = r.find('div', class_='rllt__details')
            address = address_tag.get_text(strip=True) if address_tag else 'N/A'

            rating_tag = r.find('span', class_='MW4etd')
            rating = rating_tag.get_text(strip=True) if rating_tag else 'N/A'

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
    return data

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    while True:
        query = input("🔎 Nhập từ khoá tìm kiếm (hoặc nhập 0 để thoát): ").strip()
        if query == "0":
            print("👋 Kết thúc!")
            break

        print(f"🚀 Đang crawl dữ liệu cho: {query}")
        data = crawl_google_maps(query)

        # Tạo tên file từ từ khoá: thay khoảng trắng thành _
        safe_filename = query.replace(' ', '_') + ".json"
        filepath = os.path.join("data", safe_filename)

        # Lưu file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Đã lưu kết quả vào {filepath}")
