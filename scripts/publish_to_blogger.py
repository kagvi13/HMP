import json
import os
import hashlib
import markdown2
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# from googleapiclient.errors import HttpError
import pickle
import sys

# Файлы — всегда в корне репозитория
JSON_FILE = os.path.join(os.getcwd(), "published_posts.json")

# Загружаем список опубликованных постов
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            published = json.load(f)
        print(f"✅ Загружен список опубликованных постов: {list(published.keys())}")
        print(f"Содержимое JSON при загрузке:\n{json.dumps(published, ensure_ascii=False, indent=2)}")
    except json.JSONDecodeError:
        print("⚠ published_posts.json пустой или поврежден — начинаем с нуля.")
        published = {}
else:
    published = {}
    print("⚠ published_posts.json не найден — начинаем с нуля.")

# Обход markdown файлов
for root, _, files in os.walk("docs"):
    for filename in files:
        if not filename.endswith(".md"):
            continue

        path = os.path.join(root, filename)
        title = os.path.splitext(filename)[0]

        with open(path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        content_hash = hashlib.md5(md_content.encode('utf-8')).hexdigest()

        if title in published and published[title]['hash'] == content_hash:
            print(f"⏭ Без изменений: {title}")
            continue

        # В отладочном режиме пропускаем публикацию в Blogger
        print(f"📝 Новый или изменённый пост: {title}")
        published[title] = {"id": "DUMMY_ID", "hash": content_hash}

# Логируем JSON перед записью
print(f"Содержимое JSON перед записью:\n{json.dumps(published, ensure_ascii=False, indent=2)}")

# Сохраняем JSON (можно оставить)
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(published, f, ensure_ascii=False, indent=2)

print("✅ Скрипт завершён в отладочном режиме (публикация отключена).")
