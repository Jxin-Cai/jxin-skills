"""文章读取、识别与统计工具。"""

import re
from pathlib import Path
from typing import List, Union

from .constants import ARTICLE_TYPE_KEYWORDS, DEFAULT_ARTICLE_TYPE, DEFAULT_READING_SPEED

PathLike = Union[str, Path]


def read_article(article_file: PathLike) -> str:
    """读取 UTF-8 Markdown 文章。"""
    return Path(article_file).read_text(encoding="utf-8")


def extract_title(content: str) -> str:
    """提取第一个一级标题。"""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else "未命名文章"


def detect_article_type(content: str) -> str:
    """按现有优先级根据标题与正文关键词识别文章类型。"""
    haystack = content.lower()
    for article_type, keywords in ARTICLE_TYPE_KEYWORDS.items():
        if any(keyword.lower() in haystack for keyword in keywords):
            return article_type
    return DEFAULT_ARTICLE_TYPE


def count_chinese_chars(content: str) -> int:
    """统计中文字符数。"""
    return len(re.findall(r"[一-鿿]", content))


def estimate_reading_time(content: str, chars_per_minute: int = DEFAULT_READING_SPEED) -> float:
    """估算中文阅读时长（分钟）。"""
    if chars_per_minute <= 0:
        raise ValueError("chars_per_minute 必须大于 0")
    return count_chinese_chars(content) / chars_per_minute


def extract_h2_headings(content: str) -> List[str]:
    """提取所有二级标题。"""
    return [heading.strip() for heading in re.findall(r"^##\s+(.+)$", content, re.MULTILINE)]
