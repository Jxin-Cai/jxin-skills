#!/usr/bin/env python3
"""
文章摘要生成脚本

功能：
1. 分析文章主要内容
2. 提取核心要点
3. 生成100字以内的吸引人摘要
4. 输出到独立文件

使用方法：
python generate_summary.py --article-file article.md --output summary.txt
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class SummaryGenerator:
    """文章摘要生成器"""
    
    def __init__(self, article_file: str):
        self.article_file = Path(article_file)
        self.article_content = self._read_article()
        self.title = self._extract_title()
        self.article_type = self._detect_article_type()
        self.key_sections = self._extract_key_sections()
        self.core_message = self._extract_core_message()
    
    def _read_article(self) -> str:
        """读取文章内容"""
        with open(self.article_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_title(self) -> str:
        """提取文章标题"""
        match = re.search(r'^#\s+(.+)$', self.article_content, re.MULTILINE)
        return match.group(1).strip() if match else "未知主题"
    
    def _detect_article_type(self) -> str:
        """检测文章类型"""
        content = self.article_content.lower()
        
        if any(word in content for word in ['概念', '介绍', '什么是', '基础']):
            return "科普型"
        elif any(word in content for word in ['问题', '解决', '优化', '改进']):
            return "问题解决型"
        elif any(word in content for word in ['经验', '实践', '项目', '复盘']):
            return "经验总结型"
        elif any(word in content for word in ['趋势', '未来', '发展', '预测']):
            return "趋势分析型"
        else:
            return "综合型"
    
    def _extract_key_sections(self) -> List[str]:
        """提取关键章节"""
        sections = []
        
        # 提取所有二级标题
        h2_matches = re.findall(r'^##\s+(.+)$', self.article_content, re.MULTILINE)
        
        # 排除一些常见的非核心章节
        exclude_keywords = ['摘要', '引用', '参考', '延伸阅读', '总结']
        
        for section in h2_matches:
            if not any(keyword in section for keyword in exclude_keywords):
                sections.append(section)
        
        return sections[:4]  # 最多4个关键章节
    
    def _extract_core_message(self) -> str:
        """提取核心信息"""
        # 查找"如果今天你只记得一句话"部分
        pattern = r'如果今天你只记得一句话[：:]\s*\n+>\s*(.+)'
        match = re.search(pattern, self.article_content)
        
        if match:
            return match.group(1).strip()
        
        # 如果没有找到，尝试提取总结部分的第一段
        summary_pattern = r'##\s+总结.*?\n\n(.+?)(?:\n\n|\Z)'
        match = re.search(summary_pattern, self.article_content, re.DOTALL)
        
        if match:
            summary_text = match.group(1).strip()
            # 取第一句话
            first_sentence = re.split(r'[。！？]', summary_text)[0]
            return first_sentence
        
        return ""
    
    def generate_summary(self) -> str:
        """生成文章摘要"""
        
        # 根据文章类型生成不同风格的摘要
        summary_templates = {
            "科普型": self._generate_educational_summary,
            "问题解决型": self._generate_solution_summary,
            "经验总结型": self._generate_experience_summary,
            "趋势分析型": self._generate_trend_summary,
            "综合型": self._generate_general_summary
        }
        
        generator = summary_templates.get(
            self.article_type, 
            self._generate_general_summary
        )
        
        summary = generator()
        
        # 确保在100字以内
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        return summary
    
    def _generate_educational_summary(self) -> str:
        """生成科普型文章摘要"""
        parts = [
            f"本文深入解析{self.title}的核心理念和实践方法"
        ]
        
        if self.key_sections:
            sections_str = "、".join(self.key_sections[:2])
            parts.append(f"通过{sections_str}等角度")
        
        parts.append("帮助读者理解")
        
        if self.core_message:
            parts.append(f"：{self.core_message}")
        else:
            parts.append("关键概念和实际应用")
        
        return "，".join(parts) + "。"
    
    def _generate_solution_summary(self) -> str:
        """生成问题解决型文章摘要"""
        parts = [
            f"针对{self.title}的常见问题"
        ]
        
        parts.append("本文分析传统方法的不足")
        
        if self.key_sections:
            parts.append(f"从{self.key_sections[0]}入手")
        
        parts.append("提供可落地的解决方案")
        
        if self.core_message:
            parts.append(f"：{self.core_message}")
        
        return "，".join(parts) + "。"
    
    def _generate_experience_summary(self) -> str:
        """生成经验总结型文章摘要"""
        parts = [
            f"本文基于真实项目经验，分享{self.title}的实践心得"
        ]
        
        if self.key_sections:
            sections_str = "、".join(self.key_sections[:2])
            parts.append(f"涵盖{sections_str}等关键环节")
        
        parts.append("提供可复用的经验和避坑指南")
        
        return "，".join(parts) + "。"
    
    def _generate_trend_summary(self) -> str:
        """生成趋势分析型文章摘要"""
        parts = [
            f"本文分析{self.title}的发展现状和未来趋势"
        ]
        
        if self.key_sections:
            parts.append(f"从{self.key_sections[0]}等维度")
        
        parts.append("解读技术演进方向和行业影响")
        
        if self.core_message:
            parts.append(f"：{self.core_message}")
        
        return "，".join(parts) + "。"
    
    def _generate_general_summary(self) -> str:
        """生成通用型文章摘要"""
        parts = [
            f"本文探讨{self.title}"
        ]
        
        if self.key_sections:
            sections_str = "、".join(self.key_sections[:3])
            parts.append(f"涵盖{sections_str}等内容")
        
        if self.core_message:
            parts.append(f"核心观点：{self.core_message}")
        else:
            parts.append("为读者提供全面的技术解析")
        
        return "，".join(parts) + "。"
    
    def save_to_file(self, output_file: str):
        """保存摘要到文件"""
        summary = self.generate_summary()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # 生成JSON格式的元数据
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "article_file": str(self.article_file),
            "article_title": self.title,
            "article_type": self.article_type,
            "key_sections": self.key_sections,
            "core_message": self.core_message,
            "summary": summary
        }
        
        metadata_file = output_path.with_suffix('.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 文章摘要已生成: {output_path}")
        print(f"✅ 元数据已保存: {metadata_file}")
        print(f"\n📝 摘要内容:\n{summary}")
        print(f"\n📊 字数统计: {len(summary)} 字")


def main():
    parser = argparse.ArgumentParser(description='生成文章摘要')
    parser.add_argument('--article-file', required=True, help='文章Markdown文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 检查文章文件是否存在
    if not Path(args.article_file).exists():
        print(f"❌ 错误: 文章文件不存在: {args.article_file}")
        return 1
    
    # 生成摘要
    generator = SummaryGenerator(args.article_file)
    generator.save_to_file(args.output)
    
    return 0


if __name__ == "__main__":
    exit(main())
