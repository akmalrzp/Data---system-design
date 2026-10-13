#!/usr/bin/env python3
"""Write sections from full-guide.md back to their atomic wiki pages.

Usage: python scripts/split_guide.py            (run from the repository root)
The source pages and frontmatter are preserved; only pages present in the guide
are updated. Run build_guide.py afterward to regenerate the assembled guide.
"""
import argparse
import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
GUIDE = ROOT / "full-guide.md"
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)", re.S)
SECTION = re.compile(r'(?m)^<a id="([^"]+)"></a>\s*\r?\n(#{1,2}) ([^\r\n]+)\r?\n')
SOURCE_REFERENCE = re.compile(r"\*([^*\n]+)\* \(`([^`\n]+)`\)")
PAGE_ANCHOR = re.compile(r"\]\(#([^)]+)\)")


def parse_page(path):
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"Missing or malformed frontmatter: {path}")

    metadata = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, match.group(2).strip()


def relative_link(source_path, target_path):
    return posixpath.relpath(target_path.as_posix(), source_path.parent.as_posix())


def restore_links(text, source_path, pages, sources):
    def restore_source(match):
        title, raw = match.groups()
        page = sources.get((title, raw))
        if not page:
            return match.group(0)
        return f"[{title}]({relative_link(source_path, page['path'])})"

    text = SOURCE_REFERENCE.sub(restore_source, text)

    def restore_page_anchor(match):
        slug = match.group(1).split("#", 1)[0]
        page = pages.get(slug)
        if not page:
            return match.group(0)
        return f"]({relative_link(source_path, page['path'])})"

    return PAGE_ANCHOR.sub(restore_page_anchor, text)


def hub_pages_section(body, path):
    pages_heading = re.search(r"(?m)^## Pages\s*$", body)
    if not pages_heading:
        return ""

    section = re.search(
        r"(?ms)^## Pages\r?\n(?:- \[[^\]]+\]\([^)]+\)\r?\n?)+\s*$", body
    )
    if not section:
        raise ValueError(f"Could not preserve the Pages list in hub page: {path}")
    return section.group(0).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide", type=Path, default=GUIDE, help="assembled guide Markdown file")
    parser.add_argument("--wiki", type=Path, default=WIKI, help="wiki directory containing atomic pages")
    args = parser.parse_args()

    pages = {}
    sources = {}
    for path in sorted(args.wiki.rglob("*.md")):
        if path.name in ("SCHEMA.md", "index.md", "log.md"):
            continue
        metadata, body = parse_page(path)
        page = {
            "meta": metadata,
            "body": body,
            "path": path.relative_to(args.wiki),
        }
        pages[path.stem] = page
        if metadata.get("type") == "source":
            sources[(metadata.get("title"), metadata.get("raw"))] = page

    guide_text = args.guide.read_text(encoding="utf-8")
    sections = list(SECTION.finditer(guide_text))
    if not sections:
        raise ValueError(f"No page sections found in guide: {args.guide}")

    updates = []
    seen = set()
    for index, section in enumerate(sections):
        slug, heading_level, _heading = section.groups()
        if slug in seen:
            raise ValueError(f"Duplicate page anchor in guide: {slug}")
        seen.add(slug)

        page = pages.get(slug)
        if not page:
            raise ValueError(f"Guide section has no matching wiki page: {slug}")
        if page["meta"].get("type") == "source":
            raise ValueError(f"Source page unexpectedly has a guide section: {slug}")

        expected_level = "#" if page["meta"].get("type") == "guide" else "##"
        if heading_level != expected_level:
            raise ValueError(
                f"Unexpected heading level for {slug}: expected {expected_level}, got {heading_level}"
            )

        end = sections[index + 1].start() if index + 1 < len(sections) else len(guide_text)
        body = guide_text[section.end():end].strip()
        body = restore_links(body, page["path"], pages, sources)
        if page["meta"].get("type") != "guide":
            body = re.sub(
                r"(?m)^(#{3,6}) ",
                lambda match: "#" * (len(match.group(1)) - 1) + " ",
                body,
            )

        page_body = f"# {page['meta']['title']}\n\n{body}".rstrip()
        if page["meta"].get("type") == "guide":
            pages_list = hub_pages_section(page["body"], slug)
            if pages_list:
                page_body += f"\n\n{pages_list}"

        page_file = args.wiki / page["path"]
        metadata_text = page_file.read_text(encoding="utf-8").split("---", 2)[1]
        updates.append((page_file, f"---{metadata_text}---\n\n{page_body}\n"))

    for page_file, content in updates:
        page_file.write_text(content, encoding="utf-8")
    print(f"updated={len(updates)} pages from {args.guide}")


if __name__ == "__main__":
    main()
