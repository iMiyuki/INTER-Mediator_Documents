#!/usr/bin/env python3

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


INDENT = "                    "


@dataclass(frozen=True)
class Entry:
    number: int
    title: str
    url: str


_TITLE_RE = re.compile(r"^第(?P<num>\d+)回は、(?P<rest>.*)$")
_URL_RE = re.compile(r"https?://\S+")


def _read_nonempty_lines(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {path}") from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied: {path}") from e

    return [line.strip() for line in text.splitlines() if line.strip()]


def _parse_title_line(line: str) -> tuple[int, str]:
    m = _TITLE_RE.match(line)
    if not m:
        raise ValueError(f"Invalid line (missing '第NN回は、'): {line}")

    num = int(m.group("num"))
    rest = m.group("rest")

    parts = rest.split("、")
    if len(parts) < 2:
        raise ValueError(f"Invalid line (need at least 2 '、'): {line}")

    title = parts[0].strip()
    if not title:
        raise ValueError(f"Invalid line (empty title): {line}")

    return num, title


def _format_li(url: str, text: str, indent: str = INDENT) -> str:
    return f'{indent}<li><a href="{url}" target="_blank">{text}</a></li>'


def _extract_existing_urls_from_sequential_ol(html: str) -> set[str]:
    section_pos = html.find('id="sequential"')
    if section_pos < 0:
        raise ValueError('Cannot find section id="sequential"')

    ol_open = html.find("<ol", section_pos)
    if ol_open < 0:
        raise ValueError("Cannot find <ol> in sequential section")

    ol_start = html.find(">", ol_open)
    if ol_start < 0:
        raise ValueError("Malformed <ol> tag")

    ol_end = html.find("</ol>", ol_start)
    if ol_end < 0:
        raise ValueError("Cannot find </ol> for sequential section")

    ol_inner = html[ol_start + 1 : ol_end]

    urls = set()
    for m in re.finditer(r"href=\"(?P<url>[^\"]+)\"", ol_inner):
        urls.add(m.group("url"))
    return urls


def _insert_before_sequential_ol_close(html: str, insert_text: str) -> str:
    section_pos = html.find('id="sequential"')
    if section_pos < 0:
        raise ValueError('Cannot find section id="sequential"')

    ol_open = html.find("<ol", section_pos)
    if ol_open < 0:
        raise ValueError("Cannot find <ol> in sequential section")

    ol_end = html.find("</ol>", ol_open)
    if ol_end < 0:
        raise ValueError("Cannot find </ol> for sequential section")

    before = html[:ol_end]
    after = html[ol_end:]

    # Ensure insertion starts on a new line and ends with a new line
    if before and not before.endswith("\n"):
        before += "\n"
    if insert_text and not insert_text.endswith("\n"):
        insert_text += "\n"

    return before + insert_text + after


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="update_videos2025_sequential.py",
        description=(
            "Append new <li> links to the sequential list in videos2025.html, "
            "based on titles.txt and urls.txt. Existing items are kept as-is."
        ),
    )
    parser.add_argument("videos2025", help="Path to videos2025.html")
    parser.add_argument("titles", help="Path to titles.txt")
    parser.add_argument("urls", help="Path to urls.txt")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write file; only report what would be added",
    )
    args = parser.parse_args(argv[1:])

    videos2025_path = Path(args.videos2025).expanduser().resolve()
    titles_path = Path(args.titles).expanduser().resolve()
    urls_path = Path(args.urls).expanduser().resolve()

    try:
        title_lines = _read_nonempty_lines(titles_path)
        url_lines = _read_nonempty_lines(urls_path)
    except (FileNotFoundError, PermissionError) as e:
        print(str(e), file=sys.stderr)
        return 2

    try:
        parsed = [_parse_title_line(line) for line in title_lines]
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    if len(parsed) != len(url_lines):
        print(
            f"Line count mismatch: titles={len(parsed)} urls={len(url_lines)} (must match)",
            file=sys.stderr,
        )
        return 2

    entries = [Entry(number=num, title=title, url=url) for (num, title), url in zip(parsed, url_lines)]

    try:
        html = videos2025_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"File not found: {videos2025_path}", file=sys.stderr)
        return 2
    except PermissionError as e:
        print(f"Permission denied: {videos2025_path}", file=sys.stderr)
        return 2

    try:
        existing_urls = _extract_existing_urls_from_sequential_ol(html)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    new_entries = [e for e in entries if e.url not in existing_urls]

    if not new_entries:
        print("No new entries to add.")
        return 0

    insert_block = "\n".join(_format_li(e.url, e.title) for e in new_entries)

    if args.dry_run:
        print(insert_block)
        return 0

    try:
        updated = _insert_before_sequential_ol_close(html, insert_block)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    videos2025_path.write_text(updated, encoding="utf-8")

    print(f"Added {len(new_entries)} entries to sequential list: {videos2025_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
