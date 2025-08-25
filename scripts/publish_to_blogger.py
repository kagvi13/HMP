import os
import pickle
import json
import time
import base64
from googleapiclient.discovery import build
import markdown2
from googleapiclient.errors import HttpError

# Загрузка OAuth токена
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.pkl')
with open(TOKEN_FILE, 'rb') as f:
    creds = pickle.load(f)

service = build('blogger', 'v3', credentials=creds)
BLOG_ID = os.environ['BLOG_ID']

# Папка с Markdown-файлами
POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

# Файл для хранения соответствия Markdown <-> Blogger postId
STATE_FILE = os.path.join(os.path.dirname(__file__), 'published_posts.json')
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        published = json.load(f)
else:
    published = {}

for filename in os.listdir(POSTS_DIR):
    if not filename.endswith('.md'):
        continue

    file_path = os.path.join(POSTS_DIR, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown2.markdown(md_content)

    post_body = {
        'title': filename.replace('.md', ''),
        'content': html_content
    }

    post_id = published.get(filename)
    try:
        if post_id:
            # Обновляем существующий пост
            updated_post = service.posts().update(
                blogId=BLOG_ID,
                postId=post_id,
                body=post_body
            ).execute()
            print(f"Пост обновлён: {updated_post['url']}")
        else:
            # Публикуем новый пост
            new_post = service.posts().insert(
                blogId=BLOG_ID,
                body=post_body,
                isDraft=False
            ).execute()
            published[filename] = new_post['id']
            print(f"Пост опубликован: {new_post['url']}")

    except HttpError as e:
        error_content = json.loads(e.content.decode())
        reason = error_content['error']['errors'][0]['reason']
        if reason == 'quotaExceeded':
            print(f"Квота превышена, публикация отложена для {filename}")
        else:
            raise

# Сохраняем состояние
with open(STATE_FILE, 'w', encoding='utf-8') as f:
    json.dump(published, f, ensure_ascii=False, indent=2)
