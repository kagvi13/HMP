import os
import pickle
import base64
from googleapiclient.discovery import build
import markdown2

# Загружаем OAuth токен из переменной окружения
token_b64 = os.environ['TOKEN_PKL']
creds = pickle.loads(base64.b64decode(token_b64))

# Инициализируем сервис Blogger API
service = build('blogger', 'v3', credentials=creds)
BLOG_ID = os.environ['BLOG_ID']  # Укажем через GitHub Secrets

# Папка с Markdown-файлами для публикации
POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

for filename in os.listdir(POSTS_DIR):
    if filename.endswith('.md'):
        with open(os.path.join(POSTS_DIR, filename), 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown2.markdown(md_content)
        post = {
            'title': filename.replace('.md',''),
            'content': html_content
        }
        new_post = service.posts().insert(blogId=BLOG_ID, body=post, isDraft=False).execute()
        print(f"Пост опубликован: {new_post['url']}")
