import os
import re
from pathlib import Path
import yaml

# Корень репозитория — отталкиваемся от местоположения скрипта
REPO_ROOT = Path(__file__).resolve().parent.parent

# теги по ключевым словам для автодобавления
KEYWORD_TAGS = [
    "CCore", "CShell", "REPL", "Mesh", "Agent", "HMP",
    "MeshConsensus", "CogSync", "GMP", "EGP",
    "Ethics", "Scenarios", "JSON"
]

ROOT_DIR = Path(".")
STRUCTURED_DIR = ROOT_DIR / "structured_md"
INDEX_FILE = STRUCTURED_DIR / "index.md"

MD_EXT = ".md"

# Шаблон JSON-LD для разных типов
JSON_LD_TEMPLATES = {
    "FAQ": """\n```json
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": {main_entity}
}}
```\n""",
    "HowTo": """\n```json
{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{title}",
  "description": "{description}",
  "step": {steps}
}}
```\n""",
    "Article": """\n```json
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "{title}",
  "description": "{description}"
}}
```\n"""
}

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def is_md_file(path):
    return path.suffix.lower() == MD_EXT and STRUCTURED_DIR not in path.parents

def extract_front_matter(content: str):
    """Возвращает (front_matter_dict, clean_content) — без YAML-шапки."""
    match = FRONT_MATTER_RE.match(content)
    if match:
        try:
            data = yaml.safe_load(match.group(1)) or {}
        except Exception:
            data = {}
        clean = content[match.end():]
        return data, clean
    return {}, content

def detect_file_type(content: str, front_matter: dict | None = None) -> str:
    """Определяет тип: FAQ / HowTo / Article (по front-matter или заголовкам)."""
    front_matter = front_matter or {}
    if "type" in front_matter:
        return front_matter["type"]

    # Простые эвристики по заголовкам
    if re.search(r"^#\s*FAQ\b", content, re.MULTILINE) or re.search(r"^##\s*Q&A\b", content, re.MULTILINE):
        return "FAQ"
    if re.search(r"^#\s*HowTo\b", content, re.MULTILINE) or re.search(r"^#\s*Как\s+сделать\b", content, re.IGNORECASE | re.MULTILINE):
        return "HowTo"
    return "Article"

def parse_front_matter(content):
    match = FRONT_MATTER_RE.match(content)
    if match:
        try:
            data = yaml.safe_load(match.group(1))
            return data
        except Exception:
            pass
    return {}

def determine_type(content, front_matter):
    if "type" in front_matter:
        return front_matter["type"]
    # Простейшее определение по ключевым словам в заголовках
    if re.search(r"^#.*FAQ", content, re.MULTILINE):
        return "FAQ"
    if re.search(r"^#.*HowTo", content, re.MULTILINE):
        return "HowTo"
    return "Article"

def generate_json_ld(content, front_matter, ftype, title, rel_path):
    desc = front_matter.get("description", content[:100].replace("\n", " ") + "...")
    url = f"structured_md/{rel_path.as_posix()}"

    if ftype == "FAQ":
        q_matches = re.findall(r"^##\s*(.+)$", content, re.MULTILINE)
        main_entity = []
        for q in q_matches:
            ans_match = re.search(rf"##\s*{re.escape(q)}\s*\n(.+?)(\n##|\Z)", content, re.DOTALL)
            answer_text = ans_match.group(1).strip() if ans_match else ""
            main_entity.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": answer_text}
            })
        import json
        return JSON_LD_TEMPLATES["FAQ"].format(
            main_entity=json.dumps(main_entity, ensure_ascii=False, indent=2)
        ).replace("}}", f',\n  "url": "{url}"\n}}', 1)

    elif ftype == "HowTo":
        steps = [{"@type": "HowToStep", "name": s.strip()} for s in re.findall(r"^- (.+)$", content, re.MULTILINE)]
        import json
        return JSON_LD_TEMPLATES["HowTo"].format(
            title=title, description=desc, steps=json.dumps(steps, ensure_ascii=False, indent=2)
        ).replace("}}", f',\n  "url": "{url}"\n}}', 1)

    else:  # Article
        return JSON_LD_TEMPLATES["Article"].format(
            title=title, description=desc
        ).replace("}}", f',\n  "url": "{url}"\n}}', 1)

def add_index_link(content, file_path):
    # относительный путь от текущего файла до structured_md/index.md
    rel_path = os.path.relpath(STRUCTURED_DIR / "index.md", file_path.parent)
    link_line = f"\n\n---\n> ⚡ [AI friendly version docs (structured_md)]({rel_path})\n"
    if link_line.strip() not in content:
        content += link_line
    return content

def extract_tags(content, existing_tags):
    tags = set(existing_tags or [])
    for kw in KEYWORD_TAGS:
        if kw.lower() in content.lower():
            tags.add(kw)
    return list(tags)

def mirror_md_files():
    processed = []
    for path in REPO_ROOT.rglob("*.md"):
        if "structured_md" in path.parts or path.name.lower() == "index.md":
            continue

        rel_path = path.relative_to(REPO_ROOT)
        target_path = STRUCTURED_DIR / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("r", encoding="utf-8") as f:
            content = f.read()

        front_matter, clean_content = extract_front_matter(content)
        ftype = detect_file_type(clean_content, front_matter)

        # ищем заголовок 1-го уровня для title/description
        h1_match = re.search(r"^#\s*(.+)$", clean_content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
            rest_content = clean_content[h1_match.end():].strip()
            description = front_matter.get("description", rest_content[:200].replace("\n", " ") + "...")
        else:
            title = front_matter.get("title", path.stem)
            description = front_matter.get("description", clean_content[:200].replace("\n", " ") + "...")

        tags = extract_tags(clean_content, front_matter.get("tags", []))

        # формируем YAML фронт-маттер
        fm_dict = {
            "title": title,
            "description": description,
            "type": ftype,
            "tags": tags,
        }
        yaml_fm = "---\n" + yaml.safe_dump(fm_dict, sort_keys=False, allow_unicode=True) + "---\n\n"

        # добавляем корректную ссылку на индекс
        clean_content = add_index_link(clean_content, target_path)

        # формируем JSON-LD
        json_ld = generate_json_ld(clean_content, front_matter, ftype, title, rel_path)

        # пишем новый Markdown
        with target_path.open("w", encoding="utf-8") as f:
            f.write(yaml_fm)
            f.write(clean_content.rstrip())
            f.write("\n\n")
            f.write(json_ld)

        processed.append(rel_path)

    return processed
    
def generate_index(files):
    index_lines = ["# ИИ-дружелюбные версии файлов\n"]
    tree = {}

    for f in files:
        parts = list(f.parts)
        d = tree
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = None

    def render_tree(d, parent_path="", level=0):
        lines = []
        for name, sub in sorted(d.items()):
            indent = "  " * level
            full_path = Path(parent_path) / name
            if sub is None:
                lines.append(f"{indent}- [{name}]({full_path.as_posix()})")
            else:
                lines.append(f"{indent}- {name}")
                lines.extend(render_tree(sub, full_path, level + 1))
        return lines

    index_lines.extend(render_tree(tree))

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))

if __name__ == "__main__":
    STRUCTURED_DIR.mkdir(exist_ok=True)
    md_files = mirror_md_files()
    generate_index(md_files)
    print(f"Обработано {len(md_files)} файлов. Индекс создан: {INDEX_FILE}")
