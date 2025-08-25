import os
import json
import pickle
from googleapiclient.discovery import build
import markdown2

# Загружаем токен
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.pkl')
with open(TOKEN_FILE, 'rb') as f:
    creds = pickle.load(f)

service = build('blogger', 'v3', credentials=creds)
BLOG_ID = os.environ['BLOG_ID']

# published_posts.json рядом со скриптом
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(SCRIPT_DIR, 'published_posts.json')

# Безопасная загрузка JSON
if os.path.exists(JSON_FILE) and os.path.getsize(JSON_FILE) > 0:
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            published = json.load(f)
    except (json.JSONDecodeError, ValueError):
        published = {}
else:
    published = {}

print("Успешно загружен список опубликованных постов:", published)

# Папка с Markdown-файлами
POSTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'docs')

for filename in os.listdir(POSTS_DIR):
    if filename.endswith('.md'):
        with open(os.path.join(POSTS_DIR, filename), 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown2.markdown(md_content)

        title = filename.replace('.md', '')
        content_hash = hash(md_content)

        # если пост уже есть и не изменился → пропускаем
        if title in published and published[title]['hash'] == content_hash:
            print(f"Пост без изменений: {title}")
            continue

        post = {
            'title': title,
            'content': html_content
        }

        if title in published:
            # обновляем пост
            post_id = published[title]['id']
            updated_post = service.posts().update(blogId=BLOG_ID, postId=post_id, body=post).execute()
            print(f"Пост обновлён: {updated_post['url']}")
            published[title] = {"id": post_id, "hash": content_hash}
        else:
            # создаём новый пост
            new_post = service.posts().insert(blogId=BLOG_ID, body=post, isDraft=False).execute()
            print(f"Пост опубликован: {new_post['url']}")
            published[title] = {"id": new_post['id'], "hash": content_hash}

# сохраняем обновлённый список постов
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(published, f, ensure_ascii=False, indent=2)
