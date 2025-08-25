#!/usr/bin/env python3
import os
import json
import hashlib
import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import argparse

# === Настройки ===
SITE_DIR = "site"  # HTML-файлы после mkdocs build
PUBLISHED_FILE = "published_posts.json"
SLEEP_BETWEEN_POSTS = 60  # секунд
BLOG_ID = os.environ.get("BLOG_ID")
TOKEN_FILE = os.environ.get("TOKEN_FILE", "token.pkl")

# === Утилиты ===
def md5sum(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    print("⚠ published_posts.json не найден — начинаем с нуля.")
    return {}

def save_published(data):
    with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    return build("blogger", "v3", credentials=creds)

# === Основная логика ===
def publish_site():
    service = get_service()
    published = load_published()

    # собираем все html-файлы
    html_files = []
    for root, _, files in os.walk(SITE_DIR):
        for name in files:
            if name.endswith(".html"):
                path = os.path.join(root, name)
                rel_path = os.path.relpath(path, SITE_DIR)  # ключ
                html_files.append((rel_path, path))

    for rel_path, path in html_files:
        content_hash = md5sum(path)
        post_meta = published.get(rel_path)

        # читаем содержимое html
        with open(path, "r", encoding="utf-8") as f:
            html_content = f.read()

        if post_meta and post_meta["hash"] == content_hash:
            print(f"⏭ Пропускаем {rel_path} — без изменений")
            continue

        title = os.path.splitext(os.path.basename(rel_path))[0]

        if post_meta:  # обновление поста
            post_id = post_meta["id"]
            print(f"🔄 Обновляем пост {rel_path}")
            post = (
                service.posts()
                .update(
                    blogId=BLOG_ID,
                    postId=post_id,
                    body={"title": title, "content": html_content},
                )
                .execute()
            )
        else:  # новый пост
            print(f"🆕 Публикуем новый пост {rel_path}")
            post = (
                service.posts()
                .insert(
                    blogId=BLOG_ID,
                    body={"title": title, "content": html_content},
                )
                .execute()
            )

        url = post.get("url")
        post_id = post.get("id")
        print(f"✅ {rel_path} → {url}")

        # сохраняем метаданные
        published[rel_path] = {"id": post_id, "hash": content_hash}
        save_published(published)

        print(f"⏱ Пауза {SLEEP_BETWEEN_POSTS} секунд перед следующим постом…")
        time.sleep(SLEEP_BETWEEN_POSTS)

if __name__ == "__main__":
    publish_site()
