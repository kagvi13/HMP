import os
import pickle
from googleapiclient.discovery import build
import markdown2

# Путь до token.pkl
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.pkl')

# Загружаем OAuth токен
with open(TOKEN_FILE, 'rb') as f:
    creds = pickle.load(f)

# Создаём сервис Blogger API
service = build('blogger', 'v3', credentials=creds)

# ID блога берём из переменной окружения
BLOG_ID = os.environ['BLOG_ID']

# Папка с Markdown-файлами для публикации
POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

for filename in os.listdir(POSTS_DIR):
    if filename.endswith('.md'):
        with open(os.path.join(POSTS_DIR, filename), 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown2.markdown(md_content)
        post = {
            'title': filename.replace('.md', ''),
            'content': html_content
        }
        new_post = service.posts().insert(blogId=BLOG_ID, body=post, isDraft=False).execute()
        print(f"Пост опубликован: {new_post['url']}")
        
