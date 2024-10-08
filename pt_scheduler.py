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

import pt_config
import pt_db
import pt_bot
import time
import json
import random
import os

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



def handle_selenium_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TimeoutException as timeout_err:
            print(f"Timeout occurred while loading page: {timeout_err}")
        except NoSuchElementException as no_elem_err:
            print(f"Element not found: {no_elem_err}")
        except WebDriverException as driver_err:
            print(f"WebDriver error occurred: {driver_err}")
        except ConnectionError as conn_err:
            print(f"Network connection error occurred: {conn_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
    return wrapper






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
def take_screenshot(driver, file_name):
    """保存当前页面截图"""
    screenshots_dir = 'screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)  # 创建文件夹存放截图

    file_path = os.path.join(screenshots_dir, f"{file_name}.png")
    driver.save_screenshot(file_path)
    print(f"截图已保存到: {file_path}")
@handle_selenium_errors
def fetch_product_attributes(urls_list = None,user_id = None):
    chromedriver_executable_path = pt_config.CHROMEDRIVER_EXECUTABLE_PATH

    # 设置无头模式
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    # 指定 Chrome 可执行文件路径
    chrome_options.binary_location = pt_config.CHROME_BINARY_PATH


    # 启动 Chrome
    service = Service(executable_path=chromedriver_executable_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920,1080)

    try:
        if urls_list is None:
            # 獲取 url 的 retrieve_urls_as_json_arrayN 陣列
            urls_json = pt_db.retrieve_urls_as_json_array()
            # 將 JSON 字串解析為 Python 列表
            urls_list = json.loads(urls_json)

        # 使用 for 循環遍歷 url 列表
        total = len(urls_list)
        count = 0
        for url in urls_list:
            
            count+=1
            try:
                # 访问网页
                print(f"{count}/{total}")
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))  # 等待页面的 body 元素加载完成
                )



                title = get_element_by_classname(driver,"HeroInfo__title___")
                activity = get_element_by_classname(driver,"ActivityInfo__wrapper")
                coupon = get_element_by_classname(driver,"CouponInfo__couponContainer")
                price = get_element_by_classname(driver,"mainPrice")
                
                if len(title) > 0 and len(price) > 0 :
                    result , product_data , old_document,current_time   = pt_db.update_goods_to_database(user_id,url,title,activity,coupon,price)
                    
                    if result is True and product_data is not None:
                        take_screenshot(driver, f"{product_data['title'].replace('/', '_')}_{current_time.strftime('%Y-%m-%d_%H_%M_%S')}")

                    print(result)
                    print(product_data)
                    print(old_document)
                    print(current_time)

                    
                time.sleep(random.randint(3, 10))
            except Exception as e:
                # 处理当前 URL 的异常
                print(f"处理 {url} 时发生错误: {e}")
                continue  # 继续处理下一个 URL
    except Exception as e:
        # 捕获其他异常
        print(f"总体处理时发生错误: {e}")

    finally:
        driver.quit()
def telegram_alert_on_db_update():
    notifications = pt_db.retrieve_last_notification_time()
    # 使用範例
    specific_time = notifications['yahoo']  # 替換為你想要的時間點
    print(specific_time)       # 輸出 Python 列表（JSON 陣列）
    records, records_json = pt_db.retrieve_updates_after_time(specific_time)
    msg = "%s\n目前價格為%s\n折扣碼：%s\n活動：%s\n\n前次紀錄價格為%s\n折扣碼：%s\n活動：%s\n\n%s"
    for record in records:
        format_msg = msg % (
            record['title'],
            record['price'],
            record['coupon'],
            record['activity'],
            record['price_before'],
            record['coupon_before'],
            record['activity_before'],
            record['url']
        )
        pt_bot.send(format_msg,record['user_id'])
    pt_db.update_last_notification_time('yahoo')