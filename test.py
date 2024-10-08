from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

import time
import json
def current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def add_url_to_list(urls_json, new_url):
    # 將 JSON 字串解析為 Python 列表
    urls_list = json.loads(urls_json)

    # 檢查該 URL 是否已存在於列表中
    if new_url not in urls_list:
        urls_list.append(new_url)  # 如果不存在，則推入新 URL
        print("URL added:", new_url)
    else:
        print("URL already exists:", new_url)

    # 將更新後的列表轉換回 JSON 字串
    updated_json_array_str = json.dumps(urls_list, ensure_ascii=False)
    
    return updated_json_array_str

def mongo(url, title,activity, coupon, price):
    client = MongoClient()
    db = client.website
    website = db.yahoo
    
    # Prepare the new product details
    product_details = {
        'url': url,
        'title': title.strip(),
        'activity': activity.strip(),
        'coupon': coupon.strip(),
        'price': price.strip(),
        'update_time': current_time(),
        'insert_time': current_time()
    }

    # Step 1: Check if a document with the same url, title and coupon exists
    existing_document = website.find_one({'url': product_details['url'], 'title': product_details['title'], 'activity': product_details['activity'], 'coupon': product_details['coupon'], 'price': product_details['price']})
    
    # Step 2: If a matching document is found, return without inserting
    if existing_document:
        # Update the update_time only
        updated_document = website.find_one_and_update(
            {'url': product_details['url'], 
             'title': product_details['title'], 
             'activity': product_details['activity'],
             'coupon': product_details['coupon'],
             'price': product_details['price']},  # Match by all fields
            {'$set': {'update_time': product_details['update_time']}},  # Only update update_time
            return_document=True  # Return the updated document
        )
        print("Matching document found with same url, title, and coupon. No changes made.")
        return False, None
    
    # Step 3: Check if a document with the same url exists but with different title or coupon
    old_document = website.find_one({'url': product_details['url']})
    
    if old_document:
        # Step 4: If a document with the same url exists but with different title or coupon, update it
        updated_document = website.find_one_and_update(
            {'url': product_details['url']},  # Match by url
            {'$set': {'title': product_details['title'], 'activity': product_details['activity'], 'coupon': product_details['coupon'], 'price': product_details['price'], 'update_time': product_details['update_time']}},  # Update title and coupon
            return_document=False  # Return the document before the update
        )
        print("Document updated. Old document:", updated_document)
        return True, updated_document
    
    # Step 5: If no matching url is found, insert the new document
    result = website.insert_one(product_details)
    print("No matching url found, new document inserted with id:", result.inserted_id)
    
    return True, None

def get_urls_as_json_array():
    client = MongoClient()
    db = client.website
    website = db.yahoo

    # Step 1: 查詢所有文檔的 url 欄位
    urls_cursor = website.find({}, {'url': 1})  # 僅選擇 url 欄位

    # Step 2: 將查詢結果轉換為 list，並提取出 url
    urls = [doc['url'] for doc in urls_cursor if 'url' in doc]

    # Step 3: 將 url 列表轉換為 JSON 陣列
    urls_json_array = json.dumps(urls, ensure_ascii=False)  # 設定 ensure_ascii=False 以支持非 ASCII 字符

    return urls_json_array

# 使用函數並打印結果
urls_json = get_urls_as_json_array()
print(urls_json)


def get_element_by_classname(driver,classname):
    # 使用多行 JavaScript 代码
    script = """
        var elArray = [];
        var tmp = document.getElementsByTagName("*");
        var regex = new RegExp(arguments[0]);
        for ( var i = 0; i < tmp.length; i++ ) {
            if ( regex.test(tmp[i].className) ) {
                elArray.push(tmp[i]);
            }
        }
        if(elArray.length > 0)
            return elArray[0].innerText;
        else
            return "";
    """

    # 执行脚本并返回结果
    price = driver.execute_script(script,classname)
    return price
def update_price():
    # 指定 chrome-headless-shell.exe 的路径
    chrome_path = '..\\chrome-headless-shell-win64-128\\chrome-headless-shell.exe'
    chromedriver_path = "..\\chromedriver128.exe"

    # 设置无头模式
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = chrome_path  # 指定 Chrome 可执行文件路径


    # 启动 Chrome
    service = Service(executable_path=chromedriver_path)  # 不需要传入 ChromeDriver，使用 webdriver-manager 会自动处理
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920,1080)

    try:
        # 獲取 url 的 get_urls_as_json_arrayN 陣列
        urls_json = get_urls_as_json_array()
        # 將 JSON 字串解析為 Python 列表
        urls_list = json.loads(urls_json)
        urls_list.append("https://tw.buy.yahoo.com/gdsale/gdsale.asp?gdid=10356273");

        # 使用 for 循環遍歷 url 列表
        for url in urls_list:
            # 访问网页

            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))  # 等待页面的 body 元素加载完成
            )



            title = get_element_by_classname(driver,"HeroInfo__title___")
            activity = get_element_by_classname(driver,"ActivityInfo__wrapper")
            coupon = get_element_by_classname(driver,"CouponInfo__couponContainer")
            price = get_element_by_classname(driver,"mainPrice")
            # 打印元素的文本内容
            print(f"Title: {title}")
            print(f"activity: {activity}")
            print(f"coupon: {coupon}")
            print(f"price: {price}")
            old_data = mongo(url,title,activity,coupon,price)
            print(old_data)

            content = driver.page_source
            driver.save_screenshot("screenshot.png")
    finally:
        driver.quit()
