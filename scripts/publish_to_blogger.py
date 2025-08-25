import os
import pickle
import json
import hashlib
from googleapiclient.discovery import build
import markdown2

TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.pkl')
BLOG_ID = os.environ['BLOG_ID']
POSTS_DIR = 'docs'
JSON_FILE = 'scripts/published_posts.json'

# Загружаем OAuth токен
with open(TOKEN_FILE, 'rb') as f:
    creds = pickle.load(f)

service = build('blogger', 'v3', credentials=creds)

# Загружаем JSON с опубликованными постами
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        published = json.load(f)
else:
    published = {}

def file_hash(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

for filename in os.listdir(POSTS_DIR):
    if filename.endswith('.md'):
        filepath = os.path.join(POSTS_DIR, filename)
        content_hash = file_hash(filepath)
        md_content = open(filepath, 'r', encoding='utf-8').read()
        html_content = markdown2.markdown(md_content)

        post_info = published.get(filename, {})
        post_id = post_info.get('postId')
        old_hash = post_info.get('hash')

        if old_hash == content_hash and post_id:
            print(f"Пропускаем {filename}, изменений нет")
            continue

        post = {'title': filename.replace('.md',''), 'content': html_content}

        try:
            if post_id:
                new_post = service.posts().update(blogId=BLOG_ID, postId=post_id, body=post).execute()
                print(f"Пост обновлён: {new_post['url']}")
            else:
                raise KeyError
        except Exception:
            new_post = service.posts().insert(blogId=BLOG_ID, body=post).execute()
            print(f"Пост опубликован: {new_post['url']}")

        # Сохраняем новый/обновлённый postId и hash
        published[filename] = {'postId': new_post['id'], 'hash': content_hash}

# Сохраняем JSON
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(published, f, indent=2, ensure_ascii=False)
