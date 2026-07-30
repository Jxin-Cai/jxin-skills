#!/usr/bin/env python3
"""tech-article-writer 升级能力回归测试。"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_article_quality import ArticleQualityChecker
from extract_style import analyze_style, dump_yaml
from format_citations import apply_references, validate_citations
from humanize_check import AIPatternDetector
from shared import detect_article_type, extract_title
from version_manager import VersionManager


class SharedUtilitiesTest(unittest.TestCase):
    def test_article_metadata(self):
        content = "# 缓存优化实践\n\n这是一次性能优化项目复盘。"
        self.assertEqual(extract_title(content), "缓存优化实践")
        self.assertEqual(detect_article_type(content), "问题解决型")


class HumanizeCheckTest(unittest.TestCase):
    def test_template_language_scores_higher(self):
        templated = (
            "在当今技术快速发展的背景下，值得注意的是，缓存至关重要。"
            "首先它能够赋能业务，其次能够构建生态闭环，最后具有重要意义。"
        ) * 8
        concrete = (
            "接口的 P99 延迟从 820 毫秒降到 190 毫秒。"
            "改动只有两处：把用户配置缓存 30 秒，并在写入后主动失效缓存。"
            "压测使用同一批请求回放三次，结果波动小于 4%。"
        ) * 8
        self.assertGreater(
            AIPatternDetector(templated).analyze()["score"],
            AIPatternDetector(concrete).analyze()["score"],
        )


class CitationTest(unittest.TestCase):
    def setUp(self):
        self.cards = [
            {
                "id": 1,
                "source_name": "官方文档",
                "title": "缓存指南",
                "source_url": "https://example.com/cache",
            },
            {
                "id": 2,
                "source_name": "工程团队",
                "title": "延迟复盘",
                "source_url": "https://example.com/latency",
            },
        ]

    def test_validate_and_format_citations(self):
        article = "# 标题\n\n缓存命中率达到 90%[1]，P99 延迟降低 60%[2]。\n"
        validation = validate_citations(article, self.cards)
        self.assertTrue(validation["valid"])
        formatted, result = apply_references(article, self.cards)
        self.assertTrue(result["valid"])
        self.assertIn("## 参考引用", formatted)
        self.assertIn("https://example.com/cache", formatted)

    def test_citation_gap_fails(self):
        validation = validate_citations("# 标题\n\n结论[2]。", self.cards)
        self.assertFalse(validation["valid"])
        self.assertEqual(validation["citation_gaps"], [1])


class StyleExtractionTest(unittest.TestCase):
    def test_profile_is_valid_yaml_subset(self):
        content = (
            "想象一下，你正在排查一个延迟问题。它就像堵在收费站前的车流。\n\n"
            "解决办法很直接：先量化，再修改，最后复测。"
        ) * 4
        profile = analyze_style([content])
        rendered = dump_yaml(profile)
        self.assertIn("tone:", rendered)
        self.assertIn("sentence_max_length:", rendered)
        self.assertGreaterEqual(profile["sample_size"], 1)


class VersionManagerTest(unittest.TestCase):
    def test_snapshot_diff_and_rollback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            article = root / "article.md"
            store = root / "versions"
            article.write_text("# 标题\n\n## 第一节\n\n旧内容\n", encoding="utf-8")
            manager = VersionManager(article, store)
            version = manager.snapshot("初始版本")
            article.write_text("# 标题\n\n## 第一节\n\n新内容\n", encoding="utf-8")
            diff_text, summary = manager.diff(version)
            self.assertIn("新内容", diff_text)
            self.assertEqual(summary["added_lines"], 1)
            backup = manager.rollback(version)
            self.assertGreater(backup, version)
            self.assertIn("旧内容", article.read_text(encoding="utf-8"))


class QualityCheckerTest(unittest.TestCase):
    def test_report_contains_upgrade_gates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            article = root / "article.md"
            article.write_text(
                "# 缓存实践\n\n"
                "## 场景引入\n\n线上延迟突然升高。\n\n"
                "## 核心概念\n\n缓存保存短期可复用结果。\n\n"
                "## 深度解析\n\n失效策略决定一致性。\n\n"
                "## 案例实践\n\n```python\nprint('ok')\n```\n\n"
                "## 总结\n\n先测量，再修改。\n",
                encoding="utf-8",
            )
            report = ArticleQualityChecker(str(article)).check_all()
            self.assertEqual(
                set(report["checks"]),
                {"basic", "markdown", "structure", "content", "ai_patterns", "citations", "style"},
            )
            json.dumps(report, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
