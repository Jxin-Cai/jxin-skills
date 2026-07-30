#!/usr/bin/env python3
"""统一检查技术文章的格式、结构、内容、引用、风格与 AI 痕迹。"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from humanize_check import AIPatternDetector
from shared import (
    count_chinese_chars,
    detect_article_type,
    estimate_reading_time,
    extract_h2_headings,
    extract_title,
    read_article,
)


class ArticleQualityChecker:
    """文章质量检查器。"""

    def __init__(
        self,
        article_file: str,
        style_profile: Optional[str] = None,
        ai_threshold: int = 40,
    ):
        self.article_file = Path(article_file)
        self.article_content = read_article(self.article_file)
        self.style_profile = Path(style_profile) if style_profile else None
        self.ai_threshold = ai_threshold

    def check_all(self) -> Dict[str, object]:
        """执行所有检查并生成综合结果。"""
        checks = {
            "basic": self.check_basic_info(),
            "markdown": self.check_markdown_format(),
            "structure": self.check_article_structure(),
            "content": self.check_content_quality(),
            "ai_patterns": self.check_ai_patterns(),
            "citations": self.check_citations(),
            "style": self.check_style_profile(),
        }
        passed = all(result["passed"] for result in checks.values())
        return {
            "article_file": str(self.article_file),
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "passed": passed,
            "checks": checks,
        }

    def check_basic_info(self) -> Dict[str, object]:
        """统计标题、类型、字数与阅读时长。"""
        char_count = count_chinese_chars(self.article_content)
        title = extract_title(self.article_content)
        issues: List[str] = []
        if title == "未命名文章":
            issues.append("缺少一级标题")
        if char_count < 1200:
            issues.append(f"正文偏短：{char_count} 字，建议至少 1200 字")
        if char_count > 8000:
            issues.append(f"正文偏长：{char_count} 字，建议拆分或启用动态大纲")
        return {
            "passed": title != "未命名文章" and char_count >= 1200,
            "title": title,
            "article_type": detect_article_type(self.article_content),
            "chinese_chars": char_count,
            "reading_minutes": round(estimate_reading_time(self.article_content), 1),
            "issues": issues,
        }

    def check_markdown_format(self) -> Dict[str, object]:
        """检查标题、代码块、列表与图片格式。"""
        issues: List[str] = []
        h1_count = len(re.findall(r"^#\s+.+$", self.article_content, re.MULTILINE))
        if h1_count != 1:
            issues.append(f"一级标题应恰好 1 个，当前为 {h1_count} 个")
        if self.article_content.count("```") % 2:
            issues.append("代码块围栏未成对闭合")
        if re.search(r"^\s*[-*]\s*\[[xX ]\]\s*$", self.article_content, re.MULTILINE):
            issues.append("发现空的任务列表项")
        image_issues = [
            match.group(0)
            for match in re.finditer(r"!\[\]\([^)]*\)", self.article_content)
        ]
        if image_issues:
            issues.append("存在缺少 alt 文本的图片")
        return {
            "passed": not issues,
            "h1_count": h1_count,
            "h2_count": len(extract_h2_headings(self.article_content)),
            "code_block_count": self.article_content.count("```") // 2,
            "issues": issues,
        }

    def check_article_structure(self) -> Dict[str, object]:
        """检查黄金五段式或动态大纲的关键结构。"""
        headings = extract_h2_headings(self.article_content)
        issues: List[str] = []
        if len(headings) < 5:
            issues.append(f"二级章节不足：当前 {len(headings)} 个，建议至少 5 个")

        structure_signals = {
            "introduction": ("开场", "引言", "场景", "背景", "为什么"),
            "concept": ("概念", "是什么", "原理", "基础"),
            "analysis": ("解析", "深入", "机制", "架构", "实现"),
            "practice": ("实践", "案例", "实战", "示例", "代码"),
            "conclusion": ("总结", "结语", "升华", "展望"),
        }
        matched = {
            name: any(any(keyword in heading for keyword in keywords) for heading in headings)
            for name, keywords in structure_signals.items()
        }
        missing = [name for name, found in matched.items() if not found]
        if len(missing) >= 3:
            issues.append("章节语义未体现黄金五段式，也未展示明确的动态大纲结构")
        return {
            "passed": len(headings) >= 5 and len(missing) < 3,
            "headings": headings,
            "matched_sections": matched,
            "issues": issues,
        }

    def check_content_quality(self) -> Dict[str, object]:
        """检查代码示例、段落节奏和未完成占位符。"""
        issues: List[str] = []
        placeholders = re.findall(r"\[(?:请|待|TODO|示例|标题|内容)[^\]]*\]", self.article_content, re.IGNORECASE)
        if placeholders:
            issues.append(f"存在 {len(placeholders)} 个未完成占位符")

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", self.article_content)
            if count_chinese_chars(paragraph) >= 20 and not paragraph.lstrip().startswith(("#", ">", "```"))
        ]
        long_paragraphs = [p for p in paragraphs if count_chinese_chars(p) > 350]
        if long_paragraphs:
            issues.append(f"存在 {len(long_paragraphs)} 个超过 350 字的长段落")

        code_blocks = re.findall(r"```[^\n]*\n.*?```", self.article_content, re.DOTALL)
        if not code_blocks:
            issues.append("技术文章没有代码或命令示例")
        return {
            "passed": not placeholders and bool(code_blocks),
            "placeholder_count": len(placeholders),
            "long_paragraph_count": len(long_paragraphs),
            "code_block_count": len(code_blocks),
            "issues": issues,
        }

    def check_ai_patterns(self) -> Dict[str, object]:
        """复用三层权重检测器检查 AI 写作模式。"""
        report = AIPatternDetector(self.article_content).analyze()
        score = int(report["score"])
        top_hits = report["hits"][:8]
        issues = [
            f"AI 痕迹评分 {score} 高于阈值 {self.ai_threshold}"
        ] if score > self.ai_threshold else []
        return {
            "passed": score <= self.ai_threshold,
            "score": score,
            "threshold": self.ai_threshold,
            "level": report["level"],
            "top_hits": top_hits,
            "issues": issues,
        }

    def check_citations(self) -> Dict[str, object]:
        """检查正文引用编号和文末参考引用是否对应。"""
        body, _, reference_section = self.article_content.partition("## 参考引用")
        used = sorted({int(value) for value in re.findall(r"(?<!\])\[(\d+)\](?!\()", body)})
        listed = sorted({int(value) for value in re.findall(r"^\[(\d+)\]\s+", reference_section, re.MULTILINE)})
        issues: List[str] = []
        if used:
            expected = list(range(1, max(used) + 1))
            gaps = [number for number in expected if number not in used]
            missing = [number for number in used if number not in listed]
            if gaps:
                issues.append(f"正文引用编号不连续：缺少 {gaps}")
            if missing:
                issues.append(f"参考引用节缺少编号：{missing}")
            if not reference_section:
                issues.append("正文有引用标记，但缺少参考引用节")
        elif reference_section.strip():
            issues.append("参考引用节存在条目，但正文没有引用标记")
        return {
            "passed": not issues,
            "used": used,
            "listed": listed,
            "issues": issues,
            "note": "文章未使用外部引用" if not used and not reference_section.strip() else "",
        }

    def check_style_profile(self) -> Dict[str, object]:
        """检查 profile 中可确定验证的句长、段长和禁用词。"""
        if not self.style_profile:
            return {
                "passed": True,
                "profile": None,
                "issues": [],
                "note": "未指定 profile，按 SKILL.md 默认风格执行人工审校",
            }
        if not self.style_profile.exists():
            return {
                "passed": False,
                "profile": str(self.style_profile),
                "issues": ["风格 profile 不存在"],
            }

        profile_text = self.style_profile.read_text(encoding="utf-8")
        sentence_limit = self._yaml_int(profile_text, "sentence_max_length", 45)
        paragraph_limit = self._yaml_int(profile_text, "paragraph_max_sentences", 6)
        forbidden = self._yaml_list(profile_text, "forbidden_phrases")
        plain = re.sub(r"```.*?```", "", self.article_content, flags=re.DOTALL)
        sentences = [count_chinese_chars(item) for item in re.split(r"[。！？]", plain) if count_chinese_chars(item) >= 4]
        paragraphs = [item for item in re.split(r"\n\s*\n", plain) if count_chinese_chars(item) >= 20]
        too_long_sentences = sum(length > sentence_limit for length in sentences)
        too_long_paragraphs = sum(len(re.findall(r"[。！？]", item)) > paragraph_limit for item in paragraphs)
        forbidden_hits = {term: plain.count(term) for term in forbidden if term and term in plain}
        issues: List[str] = []
        if forbidden_hits:
            issues.append(f"命中禁用表达：{forbidden_hits}")
        if too_long_sentences > max(3, len(sentences) // 10):
            issues.append(f"超过句长软上限的句子过多：{too_long_sentences} 句")
        if too_long_paragraphs:
            issues.append(f"超过段落句数上限：{too_long_paragraphs} 段")
        return {
            "passed": not issues,
            "profile": str(self.style_profile),
            "sentence_limit": sentence_limit,
            "paragraph_limit": paragraph_limit,
            "forbidden_hits": forbidden_hits,
            "issues": issues,
        }

    @staticmethod
    def _yaml_int(content: str, key: str, default: int) -> int:
        match = re.search(rf"^{re.escape(key)}:\s*(\d+)\s*$", content, re.MULTILINE)
        return int(match.group(1)) if match else default

    @staticmethod
    def _yaml_list(content: str, key: str) -> List[str]:
        match = re.search(
            rf"^{re.escape(key)}:\s*\n((?:\s+-\s+.*\n?)*)",
            content,
            re.MULTILINE,
        )
        if not match:
            return []
        return [
            item.strip().strip('"\'')
            for item in re.findall(r"^\s+-\s+(.+)$", match.group(1), re.MULTILINE)
        ]


def print_report(report: Dict[str, object]) -> None:
    """输出人类可读报告。"""
    print("\n" + "=" * 64)
    print("技术文章质量检查")
    print("=" * 64)
    labels = {
        "basic": "基础信息",
        "markdown": "Markdown 格式",
        "structure": "文章结构",
        "content": "内容质量",
        "ai_patterns": "AI 痕迹",
        "citations": "引用完整性",
        "style": "风格合规",
    }
    for name, result in report["checks"].items():
        icon = "✅" if result["passed"] else "❌"
        print(f"\n{icon} {labels[name]}")
        if name == "basic":
            print(f"   标题: {result['title']}")
            print(f"   类型: {result['article_type']}")
            print(f"   字数: {result['chinese_chars']}，阅读约 {result['reading_minutes']} 分钟")
        elif name == "ai_patterns":
            print(f"   评分: {result['score']}/100，阈值: {result['threshold']}")
        elif name == "citations":
            print(f"   正文引用: {result['used']}，参考列表: {result['listed']}")
        elif name == "style" and result.get("profile"):
            print(f"   Profile: {result['profile']}")
        for issue in result.get("issues", []):
            print(f"   - {issue}")
        if result.get("note"):
            print(f"   ℹ️ {result['note']}")
    print("\n" + ("✅ 质量门禁通过" if report["passed"] else "❌ 质量门禁未通过"))


def main() -> int:
    parser = argparse.ArgumentParser(description="检查技术文章质量")
    parser.add_argument("--article-file", required=True, help="Markdown 文章路径")
    parser.add_argument("--report", help="JSON 报告输出路径")
    parser.add_argument("--style-profile", help="风格 profile YAML 路径")
    parser.add_argument("--ai-threshold", type=int, default=40, help="AI 痕迹通过阈值，默认 40")
    args = parser.parse_args()

    article_file = Path(args.article_file)
    if not article_file.exists():
        print(f"❌ 文件不存在: {article_file}")
        return 1

    try:
        checker = ArticleQualityChecker(
            args.article_file,
            style_profile=args.style_profile,
            ai_threshold=args.ai_threshold,
        )
        report = checker.check_all()
    except (OSError, ValueError) as exc:
        print(f"❌ 质量检查失败: {exc}")
        return 1

    print_report(report)
    if args.report:
        report_file = Path(args.report)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"💾 报告已保存: {report_file}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
