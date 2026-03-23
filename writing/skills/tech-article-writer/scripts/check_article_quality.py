#!/usr/bin/env python3
"""
文章质量检查脚本

功能：
1. Markdown格式检查
2. 文章结构完整性检查
3. 内容质量评估
4. 生成质量报告

使用方法：
python check_article_quality.py --article-file article.md --report report.json
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class ArticleQualityChecker:
    """文章质量检查器"""
    
    def __init__(self, article_file: str):
        self.article_file = Path(article_file)
        self.article_content = self._read_article()
        self.errors = []
        self.warnings = []
        self.info = []
        
    def _read_article(self) -> str:
        """读取文章内容"""
        with open(self.article_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def check_all(self) -> Dict:
        """执行所有检查"""
        results = {
            "file": str(self.article_file),
            "checked_at": datetime.now().isoformat(),
            "checks": {}
        }
        
        # 1. Markdown格式检查
        results["checks"]["markdown_syntax"] = self._check_markdown_syntax()
        
        # 2. 文章结构检查
        results["checks"]["article_structure"] = self._check_article_structure()
        
        # 3. 内容质量检查
        results["checks"]["content_quality"] = self._check_content_quality()
        
        # 4. 必备元素检查
        results["checks"]["required_elements"] = self._check_required_elements()
        
        # 汇总结果
        results["summary"] = {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "info": len(self.info),
            "passed": len(self.errors) == 0
        }
        
        results["details"] = {
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }
        
        return results
    
    def _check_markdown_syntax(self) -> Dict:
        """检查Markdown语法"""
        issues = []
        
        # 1. 检查代码块配对
        code_blocks = re.findall(r'```', self.article_content)
        if len(code_blocks) % 2 != 0:
            self.errors.append({
                "type": "markdown_syntax",
                "severity": "error",
                "message": f"代码块未配对，发现{len(code_blocks)}个```标记（应为偶数）",
                "suggestion": "检查是否有代码块未闭合"
            })
            issues.append("代码块未配对")
        
        # 2. 检查代码块语言标识
        unnamed_blocks = re.findall(r'\n```\s*\n', self.article_content)
        if unnamed_blocks:
            self.warnings.append({
                "type": "markdown_syntax",
                "severity": "warning",
                "message": f"发现{len(unnamed_blocks)}个未指定语言的代码块",
                "suggestion": "为每个代码块添加语言标识（如```java）"
            })
            issues.append("代码块缺少语言标识")
        
        # 3. 检查列表格式
        bad_list_pattern = r'[^\n]\n[-*]\s+'
        bad_lists = re.findall(bad_list_pattern, self.article_content)
        if bad_lists:
            self.warnings.append({
                "type": "markdown_syntax",
                "severity": "warning",
                "message": f"发现{len(bad_lists)}处列表格式可能不正确",
                "suggestion": "确保列表前后有空行"
            })
            issues.append("列表格式")
        
        # 4. 检查标题层级
        headings = re.findall(r'^(#{1,6})\s+', self.article_content, re.MULTILINE)
        prev_level = 0
        for h in headings:
            level = len(h)
            if level > prev_level + 1 and prev_level > 0:
                self.warnings.append({
                    "type": "markdown_syntax",
                    "severity": "warning",
                    "message": f"标题层级跳跃：从{prev_level}级跳到{level}级",
                    "suggestion": "标题层级应连续递增"
                })
                issues.append("标题层级跳跃")
                break
            prev_level = level
        
        # 5. 检查文件结尾
        if not self.article_content.endswith('\n'):
            self.warnings.append({
                "type": "markdown_syntax",
                "severity": "warning",
                "message": "文件未以换行符结尾",
                "suggestion": "在文件末尾添加一个换行符"
            })
            issues.append("文件结尾格式")
        
        return {
            "passed": len([e for e in self.errors if e["type"] == "markdown_syntax"]) == 0,
            "issues_found": issues
        }
    
    def _check_article_structure(self) -> Dict:
        """检查文章结构"""
        issues = []
        
        # 检查黄金五段式结构
        required_sections = {
            "场景引入": False,
            "概念": False,  # 概念引出或破俗立新
            "深度": False,  # 深度阐释
            "应用": False,  # 举一反三
            "总结": False   # 总结回顾
        }
        
        # 提取所有二级标题
        h2_headings = re.findall(r'^##\s+(.+)$', self.article_content, re.MULTILINE)
        
        # 简单的关键词匹配
        for heading in h2_headings:
            heading_lower = heading.lower()
            if any(word in heading_lower for word in ['场景', '引入', '背景']):
                required_sections["场景引入"] = True
            if any(word in heading_lower for word in ['概念', '定义', '什么是']):
                required_sections["概念"] = True
            if any(word in heading_lower for word in ['深入', '原理', '机制', '工作']):
                required_sections["深度"] = True
            if any(word in heading_lower for word in ['应用', '实例', '例子', '案例']):
                required_sections["应用"] = True
            if any(word in heading_lower for word in ['总结', '回顾', '小结']):
                required_sections["总结"] = True
        
        # 检查缺失的部分
        missing_sections = [k for k, v in required_sections.items() if not v]
        if missing_sections:
            self.warnings.append({
                "type": "article_structure",
                "severity": "warning",
                "message": f"可能缺少以下结构部分: {', '.join(missing_sections)}",
                "suggestion": "确保文章包含黄金五段式的所有部分"
            })
            issues.extend(missing_sections)
        
        return {
            "passed": len(missing_sections) <= 1,  # 允许缺少一个部分
            "five_sections_complete": len(missing_sections) == 0,
            "missing_sections": missing_sections
        }
    
    def _check_content_quality(self) -> Dict:
        """检查内容质量"""
        issues = []
        
        # 1. 检查文章长度
        word_count = len(self.article_content)
        char_count_chinese = len(re.findall(r'[\u4e00-\u9fff]', self.article_content))
        
        # 估算阅读时长（中文400字/分钟）
        reading_time = char_count_chinese / 400
        
        if reading_time < 8:
            self.info.append({
                "type": "content_quality",
                "severity": "info",
                "message": f"文章较短，预计阅读时长{reading_time:.1f}分钟（目标8-12分钟）",
                "suggestion": "考虑增加内容深度或更多实例"
            })
            issues.append("文章偏短")
        elif reading_time > 12:
            self.info.append({
                "type": "content_quality",
                "severity": "info",
                "message": f"文章较长，预计阅读时长{reading_time:.1f}分钟（目标8-12分钟）",
                "suggestion": "考虑精简内容或拆分为多篇"
            })
            issues.append("文章偏长")
        
        # 2. 检查代码示例数量
        code_blocks = re.findall(r'```[\w]*\n.*?```', self.article_content, re.DOTALL)
        if len(code_blocks) < 3:
            self.warnings.append({
                "type": "content_quality",
                "severity": "warning",
                "message": f"代码示例较少（{len(code_blocks)}个），建议3-5个",
                "suggestion": "增加更多具体的代码示例"
            })
            issues.append("代码示例不足")
        
        # 3. 检查图表
        mermaid_diagrams = re.findall(r'```mermaid', self.article_content)
        plantuml_diagrams = re.findall(r'```plantuml', self.article_content)
        total_diagrams = len(mermaid_diagrams) + len(plantuml_diagrams)
        
        if total_diagrams == 0:
            self.warnings.append({
                "type": "content_quality",
                "severity": "warning",
                "message": "未发现Mermaid或PlantUML图表",
                "suggestion": "至少添加1个流程图或架构图"
            })
            issues.append("缺少图表")
        
        return {
            "passed": len([w for w in self.warnings if w["type"] == "content_quality"]) == 0,
            "reading_time_minutes": round(reading_time, 1),
            "code_blocks_count": len(code_blocks),
            "diagrams_count": total_diagrams,
            "issues_found": issues
        }
    
    def _check_required_elements(self) -> Dict:
        """检查必备元素"""
        issues = []
        
        # 1. 检查标准文章抬头
        has_author = re.search(r'\*\*文\s*\|\s*三七\*\*', self.article_content)
        if not has_author:
            self.errors.append({
                "type": "required_elements",
                "severity": "error",
                "message": "缺少标准作者信息",
                "suggestion": '添加"**文 | 三七**（转载请注明出处）"'
            })
            issues.append("作者信息")
        
        # 2. 检查产品口号
        has_motto = re.search(r'不积跬步无以至千里', self.article_content)
        if not has_motto:
            self.errors.append({
                "type": "required_elements",
                "severity": "error",
                "message": "缺少产品标识口号",
                "suggestion": '添加"> **不积跬步无以至千里，欢迎来到AI时代的编码实战课**"'
            })
            issues.append("产品口号")
        
        # 3. 检查封面图片提示词占位符
        has_cover_prompt = re.search(r'🎨\s*封面图片提示词', self.article_content)
        if not has_cover_prompt:
            self.warnings.append({
                "type": "required_elements",
                "severity": "warning",
                "message": "缺少封面图片提示词部分",
                "suggestion": "添加封面图片提示词占位符"
            })
            issues.append("封面提示词")
        
        # 4. 检查文章摘要
        has_summary = re.search(r'📝\s*文章摘要', self.article_content)
        if not has_summary:
            self.warnings.append({
                "type": "required_elements",
                "severity": "warning",
                "message": "缺少文章摘要部分",
                "suggestion": "添加文章摘要占位符"
            })
            issues.append("文章摘要")
        
        # 5. 检查知识图谱
        has_knowledge_graph = re.search(r'知识图谱|```mermaid', self.article_content)
        if not has_knowledge_graph:
            self.warnings.append({
                "type": "required_elements",
                "severity": "warning",
                "message": "缺少知识图谱",
                "suggestion": "在总结部分添加Mermaid知识图谱"
            })
            issues.append("知识图谱")
        
        # 6. 检查"一句话精华"
        has_key_message = re.search(r'如果今天你只记得一句话', self.article_content)
        if not has_key_message:
            self.warnings.append({
                "type": "required_elements",
                "severity": "warning",
                "message": "缺少'如果今天你只记得一句话'部分",
                "suggestion": "在总结部分添加一句话精华"
            })
            issues.append("一句话精华")
        
        # 7. 检查延伸阅读
        has_references = re.search(r'延伸阅读|参考文献|引用', self.article_content)
        if not has_references:
            self.warnings.append({
                "type": "required_elements",
                "severity": "warning",
                "message": "缺少延伸阅读部分",
                "suggestion": "添加3-5篇权威文章引用"
            })
            issues.append("延伸阅读")
        
        return {
            "passed": len([e for e in self.errors if e["type"] == "required_elements"]) == 0,
            "missing_elements": issues
        }
    
    def print_report(self):
        """打印质量报告"""
        results = self.check_all()
        
        print("\n" + "="*80)
        print(f"📋 文章质量检查报告")
        print("="*80)
        print(f"文件: {results['file']}")
        print(f"检查时间: {results['checked_at']}")
        print()
        
        # 总体结果
        summary = results['summary']
        status = "✅ 通过" if summary['passed'] else "❌ 未通过"
        print(f"总体结果: {status}")
        print(f"  错误: {summary['errors']}")
        print(f"  警告: {summary['warnings']}")
        print(f"  提示: {summary['info']}")
        print()
        
        # 各项检查结果
        print("详细检查结果:")
        print("-" * 80)
        
        for check_name, check_result in results['checks'].items():
            status = "✅" if check_result['passed'] else "❌"
            print(f"{status} {check_name}")
            if 'issues_found' in check_result and check_result['issues_found']:
                print(f"   问题: {', '.join(check_result['issues_found'])}")
        
        print()
        
        # 详细问题列表
        if self.errors:
            print("❌ 错误列表:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error['message']}")
                print(f"     建议: {error['suggestion']}")
            print()
        
        if self.warnings:
            print("⚠️  警告列表:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning['message']}")
                print(f"     建议: {warning['suggestion']}")
            print()
        
        if self.info:
            print("ℹ️  提示信息:")
            for i, info in enumerate(self.info, 1):
                print(f"  {i}. {info['message']}")
            print()
        
        # 内容质量指标
        if 'content_quality' in results['checks']:
            cq = results['checks']['content_quality']
            print("📊 内容质量指标:")
            print(f"  预计阅读时长: {cq['reading_time_minutes']} 分钟")
            print(f"  代码示例数量: {cq['code_blocks_count']}")
            print(f"  图表数量: {cq['diagrams_count']}")
            print()
        
        print("="*80)
        
        return results
    
    def save_report(self, output_file: str):
        """保存报告到JSON文件"""
        results = self.check_all()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 质量报告已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='检查文章质量')
    parser.add_argument('--article-file', required=True, help='文章Markdown文件路径')
    parser.add_argument('--report', help='输出报告文件路径（JSON格式）')
    
    args = parser.parse_args()
    
    # 检查文章文件是否存在
    if not Path(args.article_file).exists():
        print(f"❌ 错误: 文章文件不存在: {args.article_file}")
        return 1
    
    # 执行质量检查
    checker = ArticleQualityChecker(args.article_file)
    results = checker.print_report()
    
    # 保存报告
    if args.report:
        checker.save_report(args.report)
    
    # 根据检查结果返回退出码
    return 0 if results['summary']['passed'] else 1


if __name__ == "__main__":
    exit(main())
