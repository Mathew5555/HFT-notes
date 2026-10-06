import re
from pathlib import Path

import yaml


MARKER = "<!-- AUTO_SECTION_INDEX -->"

FRONT_MATTER_PATTERN = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)

H1_PATTERN = re.compile(
    r"^#\s+(.+?)\s*$",
    re.MULTILINE,
)


def read_page_information(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")

    title = ""
    description = ""

    front_matter_match = FRONT_MATTER_PATTERN.match(content)

    if front_matter_match:
        metadata = yaml.safe_load(front_matter_match.group(1)) or {}
        title = str(metadata.get("title", "")).strip()
        description = str(metadata.get("description", "")).strip()

    if not title:
        h1_match = H1_PATTERN.search(content)

        if h1_match:
            title = h1_match.group(1).strip()

    if not title:
        title = re.sub(r"^\d+[-_ ]*", "", path.stem)
        title = title.replace("-", " ").replace("_", " ").capitalize()

    return title, description


def build_section_index(directory: Path) -> str:
    pages = sorted(directory.glob("*.md"))

    items = []

    for path in pages:
        if path.name.lower() in {"index.md", "readme.md"}:
            continue

        title, description = read_page_information(path)

        if description:
            items.append(
                f"- [{title}]({path.name}) — {description}"
            )
        else:
            items.append(f"- [{title}]({path.name})")

    if not items:
        return "_В этом разделе пока нет конспектов._"

    return "\n".join(items)


def on_page_markdown(markdown, page, config, **kwargs):
    if MARKER not in markdown:
        return markdown

    source_path = Path(config.docs_dir) / str(page.file.src_uri)
    section_index = build_section_index(source_path.parent)

    return markdown.replace(MARKER, section_index)
