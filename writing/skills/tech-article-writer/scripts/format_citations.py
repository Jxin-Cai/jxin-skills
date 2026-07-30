#!/usr/bin/env python3
"""校验正文引用标记，并根据素材卡生成参考引用。"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from shared import read_article


CITATION_RE = re.compile(r"(?<!\])\[(\d+)\](?!\()")
REFERENCE_HEADING_RE = re.compile(r"\n##\s+参考引用\s*\n.*\Z", re.DOTALL)


def load_cards(path: Path) -> List[Dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cards = data.get("cards", data) if isinstance(data, dict) else data
    if not isinstance(cards, list):
        raise ValueError("素材卡 JSON 必须是数组或包含 cards 数组的对象")
    normalized = []
    for index, card in enumerate(cards, start=1):
        if not isinstance(card, dict) or not card.get("source_url"):
            raise ValueError(f"第 {index} 张素材卡缺少 source_url")
        item = dict(card)
        item["id"] = int(item.get("id", index))
        normalized.append(item)
    return normalized


def validate_citations(content: str, cards: Sequence[Dict[str, object]]) -> Dict[str, object]:
    body = REFERENCE_HEADING_RE.sub("", content)
    used = sorted({int(value) for value in CITATION_RE.findall(body)})
    available = sorted(int(card["id"]) for card in cards)
    missing_cards = [number for number in used if number not in available]
    unused_cards = [number for number in available if number not in used]
    expected = list(range(1, max(used, default=0) + 1))
    gaps = [number for number in expected if number not in used]
    return {
        "valid": not missing_cards and not gaps,
        "used": used,
        "available": available,
        "missing_cards": missing_cards,
        "unused_cards": unused_cards,
        "citation_gaps": gaps,
    }


def build_reference_section(cards: Sequence[Dict[str, object]], used: Sequence[int]) -> str:
    by_id = {int(card["id"]): card for card in cards}
    lines = ["## 参考引用", ""]
    for number in used:
        card = by_id[number]
        title = str(card.get("title") or card.get("source_name") or card.get("key_argument") or "参考资料")
        source = str(card.get("source_name") or "原始来源")
        url = str(card["source_url"])
        published = str(card.get("published_at") or "").strip()
        suffix = f"，{published}" if published else ""
        lines.append(f"[{number}] {source}：《{title}》{suffix}。{url}")
    return "\n".join(lines).rstrip() + "\n"


def apply_references(content: str, cards: Sequence[Dict[str, object]]) -> Tuple[str, Dict[str, object]]:
    validation = validate_citations(content, cards)
    if not validation["valid"]:
        return content, validation
    body = REFERENCE_HEADING_RE.sub("", content).rstrip()
    section = build_reference_section(cards, validation["used"])
    return f"{body}\n\n{section}", validation


def print_validation(validation: Dict[str, object]) -> None:
    if validation["valid"]:
        print(f"✅ 引用校验通过: {len(validation['used'])} 个正文引用")
    else:
        print("❌ 引用校验失败")
    if validation["missing_cards"]:
        print(f"- 缺少素材卡: {validation['missing_cards']}")
    if validation["citation_gaps"]:
        print(f"- 引用编号不连续: {validation['citation_gaps']}")
    if validation["unused_cards"]:
        print(f"ℹ️ 未使用素材卡: {validation['unused_cards']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验引用并生成参考引用节")
    parser.add_argument("--article-file", required=True, help="Markdown 文章路径")
    parser.add_argument("--citations", required=True, help="素材卡 JSON 路径")
    parser.add_argument("--output", help="输出路径；默认生成 *-cited.md")
    parser.add_argument("--validate-only", action="store_true", help="仅校验，不写文件")
    args = parser.parse_args()

    article_file = Path(args.article_file)
    citations_file = Path(args.citations)
    try:
        content = read_article(article_file)
        cards = load_cards(citations_file)
        formatted, validation = apply_references(content, cards)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"❌ 引用处理失败: {exc}")
        return 1

    print_validation(validation)
    if not validation["valid"] or args.validate_only:
        return 0 if validation["valid"] else 1

    output = Path(args.output) if args.output else article_file.with_name(f"{article_file.stem}-cited.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(formatted, encoding="utf-8")
    print(f"💾 引用版文章已保存: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
