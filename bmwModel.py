#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Howard_Lee

import json
import gzip
from fake_useragent import UserAgent
from jsonsearch import JsonSearch
import pprint
import aiohttp
import asyncio
from seleniumwire import webdriver

from yikogd.myProxy import get_myHttpProxy, get_myHttpsProxy

# 設定Partslink24的域名
partslink24Domain = 'https://www.partslink24.com/'


# 使用seleniumwire取得Partslink24中BMW之所有車型
def getPartslink24_modelPath():
    # 定義BMW車型資料的URL
    BMW_url = 'https://www.partslink24.com/p5bmw/extern/vehicle/models?lang=zh-TW&serviceName=bmw_parts&upds=2023-07-13--12-55&_=1690957890577'

    # 創建UserAgent物件，用於隨機產生假的User-Agent，以模擬不同瀏覽器訪問
    ua = UserAgent()

    # 自建的開源簡易型IP Proxy Pool
    options = {
        'proxy': {
            "http:": f"http://{get_myHttpProxy()}",
            "https:": f"https://{get_myHttpsProxy()}"
        }
    }
    # 初始化一個使用seleniumwire的WebDriver物件，使用Chrome瀏覽器驅動
    driver = webdriver.Chrome(seleniumwire_options=options)

    # 設置WebDriver的User-Agent
    driver.header_overrides = {
        "User-Agent": ua.firefox
    }

    # 使用WebDriver打開BMW車型資料的URL
    driver.get(BMW_url)

    # 獲取響應資料的內容
    response_data = driver.last_request.response.body

    # 使用gzip解壓縮響應資料
    response_data = gzip.decompress(response_data)

    # 將解壓縮後的響應資料轉換成JSON資料
    jsondata = JsonSearch(object=json.loads(response_data))

    # 使用jsonsearch庫來獲取所有車型的路徑
    all_model = [partslink24Domain + x for x in jsondata.search_all_value(key='path')]

    # 關閉WebDriver
    driver.quit()

    return all_model


# 定義一個非同步函數，用於從URL獲取資料
async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.read()


# 定義一個非同步函數，用於從多個URL同時獲取資料
async def fetch_all_data(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        return await asyncio.gather(*tasks)


# 定義主函數
async def main():
    # 非同步取得所有URL的內容
    data_list = await fetch_all_data(getPartslink24_modelPath())

    # 印出BMW品牌下第一個車型的資料
    pprint.pprint(json.loads(data_list[0]))

    # 將取得的內容合併成一個list，並將bytes資料轉換為字串，然後逐個輸出
    merged_data = []
    for data in data_list:
        merged_data.append(data)
    for item in merged_data:
        # 在這裡將bytes轉換為字串
        print(item.decode('utf-8'))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
