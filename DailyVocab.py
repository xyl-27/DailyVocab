from flask import Flask, jsonify, request, send_from_directory
import logging
from flask_cors import CORS
import json
import os
import random
from pathlib import Path


CURR_DIR = Path(__file__).resolve().parent
WORDS_FILE = CURR_DIR / 'data' / 'words.txt'
PROGRESS_FILE = CURR_DIR / 'data' / 'progress.json'
ARCHIVE_FILE = CURR_DIR / 'data' / 'archive.json'
BATCH_SIZE = 20



app = Flask(__name__)

CORS(app)



class ColoredConsoleHandler(logging.StreamHandler):
    COLORS = {
        'DEBUG': '\033[0;36m',  # Cyan
        'INFO': '\033[0m',  # White
        'WARNING': '\033[0;33m',  # Yellow
        'ERROR': '\033[0;31m',  # Red
        'CRITICAL': '\033[0;35m'  # Purple
    }
    RESET = '\033[0m'

    def emit(self, record):
        try:
            message = self.format(record)
            self.stream.write(self.COLORS[record.levelname] + message + self.RESET + '\n')
            self.flush()
        except Exception:
            self.handleError(record)


# 配置日志记录器
logger = logging.getLogger(__name__)
handler = ColoredConsoleHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)





def load_words():
    with open(WORDS_FILE, 'r', encoding='utf-8') as file:
        return file.read().splitlines()


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {"learned": [], "remaining": load_words()}


def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []


def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as file:
        json.dump(progress, file, ensure_ascii=False, indent=4)


def save_archive(archive):
    with open(ARCHIVE_FILE, 'w', encoding='utf-8') as file:
        json.dump(archive, file, ensure_ascii=False, indent=4)


class Learner:
    def __init__(self):
        self.words = load_words()
        self.progress = load_progress()
        self.archive = load_archive()
        self.batch_size = BATCH_SIZE
        self.pointer = 0

    def update_progress(self, daily_words):
        remaining_words = self.progress["remaining"]
        if not remaining_words:
            words = load_words()
            remaining_words.extend(words)
        self.progress["learned"].extend(daily_words)
        for word in daily_words:
            remaining_words.remove(word)
        self.progress["remaining"] = remaining_words

    def reset_progress(self):
        all_words = load_words()
        remaining_words = [word for word in all_words if word not in self.archive]
        self.progress = {"learned": [], "remaining": remaining_words}
        self.pointer = 0
        save_progress(self.progress)

    def generate_words(self, random_order=False):
        available_words = [word for word in self.progress["remaining"] if word not in self.archive]
        if random_order:
            daily_words = random.sample(available_words, min(self.batch_size, len(available_words)))
        else:
            daily_words = available_words[self.pointer:self.pointer + self.batch_size]
            self.pointer += self.batch_size
        return daily_words

    def toggle_word_status(self, word):
        word_status = self.get_word_status(word)
        if word_status == "learned":
            self.progress["learned"].remove(word)
            self.archive.append(word)
        elif word_status == "archived":
            self.archive.remove(word)
            self.progress["remaining"].append(word)
        else:
            self.progress["remaining"].remove(word)
            self.progress["learned"].append(word)
        save_progress(self.progress)
        save_archive(self.archive)

    def get_word_status(self, word):
        if word in self.progress["learned"]:
            return "learned"
        elif word in self.archive:
            return "archived"
        else:
            return "remaining"

    def archive_word(self, word):
        if word in self.archive:
            self.archive.remove(word)
            self.progress["remaining"].append(word)
        else:
            self.archive.append(word)
            if word in self.progress["remaining"]:
                self.progress["remaining"].remove(word)
            if word in self.progress["learned"]:
                self.progress["learned"].remove(word)
        save_progress(self.progress)
        save_archive(self.archive)


learner = Learner()


@app.route('/generate/random', methods=['GET'])
def generate_random():
    daily_words = learner.generate_words(random_order=True)
    logger.debug('生成乱序单词')
    return jsonify({
        'daily_words': daily_words,
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })


@app.route('/generate/sequential', methods=['GET'])
def generate_sequential():
    daily_words = learner.generate_words(random_order=False)
    logger.debug('生成顺序单词')
    return jsonify({
        'daily_words': daily_words,
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })


@app.route('/reset', methods=['POST'])
def reset():
    learner.reset_progress()
    logger.debug('学习进度已重置')
    return jsonify({
        'message': '学习进度已重置！',
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })


@app.route('/toggle-status', methods=['POST'])
def toggle_status():
    data = request.get_json()
    word = data.get("word")
    learner.toggle_word_status(word)
    status = learner.get_word_status(word)
    logger.debug(f'单词"{word}"状态已切换为{status}')
    return jsonify({
        'message': f'单词 "{word}" 状态已切换！',
        'status': status,
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# 初始化函数，用于在应用启动时加载单词列表
def initialize_app():
    global learner
    with app.app_context():
        # 调用生成随机单词列表的函数或路由
        daily_words = learner.generate_words(random_order=True)
        # 构建响应数据
        response_data = {
            'daily_words': daily_words,
            'learned_count': len(learner.progress["learned"]),
            'remaining_count': len(learner.progress["remaining"]),
            'archive_count': len(learner.archive)
        }
        # 返回 JSON 响应
        return jsonify(response_data)
if __name__ == '__main__':
    app.run(debug=False)
