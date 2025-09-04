import os
import json
import hashlib
import time
import re
from pathlib import Path

import requests

PUBLISHED_FILE = "published_posts.json"
GH_PAGES_BASE = "https://kagvi13.github.io/HMP/"

HASHNODE_TOKEN = os.environ["HASHNODE_TOKEN"]
HASHNODE_PUBLICATION_ID = os.environ["HASHNODE_PUBLICATION_ID"]
API_URL = "https://gql.hashnode.com"

def convert_md_links(md_text: str) -> str:
    def replacer(match):
        text, link = match.groups()
        if link.startswith("http://") or link.startswith("https://") or not link.endswith(".md"):
            return match.group(0)
        abs_link = GH_PAGES_BASE + link.replace(".md", "").lstrip("./")
        return f"[{text}]({abs_link})"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replacer, md_text)

def load_published():
    if Path(PUBLISHED_FILE).exists():
        with open(PUBLISHED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_published(data):
    with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def file_hash(md_text: str):
    return hashlib.md5(md_text.encode("utf-8")).hexdigest()

def graphql_request(query, variables):
    headers = {"Authorization": f"Bearer {HASHNODE_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    data = resp.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data

def create_post(title, slug, markdown_content):
    query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) {
        draft { id slug title }
      }
    }
    """
    variables = {"input": {"title": title, "contentMarkdown": markdown_content,
                           "slug": slug, "publicationId": HASHNODE_PUBLICATION_ID}}
    return graphql_request(query, variables)["data"]["createDraft"]["draft"]

def update_post(slug, title, markdown_content):
    query = """
    mutation UpdateDraft($slug: String!, $input: UpdateDraftInput!) {
      updateDraft(slug: $slug, input: $input) {
        draft { slug title id }
      }
    }
    """
    variables = {
        "slug": slug,
        "input": {
            "title": title,
            "contentMarkdown": markdown_content
        }
    }
    return graphql_request(query, variables)["data"]["updateDraft"]["draft"]


def publish_draft(draft_id):
    query = """
    mutation PublishDraft($input: PublishDraftInput!) {
      publishDraft(input: $input) { post { id slug url } }
    }
    """
    variables = {"input": {"draftId": draft_id}}
    return graphql_request(query, variables)["data"]["publishDraft"]["post"]

def main(force=False):
    published = load_published()
    md_files = list(Path("docs").rglob("*.md"))

    for md_file in md_files:
        name = md_file.stem
        title = name if len(name) >= 6 else name + "-HMP"
        slug = re.sub(r'[^a-z0-9-]', '-', title.lower()).strip('-')[:250]

        md_text = f"Источник: [ {md_file.name} ](https://github.com/kagvi13/HMP/blob/main/docs/{md_file.name})\n\n" + md_file.read_text(encoding="utf-8")
        md_text = convert_md_links(md_text)
        h = file_hash(md_text)

        if not force and name in published and published[name].get("hash") == h:
            print(f"✅ Пост '{name}' без изменений — пропускаем.")
            continue

        try:
            if name in published and "id" in published[name]:
                post = update_post(published[name]["id"], title, md_text)
                print(f"♻ Обновлён пост: https://hashnode.com/@yourusername/{post['slug']}")
            else:
                draft = create_post(title, slug, md_text)
                post = publish_draft(draft["id"])
                print(f"🆕 Пост опубликован: https://hashnode.com/@yourusername/{post['slug']}")

            published[name] = {"id": post["id"], "slug": post["slug"], "hash": h}
            save_published(published)
            time.sleep(30)

        except Exception as e:
            print(f"❌ Ошибка при публикации {name}: {e}")
            save_published(published)
            break

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    main(force=args.force)
