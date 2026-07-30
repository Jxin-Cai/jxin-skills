#!/usr/bin/env python3
"""从历史 Markdown 文章提取可复用的写作风格指纹。"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

sys.path.insert(0, str(Path(__file__).parent))
from shared import count_chinese_chars, read_article


ANALOGY_MARKERS = ("就像", "好比", "如同", "可以把", "仿佛", "相当于")
HUMOR_MARKERS = ("笑", "别急", "翻车", "踩坑", "玄学", "打脸", "瑞士军刀", "银弹")
FORMAL_MARKERS = ("因此", "此外", "基于", "本文", "如下", "即")
CASUAL_MARKERS = ("你", "咱们", "说白了", "别", "其实", "想象一下")


def strip_markup(content: str) -> str:
    text = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"!\[[^]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    return text


def percentile(values: Sequence[int], ratio: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * ratio))]


def extract_signature_phrases(texts: Sequence[str], limit: int = 8) -> List[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        compact = re.sub(r"\s+", "", text)
        unique = set()
        for length in range(4, 9):
            unique.update(re.findall(rf"[一-鿿]{{{length}}}", compact))
        counter.update(unique)
    stop_fragments = ("我们可以", "这个时候", "通过这种", "在这个", "的时候", "一个非常")
    return [
        phrase for phrase, count in counter.most_common()
        if count >= 2 and not any(fragment in phrase for fragment in stop_fragments)
    ][:limit]


def analyze_style(contents: Iterable[str]) -> Dict[str, object]:
    texts = [strip_markup(content) for content in contents]
    combined = "\n".join(texts)
    sentences = [segment.strip() for segment in re.split(r"[。！？!?]", combined) if count_chinese_chars(segment) >= 4]
    sentence_lengths = [count_chinese_chars(sentence) for sentence in sentences]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", combined) if count_chinese_chars(p) >= 10]
    paragraph_sentences = [max(1, len(re.findall(r"[。！？!?]", paragraph))) for paragraph in paragraphs]

    chinese_chars = max(1, count_chinese_chars(combined))
    analogy_count = sum(combined.count(marker) for marker in ANALOGY_MARKERS)
    humor_count = sum(combined.count(marker) for marker in HUMOR_MARKERS)
    formal_count = sum(combined.count(marker) for marker in FORMAL_MARKERS)
    casual_count = sum(combined.count(marker) for marker in CASUAL_MARKERS)

    analogy_density = analogy_count / (chinese_chars / 1000)
    humor_density = humor_count / (chinese_chars / 1000)
    if casual_count > formal_count * 1.2:
        tone = "professional-casual"
    elif formal_count > casual_count * 2:
        tone = "professional"
    else:
        tone = "balanced"

    return {
        "name": "自动提取风格",
        "tone": tone,
        "humor_level": min(10, round(humor_density * 2)),
        "analogy_density": "high" if analogy_density >= 3 else "medium" if analogy_density >= 1 else "low",
        "sentence_average_length": round(statistics.mean(sentence_lengths), 1) if sentence_lengths else 0,
        "sentence_max_length": percentile(sentence_lengths, 0.9),
        "paragraph_max_sentences": max(1, percentile(paragraph_sentences, 0.9)),
        "signature_phrases": extract_signature_phrases(texts),
        "forbidden_phrases": [],
        "code_comment_style": "chinese" if re.search(r"#\s*[一-鿿]", combined) else "mixed",
        "transition_style": "natural" if formal_count / (chinese_chars / 1000) < 8 else "explicit",
        "opening_preference": ["question", "case", "direct"],
        "sample_size": len(texts),
    }


def dump_yaml(data: Dict[str, object]) -> str:
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                lines.extend(f"  - {json.dumps(item, ensure_ascii=False)}" for item in value)
        elif isinstance(value, str):
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def collect_files(article_file: str, articles_dir: str) -> List[Path]:
    files: List[Path] = []
    if article_file:
        files.append(Path(article_file))
    if articles_dir:
        files.extend(sorted(Path(articles_dir).glob("*.md")))
    unique = list(dict.fromkeys(path.resolve() for path in files))
    return [path for path in unique if path.is_file()]


def main() -> int:
    parser = argparse.ArgumentParser(description="从文章中提取写作风格指纹")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--article-file", help="单篇 Markdown 文章")
    source.add_argument("--articles-dir", help="Markdown 文章目录")
    parser.add_argument("--output", required=True, help="YAML profile 输出路径")
    parser.add_argument("--compare", help="现有 profile 路径，仅用于报告")
    args = parser.parse_args()

    files = collect_files(args.article_file, args.articles_dir)
    if not files:
        print("❌ 未找到可分析的 Markdown 文章")
        return 1

    try:
        profile = analyze_style(read_article(path) for path in files)
    except OSError as exc:
        print(f"❌ 读取文章失败: {exc}")
        return 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dump_yaml(profile), encoding="utf-8")
    print(f"✅ 已分析 {len(files)} 篇文章")
    print(f"🎨 风格: {profile['tone']}，类比密度: {profile['analogy_density']}，幽默度: {profile['humor_level']}/10")
    print(f"💾 风格指纹已保存: {output}")
    if args.compare:
        compare = Path(args.compare)
        print(f"ℹ️ 可将输出与现有 profile 对照: {compare}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
