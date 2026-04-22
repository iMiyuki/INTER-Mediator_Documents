#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


_TITLE_START_RE = re.compile(r"^第(?P<num>\d+)回は、")
_URL_RE = re.compile(r"https?://\S+")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {path}") from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied: {path}") from e


def _extract_title_blocks(text: str) -> list[str]:
    lines = [ln.rstrip() for ln in text.splitlines()]

    blocks: list[list[str]] = []
    current: list[str] = []

    for ln in lines:
        if not ln.strip():
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(ln.strip())

    if current:
        blocks.append(current)

    title_lines: list[str] = []
    for b in blocks:
        if not b:
            continue
        if not _TITLE_START_RE.match(b[0]):
            continue
        joined = " ".join(b).strip()
        title_lines.append(joined)

    return title_lines


def _extract_urls(text: str) -> list[str]:
    urls: list[str] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        m = _URL_RE.search(ln)
        if not m:
            continue
        urls.append(m.group(0))
    return urls


def _write_lines(path: Path, lines: list[str], mode: str) -> None:
    if mode == "overwrite":
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return

    # append
    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"

    out = existing + "\n".join(lines) + ("\n" if lines else "")
    path.write_text(out, encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="discord_to_titles_urls.py",
        description=(
            "Extract title blocks (starting with '第NN回は、') and URLs from a pasted Discord text."
        ),
    )
    parser.add_argument("input", help="Path to a text file copied from Discord")
    parser.add_argument("--titles", default="titles.txt", help="Output titles file path")
    parser.add_argument("--urls", default="urls.txt", help="Output urls file path")
    parser.add_argument(
        "--mode",
        choices=["append", "overwrite"],
        default="append",
        help="How to write output files",
    )
    args = parser.parse_args(argv[1:])

    input_path = Path(args.input).expanduser().resolve()
    titles_path = Path(args.titles).expanduser().resolve()
    urls_path = Path(args.urls).expanduser().resolve()

    try:
        text = _read_text(input_path)
    except (FileNotFoundError, PermissionError) as e:
        print(str(e), file=sys.stderr)
        return 2

    title_lines = _extract_title_blocks(text)
    url_lines = _extract_urls(text)

    if not title_lines:
        print("No title blocks found (lines starting with '第NN回は、').", file=sys.stderr)
        return 2
    if not url_lines:
        print("No URLs found.", file=sys.stderr)
        return 2

    if len(title_lines) != len(url_lines):
        print(
            f"Line count mismatch: titles={len(title_lines)} urls={len(url_lines)} (must match)",
            file=sys.stderr,
        )
        return 2

    _write_lines(titles_path, title_lines, args.mode)
    _write_lines(urls_path, url_lines, args.mode)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
