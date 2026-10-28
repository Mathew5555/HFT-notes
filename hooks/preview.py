"""Build the optional cloud navigation from the existing Markdown sources."""
import html
import posixpath
from urllib.parse import urljoin, urlsplit, urlunsplit
import json
import re
import shutil
from pathlib import Path

import yaml


def metadata(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    values = yaml.safe_load(match.group(1)) or {} if match else {}
    body = text[match.end():] if match else text
    heading = re.search(r"^#\s+(.+)$", body, re.M)
    title = str(values.get("title") or (heading.group(1) if heading else path.stem))
    meaningful = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    meaningful = re.sub(r"^#{1,6}\s+.*$", "", meaningful, flags=re.M).strip()
    return title, str(values.get("description") or ""), bool(meaningful)


def natural_key(path):
    return [(0, int(part)) if part.isdigit() else (1, part.lower())
            for part in re.split(r"(\d+)", path.as_posix())]


def page_entry(path, docs_dir, config, number):
    title, description, ready = metadata(path)
    relative = path.relative_to(docs_dir)
    if relative.name == "index.md":
        url = relative.parent.as_posix() + "/"
    elif config.use_directory_urls:
        url = relative.with_suffix("").as_posix() + "/"
    else:
        url = relative.with_suffix(".html").as_posix()
    return {"title": title, "description": description, "ready": ready,
            "url": "read/" + url, "original_url": url, "number": number}


def on_post_build(config, **kwargs):
    docs_dir = Path(config.docs_dir)
    catalog = []
    preferred = ["ml", "infrastructure", "strategy-research"]
    directories = [p for p in docs_dir.iterdir() if p.is_dir() and (p / "index.md").exists()]
    directories.sort(key=lambda p: (preferred.index(p.name) if p.name in preferred else len(preferred), p.name))
    for directory in directories:
        title, _, _ = metadata(directory / "index.md")
        navigation = directory / ".nav.yml"
        if navigation.exists():
            nav = yaml.safe_load(navigation.read_text(encoding="utf-8")) or {}
            title = str(nav.get("title") or title)
        pages = sorted((p for p in directory.rglob("*.md")
                        if p.name.lower() not in {"index.md", "readme.md"}), key=natural_key)
        catalog.append({"id": directory.name, "title": title,
                        "label": "ТЕМЫ И КОНСПЕКТЫ", "pages": [
                            page_entry(p, docs_dir, config, i) for i, p in enumerate(pages, 1)]})
    contributing = docs_dir / "contributing.md"
    if contributing.exists():
        catalog.append({"id": "contributing", "title": "Дополнение конспектов",
                        "label": "ПИШЕМ ВМЕСТЕ", "pages": [page_entry(contributing, docs_dir, config, 1)]})
    output = Path(config.site_dir) / "preview"
    output.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent.parent / "preview"
    for name in ("index.html", "style.css", "app.js", "reader.css", "reader.js"):
        shutil.copyfile(source / name, output / name)
    shutil.copytree(source / "assets", output / "assets", dirs_exist_ok=True)
    data = json.dumps(catalog, ensure_ascii=False).replace("<", "\\u003c")
    (output / "catalog.js").write_text("window.HFT_CATALOG = " + data + ";\n", encoding="utf-8")

    # Reuse the finished Markdown HTML, including MkDocs' resolved image URLs.
    available = {page["original_url"]: page for section in catalog
                 for page in section["pages"] if page["ready"]}
    for section in catalog:
        ready = [page for page in section["pages"] if page["ready"]]
        for index, page in enumerate(ready):
            original = page["original_url"]
            built = Path(config.site_dir) / original
            if original.endswith("/"):
                built /= "index.html"
            rendered = built.read_text(encoding="utf-8")
            match = re.search(r'<article\b[^>]*>(.*?)</article>', rendered, re.S)
            if not match:
                raise ValueError("Cannot find rendered article: " + original)
            content = match.group(1)
            content = re.sub(r'<a\b[^>]*class="[^"]*(?:headerlink|md-content__button)[^"]*"[^>]*>.*?</a>', '', content, flags=re.S)
            destination = "preview/" + page["url"]
            parent = destination if destination.endswith("/") else posixpath.dirname(destination) + "/"

            def relative(target):
                return posixpath.relpath(target, parent.rstrip("/"))

            def rewrite_attribute(found):
                name, quote, raw = found.groups()
                value = html.unescape(raw)
                if not value or value.startswith("#") or urlsplit(value).scheme or value.startswith("//"):
                    return found.group(0)
                resolved = urlsplit(urljoin("/" + original, value))
                target = resolved.path.lstrip("/")
                if name == "href" and target in available:
                    target = "preview/" + available[target]["url"]
                elif name == "href" and target in {section["id"] + "/", ""}:
                    fragment = section["id"] if target else ""
                    return name + "=" + quote + html.escape(relative("preview/") + "/#" + fragment, quote=True) + quote
                rewritten = urlunsplit(("", "", relative(target) + ("/" if target.endswith("/") else ""), resolved.query, resolved.fragment))
                return name + "=" + quote + html.escape(rewritten, quote=True) + quote

            content = re.sub(r"\b(href|src)=([\"'])(.*?)\2", rewrite_attribute, content)
            toc = []
            for anchor, title in re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', content, re.S):
                title = re.sub(r'<[^>]+>', '', title)
                toc.append('<a href="#' + html.escape(anchor, quote=True) + '">' + title + '</a>')
            section_url = relative("preview/") + "/#" + section["id"]
            home_url = relative("preview/") + "/"
            links = []
            for offset, label, arrow in [(-1, "Предыдущий конспект", "←"), (1, "Следующий конспект", "→")]:
                adjacent = index + offset
                if 0 <= adjacent < len(ready):
                    other = ready[adjacent]
                    href = relative("preview/" + other["url"]) + ("/" if other["url"].endswith("/") else "")
                    links.append('<a class="page-turn ' + ('next' if offset == 1 else 'previous') + '" href="' + html.escape(href, quote=True) + '"><span class="turn-label">' + arrow + ' ' + label + '</span><strong>' + html.escape(other["title"]) + '</strong></a>')
                else:
                    links.append('<span aria-hidden="true"></span>')
            template = (source / "reader.html").read_text(encoding="utf-8")
            replacements = {"TITLE": html.escape(page["title"]), "SECTION": html.escape(section["title"]),
                            "SECTION_URL": html.escape(section_url, quote=True), "HOME_URL": home_url,
                            "CSS_URL": relative("preview/reader.css"), "JS_URL": relative("preview/reader.js"),
                            "CONTENT": content, "TOC": ''.join(toc), "PAGINATION": ''.join(links)}
            for key, value in replacements.items():
                template = template.replace("{{" + key + "}}", value)
            target = Path(config.site_dir) / destination
            if destination.endswith("/"):
                target /= "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(template, encoding="utf-8")
