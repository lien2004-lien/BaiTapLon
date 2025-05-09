import time
import datetime
import pandas as pd
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_article_details(driver, url):
    try:
        driver.get(url)
        time.sleep(2)
        description, image_url, content = "", "", ""

        try:
            
            description = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute('content')
        except:
            pass
        try:
            
            image_url = driver.find_element(By.XPATH, "//meta[@property='og:image']").get_attribute('content')
        except:
            pass
        try:
           
            paragraphs = driver.find_elements(By.XPATH, "//div[contains(@class,'content')]/p")
            content = "\n".join([p.text for p in paragraphs if p.text.strip()])
        except:
            pass

        return description, image_url, content
    except:
        return "", "", ""


def scrape_selected_category():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    base_url = "https://baomoi.com"
    driver.get(base_url)
    print("🖱️ Hãy nhấp vào một danh mục (VD: Thế giới, Công nghệ...) trên trang chủ.")
    time.sleep(10)

    category_url = driver.current_url
    if category_url == base_url or "video" in category_url or "tin-moi" in category_url:
        print("\n⚠️ Bạn chưa chọn đúng danh mục cụ thể. Vui lòng chọn lại!")
        driver.quit()
        return

    category_name = category_url.strip("/").split("/")[-1]
    print(f"\n✅ Bạn đã chọn danh mục: {category_name}")
    print(f"🔗 URL: {category_url}")

    all_data = []
    page_number = 1
    seen_links = set()
    while True:
        url = category_url if page_number == 1 else f"{category_url}/trang{page_number}.epi"
        print(f"🔍 Đang lấy trang {page_number}: {url}")
        driver.get(url)
        time.sleep(2)

        articles = driver.find_elements(By.XPATH, "//h3/a[@href]")
        if not articles:
            print("⛔ Hết trang hoặc không có bài viết.")
            break

        for article in articles:
            try:
                title = article.text.strip()
                link = article.get_attribute("href")

                if not title or not link:
                    continue

                description, image_url, content = get_article_details(driver, link)

                all_data.append({
                    "Tiêu đề": title,
                    "Mô tả": description,
                    "Hình ảnh": image_url,
                    "Nội dung": content,
                    "Link": link
                })
            except:
                continue

        page_number += 1

    driver.quit()

    if all_data:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"baomoi_{category_name}_{today}.csv"
        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n📁 Đã lưu dữ liệu vào: {filename}")
    else:
        print("\n⚠️ Không có dữ liệu để lưu.")

def job():
    print("🕐 Chạy vào lúc: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    scrape_selected_category()

if __name__ == "__main__":
    schedule.every().day.at("06:00").do(job)
    print("Đang chờ đến 6:00 sáng mỗi ngày..")

while True:
    schedule.run_pending()
    time.sleep(60)
