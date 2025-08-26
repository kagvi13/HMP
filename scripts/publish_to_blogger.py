import os
import json
import hashlib
import time
import re
import argparse
from pathlib import Path

import markdown
from markdown.extensions import tables, fenced_code, codehilite, toc
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

BLOG_ID = os.environ["BLOG_ID"]
TOKEN_FILE = os.environ["TOKEN_FILE"]
PUBLISHED_FILE = "published_posts.json"
GH_PAGES_BASE = "https://kagvi13.github.io/HMP/"


def convert_md_links(md_text: str) -> str:
    """
    Конвертирует относительные ссылки (*.md) в абсолютные ссылки на GitHub Pages.
    """
    def replacer(match):
        text = match.group(1)
        link = match.group(2)

        if link.startswith("http://") or link.startswith("https://") or not link.endswith(".md"):
            return match.group(0)

        abs_link = GH_PAGES_BASE + link.replace(".md", "").lstrip("./")
        return f"[{text}]({abs_link})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replacer, md_text)


def load_published():
    if Path(PUBLISHED_FILE).exists():
        with open(PUBLISHED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    print("⚠ published_posts.json не найден — начинаем с нуля.")
    return {}


def save_published(data):
    with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def file_hash(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def main(force: bool = False):
    # Загружаем токен.json
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/blogger"])

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    service = build("blogger", "v3", credentials=creds)
    published = load_published()

    md_files = list(Path("docs").rglob("*.md"))
    for md_file in md_files:
        name = md_file.stem
        h = file_hash(md_file)

        if not force and name in published and published[name]["hash"] == h:
            continue  # ничего не изменилось

        print(f"📝 {'Форс-обновление' if force else 'Новый или изменённый'} пост: {name}")

        md_text = md_file.read_text(encoding="utf-8")
        
        # Добавляем ссылку на исходный файл в начале
        source_link = f"Источник: [ {md_file.name} ](https://github.com/kagvi13/HMP/blob/main/docs/{md_file.name})\n\n"
        md_text = source_link + md_text

        md_text = convert_md_links(md_text)

        # Конвертация Markdown в HTML с расширениями
        html_content = markdown.markdown(
            md_text,
            extensions=["tables", "fenced_code", "codehilite", "toc"]
        )

        # Добавляем CSS для корректного отображения таблиц и блок-схем
        style = """
        <style>
        table { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
        th, td { border: 1px solid #ccc; padding: 6px 12px; }
        pre { display: block; max-width: 100%; overflow-x: auto; padding: 10px; background-color: #f8f8f8; border: 1px solid #ddd; border-radius: 6px; font-family: monospace; white-space: pre; }
        </style>
        """
        html_content = style + html_content

        body = {
            "kind": "blogger#post",
            "title": name,
            "content": html_content,
        }

        try:
            if name in published:
                post_id = published[name]["id"]
                post = service.posts().update(blogId=BLOG_ID, postId=post_id, body=body).execute()
                print(f"♻ Обновлён пост: {post['url']}")
            else:
                post = service.posts().insert(blogId=BLOG_ID, body=body).execute()
                print(f"🆕 Пост опубликован: {post['url']}")
                post_id = post["id"]

            published[name] = {"id": post_id, "hash": h}
            save_published(published)

            print("⏱ Пауза 60 секунд перед следующим постом...")
            time.sleep(60)

        except HttpError as e:
            print(f"❌ Ошибка при публикации {name}: {e}")
            save_published(published)
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Обновить все посты, даже без изменений")
    args = parser.parse_args()

    main(force=args.force)
