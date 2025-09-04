import os
import json
import hashlib
import time
import re
from pathlib import Path

import requests
import markdown
from markdown.extensions import tables, fenced_code, codehilite, toc

PUBLISHED_FILE = "published_posts.json"
GH_PAGES_BASE = "https://kagvi13.github.io/HMP/"

HASHNODE_TOKEN = os.environ["HASHNODE_TOKEN"]
HASHNODE_PUBLICATION_ID = os.environ["HASHNODE_PUBLICATION_ID"]
API_URL = "https://gql.hashnode.com"


def convert_md_links(md_text: str) -> str:
    """Конвертирует относительные ссылки (*.md) в абсолютные ссылки на GitHub Pages."""
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


def graphql_request(query, variables):
    headers = {
        "Authorization": f"Bearer {HASHNODE_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    try:
        resp_json = response.json()
    except json.JSONDecodeError:
        raise Exception(f"GraphQL вернул не JSON: {response.text}")

    print("DEBUG: GraphQL response:", json.dumps(resp_json, indent=2))

    if response.status_code != 200:
        raise Exception(f"GraphQL request failed with {response.status_code}: {response.text}")
    if "errors" in resp_json:
        raise Exception(f"GraphQL errors: {resp_json['errors']}")
    return resp_json


def create_post(title, slug, markdown_content):
    query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) {
        draft {
          id
          slug
          title
        }
      }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": markdown_content,
            "slug": slug,
            "publicationId": HASHNODE_PUBLICATION_ID
        }
    }
    return graphql_request(query, variables)["data"]["createDraft"]["draft"]


def update_post(post_id, title, slug, markdown_content):
    query = """
    mutation UpdateDraft($id: ID!, $input: UpdateDraftInput!) {
      updateDraft(id: $id, input: $input) {
        draft {
          id
          slug
          title
        }
      }
    }
    """
    variables = {
        "id": post_id,
        "input": {
            "title": title,
            "contentMarkdown": markdown_content,
            "slug": slug
        }
    }
    return graphql_request(query, variables)["data"]["updateDraft"]["draft"]


def publish_draft(draft_id):
    query = """
    mutation PublishDraft($id: ID!) {
      publishDraft(id: $id) {
        post {
          id
          slug
          url
        }
      }
    }
    """
    variables = {"id": draft_id}
    return graphql_request(query, variables)["data"]["publishDraft"]["post"]


def main(force=False):
    published = load_published()
    md_files = list(Path("docs").rglob("*.md"))

    for md_file in md_files:
        name = md_file.stem
        slug = re.sub(r'[^a-z0-9-]', '-', name.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        slug = slug[:250]
        h = file_hash(md_file)

        if not force and name in published and published[name]["hash"] == h:
            print(f"✅ Пост '{name}' без изменений — пропускаем.")
            continue

        md_text = md_file.read_text(encoding="utf-8")
        source_link = f"Источник: [ {md_file.name} ](https://github.com/kagvi13/HMP/blob/main/docs/{md_file.name})\n\n"
        md_text = source_link + md_text
        md_text = convert_md_links(md_text)

        try:
            if name in published and "id" in published[name]:
                post_id = published[name]["id"]
                post = update_post(post_id, name, slug, md_text)
                print(f"♻ Обновлён пост: https://hashnode.com/@yourusername/{post['slug']}")
            else:
                post = create_post(name, slug, md_text)
                post = publish_draft(post["id"])
                print(f"🆕 Пост опубликован: https://hashnode.com/@yourusername/{post['slug']}")

            published[name] = {"id": post["id"], "slug": post["slug"], "hash": h}
            save_published(published)

            print("⏱ Пауза 30 секунд перед следующим постом...")
            time.sleep(30)

        except Exception as e:
            print(f"❌ Ошибка при публикации {name}: {e}")
            save_published(published)
            break


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Обновить все посты, даже без изменений")
    args = parser.parse_args()

    main(force=args.force)
