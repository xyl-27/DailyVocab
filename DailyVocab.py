from flask import Flask, jsonify, request, send_from_directory

from flask_cors import CORS
import json
import os
import random
from pathlib import Path

app = Flask(__name__)
CORS(app)

CURR_DIR = Path(__file__).resolve().parent

WORDS_FILE = CURR_DIR / 'data' / 'sorted_words.txt'
PROGRESS_FILE = CURR_DIR / 'data' / 'progress.json'
ARCHIVE_FILE = CURR_DIR / 'data' / 'archive.json'
BATCH_SIZE = 20


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
        save_progress(self.progress)

    def learn_random(self):
        available_words = [word for word in self.progress["remaining"] if word not in self.archive]
        daily_words = random.sample(available_words, min(self.batch_size, len(available_words)))
        self.update_progress(daily_words)
        save_progress(self.progress)
        return daily_words

    def learn_sequential(self):
        available_words = [word for word in self.progress["remaining"] if word not in self.archive]
        daily_words = available_words[:self.batch_size]
        self.update_progress(daily_words)
        save_progress(self.progress)
        return daily_words

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

@app.route('/learn/random', methods=['GET'])
def learn_random():
    daily_words = learner.learn_random()
    return jsonify({
        'daily_words': daily_words,
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })

@app.route('/learn/sequential', methods=['GET'])
def learn_sequential():
    daily_words = learner.learn_sequential()
    return jsonify({
        'daily_words': daily_words,
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })


@app.route('/reset', methods=['POST'])
def reset():
    learner.reset_progress()
    return jsonify({
        'message': '学习进度已重置！',
        'learned_count': len(learner.progress["learned"]),
        'remaining_count': len(learner.progress["remaining"]),
        'archive_count': len(learner.archive)
    })


@app.route('/archive', methods=['POST'])
def archive():
    data = request.get_json()
    word = data.get("word")
    learner.archive_word(word)
    return jsonify({
        'message': f'单词 "{word}" 归档状态已切换！',
        'archive_count': len(learner.archive)
    })


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
