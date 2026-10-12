#!/usr/bin/env python3
"""Build wiki/index.md and 'System design guide.md' from atomic pages.

Usage: python scripts/build_guide.py            (run from the repository root)
Order of the assembled guide = guide-NN hubs, then each hub's Markdown page list.
Relative Markdown page links become in-document anchors in the assembled guide.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

def parse(p):
    t = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    fm, body = m.group(1), m.group(2).strip()
    meta = {}
    for line in fm.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, body

pages = {}
for p in sorted(WIKI.rglob("*.md")):
    if p.name in ("SCHEMA.md", "index.md", "log.md"):
        continue
    meta, body = parse(p)
    pages[p.stem] = dict(meta=meta, body=body, path=p.relative_to(WIKI))

def linked_page(source_path, target):
    target_path = target.split("#", 1)[0]
    if not target_path.lower().endswith(".md"):
        return None
    resolved = (WIKI / source_path).parent / target_path
    try:
        relative = resolved.resolve().relative_to(WIKI.resolve()).as_posix()
    except ValueError:
        return None
    return next((page for page in pages.values() if page["path"].as_posix() == relative), None)

def summary(body, source_path):
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith(("#", "|", "-", "*", "```", ">", "1.")):
            def link_title(match):
                page = linked_page(source_path, match.group(2))
                return page["meta"]["title"] if page else match.group(0)
            s = MD_LINK.sub(link_title, s)
            s = re.sub(r"[*`]", "", s)
            return (s[:117] + "...") if len(s) > 120 else s
    return ""

# ---- index.md
order = [("source", "Sources"), ("guide", "Guide sections"), ("concept", "Concepts"),
         ("module-type", "Module types"), ("table-type", "Table types"), ("pattern", "Communication patterns"),
         ("usecase", "Use cases"), ("decision", "Decisions"), ("ops", "Operations and appendices")]
out = ["# Wiki Index", "",
       "Catalog of all pages. Start with the guide sections, or read the single-file version: `../System design guide.md`.", ""]
for typ, head in order:
    out += [f"## {head}", ""]
    for slug, pg in pages.items():
        if pg["meta"].get("type") == typ:
            out.append(f"- [{slug}]({pg['path'].as_posix()}): {summary(pg['body'], pg['path'])}")
    out.append("")
(WIKI / "index.md").write_text("\n".join(out), encoding="utf-8")

# ---- assembled guide
def conv(text, source_path):
    def r(m):
        page = linked_page(source_path, m.group(2))
        if page and page["meta"].get("type") == "source":
            return f"*{page['meta']['title']}* (`{page['meta']['raw']}`)"
        if page:
            slug = page["path"].stem
            return f"[{page['meta']['title']}](#{slug})"
        return m.group(0)
    return MD_LINK.sub(r, text)

def render(slug, top):
    pg = pages[slug]
    body = pg["body"]
    body = re.sub(r"^# .*\n", "", body, count=1)
    title = pg["meta"]["title"]
    body = re.sub(r"^## Pages\n(?:- \[[^\]]+\]\([^)]+\)\n?)+", "", body, flags=re.M).strip()
    h = "#" if top else "##"
    body = re.sub(r"^(#{2,5}) ", lambda m: "#" * (len(m.group(1)) + (0 if top else 1)) + " ", body, flags=re.M)
    return f'<a id="{slug}"></a>\n\n{h} {title}\n\n{conv(body, pg["path"])}\n'

parts = ["# System design guide: integrating independent OSDM modules", "",
         "Technology-neutral guide for architects and developers. Generated from the atomic pages in `wiki/` by `scripts/build_guide.py`; edit the pages, not this file.", ""]
toc = ["## Contents", ""]
chunks = []
hubs = sorted(s for s in pages if s.startswith("guide-"))
seen = set()
for hub in hubs:
    chunks.append(render(hub, True))
    toc.append(f"- [{pages[hub]['meta']['title']}](#{hub})")
    hub_path = pages[hub]["path"]
    for line in pages[hub]["body"].splitlines():
        if not line.startswith("- "):
            continue
        match = MD_LINK.fullmatch(line[2:].strip())
        if not match:
            continue
        page = linked_page(hub_path, match.group(2))
        slug = page["path"].stem if page else None
        if slug and slug in pages:
            chunks.append(render(slug, False)); seen.add(slug)
            toc.append(f"  - [{pages[slug]['meta']['title']}](#{slug})")
# normalise: hubs are H1 inside the doc, children H2, their subsections H3+
(ROOT / "System design guide.md").write_text("\n".join(parts + toc + [""] + chunks), encoding="utf-8")

missing = [s for s, p in pages.items() if p["meta"].get("type") not in ("source", "guide") and s not in seen]
print(f"pages={len(pages)} in_guide={len(seen)} not_in_guide={missing}")
