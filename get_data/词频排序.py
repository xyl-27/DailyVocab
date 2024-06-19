import string
from collections import OrderedDict
import json
import re
from collections import defaultdict
import os
from pdfminer.high_level import extract_text

text_ls = []
for file in os.listdir("../data/cet4/"):
    if file.endswith(".pdf"):
        text = extract_text(f"../data/cet4/{file}")
        text_ls.append(text)
long_text = " ".join(text_ls)

# 将文本转换为小写sxuua
long_text = long_text.lower()
# 将文本转换为小写
long_text = long_text.lower()
# 去除所有非单词字符（包括标点符号和中文字符）
cleaned_text = re.sub(r'[^a-z\s]', '', long_text)
# 去除单个字符（保留完整单词）
cleaned_text = re.sub(r'\b\w\b', '', cleaned_text)
# 按空格分割单词
words = cleaned_text.split()

# 使用字典统计单词数量
word_count = defaultdict(int)
for word in words:
    word_count[word] += 1

word_count = dict(word_count)
sorted_word_count = dict(sorted(word_count.items(), key=lambda item: item[1], reverse=True))

with open('../data/words.txt','r',encoding='utf-8') as f:
    words_txt = f.read().split('\n')

word_dict = {}

for item in words_txt:
    parts = item.split(' ', 1)
    word = parts[0].strip()  # 单词作为键
    if len(parts) > 1:
        explanation = parts[1].strip()  # 剩余部分作为值
    else:
        print(item)
        explanation = ''
    word_dict[word] = explanation

sorted_word_dict = dict(OrderedDict((word, word_dict[word]) for word in sorted_word_count.keys() if word in word_dict))
with open("../data/sorted_word_dict.json", "w", encoding="utf-8") as json_file:
    json.dump(sorted_word_dict, json_file, ensure_ascii=False, indent=4)
with open('../data/sorted_words.txt', "w", encoding="utf-8") as txt_file:
    for word, info in sorted_word_dict.items():
        txt_file.write(f"{word} {info[0]}\n")