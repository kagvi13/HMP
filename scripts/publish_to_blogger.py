import json
import os
import hashlib
import markdown2
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import pickle
import sys

# Файлы
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "published_posts.json"))

# Загружаем токен
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.pkl')
with open(TOKEN_FILE, 'rb') as f:
    creds = pickle.load(f)

service = build('blogger', 'v3', credentials=creds)
BLOG_ID = os.environ['BLOG_ID']

# Загружаем список опубликованных постов
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            published = json.load(f)
        print(f"✅ Загружен список опубликованных постов: {list(published.keys())}")
    except json.JSONDecodeError:
        print("⚠ published_posts.json пустой или поврежден — начинаем с нуля.")
        published = {}
else:
    published = {}

# Обход markdown файлов
for root, _, files in os.walk("docs"):
    for filename in files:
        if not filename.endswith(".md"):
            continue

        path = os.path.join(root, filename)
        title = os.path.splitext(filename)[0]

        with open(path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        html_content = markdown2.markdown(md_content)
        content_hash = hashlib.md5(md_content.encode('utf-8')).hexdigest()

        # Пропускаем если ничего не изменилось
        if title in published and published[title]['hash'] == content_hash:
            print(f"⏭ Без изменений: {title}")
            continue

        post = {
            "kind": "blogger#post",
            "title": title,
            "content": html_content
        }

        try:
            if title in published:
                # обновляем
                post_id = published[title]['id']
                updated_post = service.posts().update(
                    blogId=BLOG_ID, postId=post_id, body=post
                ).execute()
                print(f"♻️ Пост обновлён: {updated_post['url']}")
                published[title] = {"id": post_id, "hash": content_hash}
            else:
                # публикуем новый
                new_post = service.posts().insert(
                    blogId=BLOG_ID, body=post, isDraft=False
                ).execute()
                print(f"🆕 Пост опубликован: {new_post['url']}")
                published[title] = {"id": new_post['id'], "hash": content_hash}

            # 💾 сохраняем прогресс
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(published, f, ensure_ascii=False, indent=2)

            print("✅ Завершаем выполнение после первого поста.")
            sys.exit(0)

        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                print("⚠ Достигнут лимит Blogger API. Попробуйте снова позже.")
                sys.exit(1)
            else:
                raise

print("🎉 Все посты уже актуальны — новых публикаций нет.")
