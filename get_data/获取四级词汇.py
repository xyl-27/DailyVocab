import requests
from bs4 import BeautifulSoup
import json
user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 Edg/126.0.0.0'
header = {"User-Agent":user_agent,}
url = "https://www.eol.cn/html/en/cetwords/cet4.shtml"
response = requests.get(url,headers=header)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
# 提取所有单词
word_dict = {}
for div in soup.find_all('div', class_='wordBox'):
    k = div.find('h1').text
    words = []
    for p in div.find_all('p'):
        words.append(p.text.strip())
    word_dict[k] = words
# 保存单词
with open('words.json', 'w', encoding='utf-8') as file:
    json.dump(word_dict, file, ensure_ascii=False, indent=4)
with open('words.txt', 'w', encoding='utf-8') as file:
    file.write("\n".join(sum(word_dict.values(),[])))