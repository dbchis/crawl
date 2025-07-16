from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import os

def crawl_list(query, scroll_times=3, wait_time=2):
    driver = webdriver.Chrome()
    driver.get("https://www.google.com/maps")
    time.sleep(4)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(6)  # tăng thời gian load lần đầu

    # Cuộn để load thêm kết quả
    for _ in range(scroll_times):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(wait_time)

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

            rating_tag = r.find('span', class_='MW4etd')
            rating = rating_tag.get_text(strip=True) if rating_tag else 'N/A'

            address_tag = r.find('div', class_='rllt__details')
            address = address_tag.get_text(strip=True) if address_tag else 'N/A'

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

# def crawl_detail(link):
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(6)  # tăng thời gian load chi tiết

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Lấy địa chỉ chi tiết
    address = 'N/A'
    address_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Địa chỉ:')})
    if address_button:
        address_div = address_button.find('div', class_='Io6YTe')
        address = address_div.get_text(strip=True) if address_div else 'N/A'

    # Lấy số điện thoại
    phone = 'N/A'
    phone_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Số điện thoại:')})
    if phone_button:
        phone_div = phone_button.find('div', class_='Io6YTe')
        phone = phone_div.get_text(strip=True) if phone_div else 'N/A'

    # Lấy thumbnail
    thumbnail = 'N/A'
    img_tag = soup.find('button', class_='aoRNLd')
    if img_tag:
        img = img_tag.find('img')
        if img:
            thumbnail = img.get('src', 'N/A')

    driver.quit()

    return {
        "address_detail": address,
        "phone": phone,
        "thumbnail": thumbnail
    }
def crawl_detail(link):
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(6)  # đủ thời gian load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Địa chỉ chi tiết
    address = 'N/A'
    address_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Address:')})
    if address_button:
        address_div = address_button.find('div', class_='Io6YTe')
        address = address_div.get_text(strip=True) if address_div else 'N/A'

    # Số điện thoại
    phone = 'N/A'
    phone_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Phone:')})
    if phone_button:
        phone_div = phone_button.find('div', class_='Io6YTe')
        phone = phone_div.get_text(strip=True) if phone_div else 'N/A'

    # Website
    website = 'N/A'
    website_link = soup.find('a', attrs={'aria-label': lambda x: x and x.startswith('Website:')})
    if website_link:
        website = website_link.get('href', 'N/A')

    # Plus code
    plus_code = 'N/A'
    plus_button = soup.find('button', attrs={'aria-label': lambda x: x and x.startswith('Plus code:')})
    if plus_button:
        plus_div = plus_button.find('div', class_='Io6YTe')
        plus_code = plus_div.get_text(strip=True) if plus_div else 'N/A'

    # Price range
    price_range = 'N/A'
    price_div = soup.find('div', string=lambda x: x and 'per person' in x)
    if price_div:
        price_range = price_div.get_text(strip=True)

    # Open hours: table
    open_hours = {}
    try:
        table = soup.find('table', class_='eK4R0e')
        if table:
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    day = cols[0].get_text(strip=True)
                    hours = cols[1].get_text(strip=True)
                    open_hours[day] = hours
    except Exception as e:
        print(f"⚠️ Lỗi lấy giờ mở cửa: {e}")

    driver.quit()

    return {
        "address_detail": address,
        "phone": phone,
        "website": website,
        "plus_code": plus_code,
        "price_range": price_range,
        "open_hours": open_hours
    }

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    while True:
        query = input("🔎 Nhập từ khoá tìm kiếm (0 để thoát): ").strip()
        if query == "0":
            print("👋 Kết thúc!")
            break

        print(f"🚀 Đang crawl danh sách quán: {query}")
        items = crawl_list(query)

        # Tiếp tục vào từng link để crawl chi tiết
        for i, item in enumerate(items):
            if item["link"] != 'N/A':
                print(f"➡️ [{i+1}/{len(items)}] Lấy chi tiết: {item['name']}")
                detail = crawl_detail(item["link"])
                item.update(detail)
            else:
                print(f"⚠️ Bỏ qua quán không có link: {item['name']}")

        # Lưu file
        filename = query.replace(' ', '_') + ".json"
        filepath = os.path.join("data", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        print(f"✅ Đã lưu kết quả chi tiết vào {filepath}")
