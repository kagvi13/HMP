import os
import sys
import json
import hashlib
import markdown2
import pickle
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Настройки
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "published_posts.json"))
LOCK_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "publish.lock"))

# Блокировка, чтобы скрипт не запускался дважды
if os.path.exists(LOCK_FILE):
    print("⚠ Скрипт уже запущен — выходим.")
    sys.exit(0)

with open(LOCK_FILE, "w") as f:
    f.write("locked")

try:
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
        print("⚠ published_posts.json не найден — начинаем с нуля.")
        published = {}

    # Обходим markdown-файлы
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
                continue

            print(f"📝 Новый или изменённый пост: {title}")

            post = {
                "kind": "blogger#post",
                "title": title,
                "content": html_content
            }

            try:
                # Если отладка — просто обновляем JSON
                if os.environ.get('DEBUG_PUBLISH', '0') == '1':
                    post_id = published.get(title, {}).get("id", "DUMMY_ID")
                    published[title] = {"id": post_id, "hash": content_hash}
                    print("✅ Скрипт завершён в отладочном режиме (публикация отключена).")
                    with open(JSON_FILE, 'w', encoding='utf-8') as f:
                        json.dump(published, f, ensure_ascii=False, indent=2)
                    sys.exit(0)

                # Публикуем новый или обновляем существующий
                if title in published:
                    post_id = published[title]['id']
                    updated_post = service.posts().update(
                        blogId=BLOG_ID, postId=post_id, body=post
                    ).execute()
                    print(f"♻️ Пост обновлён: {updated_post['url']}")
                    published[title] = {"id": post_id, "hash": content_hash}
                else:
                    new_post = service.posts().insert(
                        blogId=BLOG_ID, body=post, isDraft=False
                    ).execute()
                    print(f"🆕 Пост опубликован: {new_post['url']}")
                    published[title] = {"id": new_post['id'], "hash": content_hash}

                # Сохраняем прогресс
                with open(JSON_FILE, 'w', encoding='utf-8') as f:
                    json.dump(published, f, ensure_ascii=False, indent=2)

                # Публикуем только один пост за запуск
                print("✅ Завершаем выполнение после одного поста.")
                sys.exit(0)

            except HttpError as e:
                if e.resp.status == 403 and "quotaExceeded" in str(e):
                    print("⚠ Достигнут лимит Blogger API. Попробуйте снова позже.")
                    sys.exit(1)
                else:
                    raise

    print("🎉 Все посты уже актуальны — новых публикаций нет.")

finally:
    # Удаляем блокировку
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
