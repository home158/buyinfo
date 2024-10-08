# coding: utf-8
import logging
from datetime import datetime

import pt_config
import pt_error
import json
from pymongo import MongoClient

def current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def add_goods(url):
    client = MongoClient(pt_config.DB_SERVER)
    collection = client.website.yahoo
    product_details = {
        'url': url,
        'title': "None",
        'coupon': "None",
        'price': "None",
        'update_time': "None",
        'insert_time': "None",
    }
    existing_document = collection.find_one({'url': product_details['url']})
    if existing_document:
    	return True, None
    else:
    	collection.insert_one(product_details)
    	return True, product_details
def update_goods_to_database(user_id = None, url= None, title= None,activity= None, coupon= None, price= None):
    client = MongoClient(pt_config.DB_SERVER)
    db = client.website
    website = db.yahoo
    current_time = datetime.now()
    # Prepare the new product details
    product_details = {
        'url': url,
        'title': title.strip(),
        'activity': activity.strip(),
        'coupon': coupon.strip(),
        'price': price.strip(),
        'title_before': None,
        'activity_before': None,
        'coupon_before': None,
        'price_before': None,
        'update_time': datetime.now()
    }
    # Step 1: Check if a document with the same url, title and coupon exists
    existing_document = website.find_one({'url': product_details['url'], 'title': product_details['title'], 'activity': product_details['activity'], 'coupon': product_details['coupon'], 'price': product_details['price']})
    existing_url = website.find_one({'url': product_details['url']})

    if existing_url is None:
        product_details['insert_time'] = current_time
        product_details['user_id'] = user_id
        result = website.insert_one(product_details)
        print("No matching url found, new document inserted with id:", result.inserted_id)
        return True, product_details, None, current_time

    if existing_document is None:
        old_document = website.find_one_and_update(
            {'url': product_details['url']},  # Match by url
            {'$set': {'title': product_details['title'], 'activity': product_details['activity'], 'coupon': product_details['coupon'], 'price': product_details['price'], 'update_time': current_time}},  # Update title and coupon
            return_document=False  # Return the document before the update
        )
        website.find_one_and_update(
            {'url': product_details['url']},  # Match by url
            {'$set': {'title_before': old_document['title'], 'activity_before': old_document['activity'], 'coupon_before': old_document['coupon'], 'price_before': old_document['price']}}
        )
        print("Document updated. ")
        return True, product_details, old_document, current_time

    return False, None, None, current_time
def retrieve_urls_as_json_array():
    client = MongoClient(pt_config.DB_SERVER)
    db = client.website
    website = db.yahoo

    # Step 1: 查詢所有文檔的 url 欄位
    urls_cursor = website.find({}, {'url': 1})  # 僅選擇 url 欄位

    # Step 2: 將查詢結果轉換為 list，並提取出 url
    urls = [doc['url'] for doc in urls_cursor if 'url' in doc]

    # Step 3: 將 url 列表轉換為 JSON 陣列
    urls_json_array = json.dumps(urls, ensure_ascii=False)  # 設定 ensure_ascii=False 以支持非 ASCII 字符

    return urls_json_array

def retrieve_last_notification_time():
    client = MongoClient(pt_config.DB_SERVER) 
    collection = client.website.notify  # 確保這裡的 'notify' 是正確的集合名稱

    # 查詢所有資料
    documents = collection.find()  # 這裡會取出集合中的所有文件

    # 將資料轉換為 JSON 對象
    json_object = {}
    for doc in documents:
        website = doc.get("website")
        last_notification_time = doc.get("last_notification_time")
        if website and last_notification_time:
            json_object[website] = last_notification_time


    return json_object  # 返回 JSON 對象和 JSON 字串（如果需要）
def update_last_notification_time(website):
    client = MongoClient(pt_config.DB_SERVER)
    collection = client.website.notify
    collection.find_one_and_update(
        {'website': website},
        {'$set': {'last_notification_time': datetime.now()}}
    )
    return True
def retrieve_updates_after_time(specific_time):
    # 連接到 MongoDB
    client = MongoClient(pt_config.DB_SERVER)
    collection = client.website.yahoo

    # 查詢 update_time 大於特定時間的資料
    query = {"update_time": {"$gt": specific_time}}
    
    # 執行查詢
    documents = collection.find(query)

    # 將資料轉換為列表（JSON 陣列）
    json_array = [doc for doc in documents]

    # 將列表轉換為 JSON 字串（可選）
    json_string = json.dumps(json_array, default=str)  # default=str 用於處理非可序列化的日期等資料類型

    return json_array, json_string  # 返回 JSON 陣列和 JSON 字串（如果需要）

