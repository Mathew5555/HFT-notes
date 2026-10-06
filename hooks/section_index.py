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

NUMBER_PREFIX_PATTERN = re.compile(
    r"^\d+[.)]\s*",
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

    title = NUMBER_PREFIX_PATTERN.sub("", title)

    return title, description


def section_pages(directory: Path) -> list[Path]:
    return [
        path
        for path in sorted(directory.glob("*.md"))
        if path.name.lower() not in {"index.md", "readme.md"}
    ]


def build_section_index(directory: Path) -> str:
    items = []

    for chapter_number, path in enumerate(section_pages(directory), start=1):
        title, description = read_page_information(path)
        label = f"{chapter_number}. {title}"

        if description:
            items.append(
                f"- [{label}]({path.name}) — {description}"
            )
        else:
            items.append(f"- [{label}]({path.name})")

    if not items:
        return "_В этом разделе пока нет глав._"

    return "\n".join(items)


def number_navigation_section(section, docs_directory: Path) -> None:
    chapter_number = 1

    for item in section.children:
        if item.is_page:
            source_path = docs_directory / str(item.file.src_uri)
            title, _ = read_page_information(source_path)

            item.title = f"{chapter_number}. {title}"
            chapter_number += 1

        elif item.is_section:
            number_navigation_section(item, docs_directory)


def on_nav(nav, config, **kwargs):
    docs_directory = Path(config.docs_dir)

    for item in nav.items:
        if item.is_section:
            number_navigation_section(item, docs_directory)

    return nav


def on_page_markdown(markdown, page, config, **kwargs):
    if MARKER not in markdown:
        return markdown

    source_path = Path(config.docs_dir) / str(page.file.src_uri)
    generated_index = build_section_index(source_path.parent)

    return markdown.replace(MARKER, generated_index)
