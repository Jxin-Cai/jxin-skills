#!/usr/bin/env python3
"""检测中文技术文章中的常见 AI 写作模式。"""

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from shared import count_chinese_chars, read_article


PATTERNS: Dict[str, Tuple[int, Sequence[str]]] = {
    "high": (
        5,
        (
            "值得注意的是", "综上所述", "不可或缺", "至关重要", "应运而生",
            "方兴未艾", "不言而喻", "毋庸置疑", "具有重要意义", "在当今",
            "本文将从", "赋能", "拥抱变化", "生态闭环", "降维打击", "范式",
            "深刻洞察", "全面提升", "显著提高", "强大能力", "坚实基础",
            "广泛应用", "巨大潜力", "革命性", "颠覆性", "无缝衔接",
        ),
    ),
    "medium": (
        3,
        (
            "本质上", "从某种意义上说", "事实上", "进一步来说", "与此同时",
            "在此基础上", "值得一提的是", "从这个角度来看", "不难发现",
            "显而易见", "可以看出", "由此可见", "在这一过程中", "从而实现",
            "有效地", "有助于", "旨在", "助力", "推动", "构建起",
        ),
    ),
    "low": (
        2,
        (
            "总的来说", "换句话说", "简单来说", "归根结底", "诚然",
            "毫无疑问", "众所周知", "一般而言", "相较而言", "可以说",
            "一方面", "另一方面", "首先", "其次", "最后",
        ),
    ),
}

TRANSITIONS = tuple(term for _, terms in PATTERNS.values() for term in terms)


@dataclass
class PatternHit:
    category: str
    pattern: str
    count: int
    weight: int
    raw_score: int
    suggestion: str


class AIPatternDetector:
    """按词汇、结构和节奏三个维度审计文章。"""

    def __init__(self, content: str):
        self.content = content
        self.plain_text = self._strip_non_prose(content)
        self.char_count = max(1, count_chinese_chars(self.plain_text))

    @staticmethod
    def _strip_non_prose(content: str) -> str:
        text = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        text = re.sub(r"`[^`]+`", "", text)
        text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^>.*$", "", text, flags=re.MULTILINE)
        return text

    def detect_vocabulary(self) -> List[PatternHit]:
        hits: List[PatternHit] = []
        for tier, (weight, terms) in PATTERNS.items():
            for term in terms:
                count = self.plain_text.count(term)
                if count:
                    hits.append(PatternHit(
                        category=f"vocabulary:{tier}",
                        pattern=term,
                        count=count,
                        weight=weight,
                        raw_score=count * weight,
                        suggestion="删除套话，或改成具体事实、动作与结果。",
                    ))
        return hits

    def detect_structural_patterns(self) -> List[PatternHit]:
        hits: List[PatternHit] = []
        paragraphs = [
            re.sub(r"\s+", "", paragraph)
            for paragraph in re.split(r"\n\s*\n", self.plain_text)
            if count_chinese_chars(paragraph) >= 30
        ]

        symmetric_runs = 0
        for index in range(len(paragraphs) - 2):
            lengths = [count_chinese_chars(p) for p in paragraphs[index:index + 3]]
            average = sum(lengths) / 3
            if average and max(abs(length - average) / average for length in lengths) <= 0.1:
                symmetric_runs += 1
        if symmetric_runs:
            hits.append(PatternHit(
                category="structure:symmetry",
                pattern="连续段落长度过度对称",
                count=symmetric_runs,
                weight=4,
                raw_score=symmetric_runs * 4,
                suggestion="打散段落节奏：合并短解释，拆出关键结论，避免机械等长。",
            ))

        sentence_starts = re.findall(r"(?:^|[。！？\n])\s*([一-鿿]{2,6})", self.plain_text)
        repeated_starts = sum(count - 2 for count in _frequencies(sentence_starts).values() if count >= 3)
        if repeated_starts:
            hits.append(PatternHit(
                category="structure:parallelism",
                pattern="连续句式或句首重复",
                count=repeated_starts,
                weight=4,
                raw_score=repeated_starts * 4,
                suggestion="改变主语和句式，让论证自然推进，不要连续使用同一模板。",
            ))

        transition_count = sum(self.plain_text.count(term) for term in TRANSITIONS)
        density = transition_count / max(1, self.char_count / 1000)
        if density > 8:
            excess = max(1, round(density - 8))
            hits.append(PatternHit(
                category="style:transition-density",
                pattern="过渡词密度过高",
                count=transition_count,
                weight=2,
                raw_score=excess * 2,
                suggestion="删除可由上下文自然表达的连接词，用因果与例子连接段落。",
            ))

        mechanical = min(
            self.plain_text.count("首先"),
            self.plain_text.count("其次"),
            self.plain_text.count("最后"),
        )
        if mechanical >= 2:
            hits.append(PatternHit(
                category="structure:mechanical-enumeration",
                pattern="首先/其次/最后机械列举",
                count=mechanical,
                weight=3,
                raw_score=mechanical * 3,
                suggestion="改用有语义的小标题，或让步骤由实际依赖关系串联。",
            ))
        return hits

    def analyze(self) -> Dict[str, object]:
        hits = self.detect_vocabulary() + self.detect_structural_patterns()
        raw_score = sum(hit.raw_score for hit in hits)
        normalization = max(1.0, math.log2(max(100, self.char_count) / 100))
        score = min(100, round(raw_score / normalization))
        level = "优秀" if score <= 20 else "良好" if score <= 40 else "需修改" if score <= 60 else "严重"
        return {
            "char_count": self.char_count,
            "raw_score": raw_score,
            "score": score,
            "level": level,
            "hits": [asdict(hit) for hit in sorted(hits, key=lambda item: item.raw_score, reverse=True)],
            "two_pass": {
                "pass_1": "按高权重到低权重逐项重写，优先用事实、场景和结果替换套话。",
                "pass_2": "重新阅读全文，检查重写是否引入新套话、逻辑跳跃或语气失真。",
            },
        }


def _frequencies(items: Sequence[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result


def print_report(report: Dict[str, object], verbose: bool = False) -> None:
    icon = "✅" if int(report["score"]) <= 40 else "⚠️"
    print(f"{icon} AI 痕迹评分: {report['score']}/100（{report['level']}）")
    print(f"📝 检测正文: {report['char_count']} 个中文字符")
    hits = report["hits"]
    if not hits:
        print("✅ 未发现显著 AI 写作模式")
        return
    display_hits = hits if verbose else hits[:8]
    for hit in display_hits:
        print(f"- [{hit['category']}] {hit['pattern']} × {hit['count']} (+{hit['raw_score']})")
        if verbose:
            print(f"  建议: {hit['suggestion']}")
    if len(hits) > len(display_hits):
        print(f"... 另有 {len(hits) - len(display_hits)} 项，使用 --verbose 查看")


def main() -> int:
    parser = argparse.ArgumentParser(description="检测中文技术文章中的 AI 写作模式")
    parser.add_argument("--article-file", required=True, help="Markdown 文章路径")
    parser.add_argument("--report", help="JSON 报告输出路径")
    parser.add_argument("--threshold", type=int, default=40, help="通过阈值，默认 40")
    parser.add_argument("--verbose", action="store_true", help="显示全部命中与建议")
    args = parser.parse_args()

    article_file = Path(args.article_file)
    if not article_file.exists():
        print(f"❌ 文件不存在: {article_file}")
        return 1

    report = AIPatternDetector(read_article(article_file)).analyze()
    print_report(report, args.verbose)
    if args.report:
        report_file = Path(args.report)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"💾 报告已保存: {report_file}")
    return 0 if int(report["score"]) <= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
