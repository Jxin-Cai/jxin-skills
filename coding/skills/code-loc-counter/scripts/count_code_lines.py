#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    "coverage",
    "out",
    "vendor",
    "tmp",
    "temp",
}

TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs", "e2e", "integration"}

SPECIAL_FILENAMES = {
    "dockerfile": "Dockerfile",
    "makefile": "Makefile",
    "jenkinsfile": "Groovy",
}

LANGUAGE_BY_EXTENSION = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".cxx": "C++",
    ".go": "Go",
    ".h": "C/C++ Header",
    ".hpp": "C/C++ Header",
    ".html": "HTML",
    ".htm": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".lua": "Lua",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".php": "PHP",
    ".pl": "Perl",
    ".pm": "Perl",
    ".py": "Python",
    ".r": "R",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".scala": "Scala",
    ".scss": "SCSS",
    ".sh": "Shell",
    ".sql": "SQL",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".vue": "Vue",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".zig": "Zig",
}

@dataclass(frozen=True)
class CommentSpec:
    line_comments: tuple[str, ...] = ()
    block_comments: tuple[tuple[str, str], ...] = ()
    string_delims: tuple[str, ...] = ()
    triple_quotes: bool = False

COMMENT_SPECS = {
    "C": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "C#": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "C++": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "C/C++ Header": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "CSS": CommentSpec(block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Dockerfile": CommentSpec(line_comments=("#",), string_delims=("\"", "'")),
    "Go": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Groovy": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "HTML": CommentSpec(block_comments=(("<!--", "-->"),), string_delims=("\"", "'")),
    "Java": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "JavaScript": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'", "`")),
    "Kotlin": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Lua": CommentSpec(line_comments=("--",), block_comments=(("--[[", "]]"),), string_delims=("\"", "'")),
    "Makefile": CommentSpec(line_comments=("#",), string_delims=("\"", "'")),
    "Objective-C": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Objective-C++": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Perl": CommentSpec(line_comments=("#",), string_delims=("\"", "'")),
    "PHP": CommentSpec(line_comments=("//", "#"), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Python": CommentSpec(line_comments=("#",), string_delims=("\"", "'"), triple_quotes=True),
    "R": CommentSpec(line_comments=("#",), string_delims=("\"", "'")),
    "Ruby": CommentSpec(line_comments=("#",), block_comments=(("=begin", "=end"),), string_delims=("\"", "'")),
    "Rust": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "SCSS": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Scala": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Shell": CommentSpec(line_comments=("#",), string_delims=("\"", "'")),
    "SQL": CommentSpec(line_comments=("--", "#"), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "Swift": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
    "TypeScript": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'", "`")),
    "Vue": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"), ("<!--", "-->")), string_delims=("\"", "'", "`")),
    "XML": CommentSpec(block_comments=(("<!--", "-->"),), string_delims=("\"", "'")),
    "YAML": CommentSpec(line_comments=("#",), string_delims=("\"", "'")),
    "Zig": CommentSpec(line_comments=("//",), block_comments=(("/*", "*/"),), string_delims=("\"", "'")),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="count_code_lines.py",
        description="Count code lines in a project while excluding tests and comments.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Project directory or single file to scan.")
    parser.add_argument("--include-tests", action="store_true", help="Include test files in statistics.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON instead of text.")
    return parser.parse_args()


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def detect_git_root(target: Path) -> Path | None:
    base = target if target.is_dir() else target.parent
    result = run_git(["rev-parse", "--show-toplevel"], base)
    if result.returncode != 0:
        return None
    root = result.stdout.strip()
    return Path(root) if root else None


def list_git_files(target: Path, git_root: Path) -> list[Path] | None:
    try:
        relative = target.resolve().relative_to(git_root.resolve())
        pathspec = str(relative) or "."
    except ValueError:
        return None
    result = run_git(["ls-files", "-co", "--exclude-standard", "--full-name", "--", pathspec], git_root)
    if result.returncode != 0:
        return None
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        candidate = (git_root / line.strip()).resolve()
        if candidate.is_file():
            files.append(candidate)
    return files


def list_walk_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files: list[Path] = []
    for root, dirs, names in os.walk(target):
        dirs[:] = [name for name in dirs if name not in SKIP_DIR_NAMES]
        root_path = Path(root)
        for name in names:
            candidate = root_path / name
            if candidate.is_file():
                files.append(candidate.resolve())
    return files


def list_candidate_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target.resolve()]
    git_root = detect_git_root(target)
    if git_root is not None:
        files = list_git_files(target, git_root)
        if files is not None:
            return files
    return list_walk_files(target.resolve())


def has_skipped_dir(path: Path) -> bool:
    return any(part.lower() in SKIP_DIR_NAMES for part in path.parts[:-1])


def is_binary_file(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            chunk = handle.read(4096)
    except OSError:
        return True
    return b"\x00" in chunk


def detect_language(path: Path) -> str | None:
    special = SPECIAL_FILENAMES.get(path.name.lower())
    if special is not None:
        return special
    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower())


def is_test_file(path: Path) -> bool:
    lower_parts = [part.lower() for part in path.parts]
    if any(part in TEST_DIR_NAMES for part in lower_parts[:-1]):
        return True
    name = path.name.lower()
    stem = path.stem.lower()
    if ".test." in name or ".spec." in name:
        return True
    if stem.startswith("test_") or stem.endswith("_test"):
        return True
    return False


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def count_code_lines(text: str, spec: CommentSpec) -> int:
    line_comments = tuple(sorted(spec.line_comments, key=len, reverse=True))
    block_comments = tuple(sorted(spec.block_comments, key=lambda item: len(item[0]), reverse=True))
    i = 0
    length = len(text)
    total = 0
    line_has_code = False
    block_end: str | None = None
    string_delim: str | None = None
    triple_string = False
    in_line_comment = False

    while i < length:
        if in_line_comment:
            if text[i] == "\n":
                if line_has_code:
                    total += 1
                line_has_code = False
                in_line_comment = False
            i += 1
            continue

        if block_end is not None:
            if text.startswith(block_end, i):
                i += len(block_end)
                block_end = None
                continue
            if text[i] == "\n":
                if line_has_code:
                    total += 1
                line_has_code = False
            i += 1
            continue

        if string_delim is not None:
            if triple_string and text.startswith(string_delim * 3, i):
                i += 3
                string_delim = None
                triple_string = False
                continue
            if text[i] == "\\":
                i += 2
                continue
            if not triple_string and text[i] == string_delim:
                i += 1
                string_delim = None
                continue
            if text[i] == "\n":
                if line_has_code:
                    total += 1
                line_has_code = True
                i += 1
                continue
            i += 1
            continue

        if text[i] == "\n":
            if line_has_code:
                total += 1
            line_has_code = False
            i += 1
            continue

        if text[i].isspace():
            i += 1
            continue

        matched = False
        if spec.triple_quotes:
            if text.startswith("'''", i):
                line_has_code = True
                string_delim = "'"
                triple_string = True
                i += 3
                continue
            if text.startswith('"""', i):
                line_has_code = True
                string_delim = '"'
                triple_string = True
                i += 3
                continue

        for marker in line_comments:
            if text.startswith(marker, i):
                in_line_comment = True
                i += len(marker)
                matched = True
                break
        if matched:
            continue

        for start, end in block_comments:
            if text.startswith(start, i):
                block_end = end
                i += len(start)
                matched = True
                break
        if matched:
            continue

        if text[i] in spec.string_delims:
            line_has_code = True
            string_delim = text[i]
            triple_string = False
            i += 1
            continue

        line_has_code = True
        i += 1

    if line_has_code:
        total += 1
    return total


def render_text(result: dict) -> str:
    lines = [
        f"扫描路径: {result['target']}",
        f"总代码行数: {result['total_code_lines']}",
        f"扫描文件数: {result['scanned_files']}",
        f"跳过测试文件数: {result['skipped_test_files']}",
        f"跳过 unknown / unsupported 文件数: {result['skipped_unknown_files']}",
        f"跳过二进制文件数: {result['skipped_binary_files']}",
        "",
        "按语言明细:",
    ]
    if result["languages"]:
        for item in result["languages"]:
            lines.append(f"- {item['language']}: {item['code_lines']}")
    else:
        lines.append("- 无可统计的代码文件")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        raise SystemExit(f"ERROR: path not found: {target}")

    counts = Counter()
    scanned_files = 0
    skipped_test_files = 0
    skipped_unknown_files = 0
    skipped_binary_files = 0

    base_path = target if target.is_dir() else target.parent

    for path in list_candidate_files(target):
        relative_path = path.relative_to(base_path)
        if target.is_dir() and has_skipped_dir(relative_path):
            continue
        if is_test_file(relative_path) and not args.include_tests:
            skipped_test_files += 1
            continue
        language = detect_language(path)
        if language is None:
            skipped_unknown_files += 1
            continue
        if is_binary_file(path):
            skipped_binary_files += 1
            continue
        text = read_text(path)
        spec = COMMENT_SPECS.get(language)
        if spec is None:
            skipped_unknown_files += 1
            continue
        counts[language] += count_code_lines(text, spec)
        scanned_files += 1

    languages = [
        {"language": language, "code_lines": code_lines}
        for language, code_lines in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    result = {
        "target": str(target),
        "total_code_lines": sum(counts.values()),
        "scanned_files": scanned_files,
        "skipped_test_files": skipped_test_files,
        "skipped_unknown_files": skipped_unknown_files,
        "skipped_binary_files": skipped_binary_files,
        "languages": languages,
    }

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
