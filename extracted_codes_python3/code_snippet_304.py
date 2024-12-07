import requests
from bs4 import BeautifulSoup
import urllib.request as req
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from datetime import date
from datetime import timedelta
import time
import csv

# Google Chromeを起動
browser = webdriver.Chrome()
# Chrome find wait
browser.implicitly_wait(10)

# ページにアクセス
urlName = "https://review.kakaku.com/review/K0000661313/"
browser.get(urlName)
url = BeautifulSoup(browser.page_source, 'html.parser')
# 特定のクラスを持つすべての要素を検索
reviews = url.find_all("p", class_="revEntryCont")

x = 1
while x <= 10:
    try:
        # 要素が存在するまで待つ
        if x == 1:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div[4]/div[5]/div/div[2]/div[1]/p/a'))
            )
        else:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div[4]/div[5]/div/div[2]/div[1]/p/a[2]'))
            )
        print("Element is found")
        # 要素がクリック可能になるまで待つ
        # element = WebDriverWait(browser, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]/div/div[11]/a/span'))
        # )
        # 要素が画面内に表示されるようにスクロール
        browser.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # スクロール後に待機時間を設ける
        # JavaScript Executorを使ってクリック
        browser.execute_script("arguments[0].click();", element)
        print('click')
        x += 1
        url = BeautifulSoup(browser.page_source, 'html.parser')
        # 特定のクラスを持つすべての要素を検索
        reviews.append(url.find_all("p", class_="revEntryCont"))
    except Exception as e:
        print(f"An error occurred: {e}")
        break

time.sleep(3)
# ページのHTMLを取得
# # response = req.urlopen(urlName)
# url = BeautifulSoup(browser.page_source, 'html.parser')

# # 特定のクラスを持つすべての要素を検索
# reviews = url.find_all("p", class_="revEntryCont")

# 各トレンド記事を表示
# for review in reviews:
#     print(review.text)

with open('reviews.csv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([review.text for review in reviews])

df = pd.read_csv('reviews.csv')
print(df)

browser.quit()