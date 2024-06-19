import json
import os
import random
import pandas as pd
import re
import requests
import selenium
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 Edg/126.0.0.0'
header = {"User-Agent": user_agent, }
url = "https://zhenti.burningvocabulary.cn/cet4"
response = requests.get(url, headers=header)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
html_content = str(soup)
pattern = re.compile(r'<a class="link-primary" href="([^"]+)"')
urls = pattern.findall(html_content)

root = r"https://zhenti.burningvocabulary.com"
for url in urls[-1]:
    info = {}
    pdf_url = root + url
    driver = webdriver.Edge()
    driver.get(pdf_url)
    time.sleep(random.randint(1, 5)/10)
    download_button = driver.find_element(By.ID, "download")
    if "下载" in download_button.get_attribute('innerHTML'):
        download_button.click()
        time.sleep(random.randint(1, 5) / 20)
        try:
            answer_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@title="查答案"]')))
            answer_btn.click()
            time.sleep(random.randint(1, 5) / 20)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            answer_cells = soup.find_all('td', class_='aws')
            if answer_cells:
                answers = {cell['data-index']: cell['data-ans'] for cell in answer_cells}
                info["answers"] = answers
                print(url,"已全部下载")
            else:
                print(url, "找不到具体答案")
        except Exception as e:
            print(url,"没有答案")
    else:
        print(url, "无法下载")
    with open(f'../data/cet4/{url.replace("/","_")}.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)

time.sleep(10)