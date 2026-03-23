#!/usr/bin/env python3
"""
会话记录脚本

功能：
1. 记录文章生成会话信息
2. 捕获用户反馈和修正
3. 存储到短期记忆
4. 支持升级分析

使用方法：
python record_session.py --article-file article.md --metadata metadata.json
"""

import argparse
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class SessionRecorder:
    """会话记录器"""
    
    def __init__(self, article_file: str, metadata: Optional[Dict] = None):
        self.article_file = Path(article_file)
        self.article_content = self._read_article()
        self.metadata = metadata or {}
        self.session_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        
    def _read_article(self) -> str:
        """读取文章内容"""
        if self.article_file.exists():
            with open(self.article_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
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
    
    def _extract_title(self) -> str:
        """提取文章标题"""
        import re
        match = re.search(r'^#\s+(.+)$', self.article_content, re.MULTILINE)
        return match.group(1).strip() if match else "未知标题"
    
    def _calculate_quality_metrics(self) -> Dict:
        """计算质量指标"""
        import re
        
        # 基本统计
        char_count = len(re.findall(r'[\u4e00-\u9fff]', self.article_content))
        code_blocks = len(re.findall(r'```', self.article_content)) // 2
        diagrams = len(re.findall(r'```mermaid|```plantuml', self.article_content))
        
        # 阅读时长（中文400字/分钟）
        reading_time = char_count / 400
        
        # 结构完整性
        has_intro = bool(re.search(r'场景|引入|背景', self.article_content))
        has_concept = bool(re.search(r'概念|定义|什么是', self.article_content))
        has_depth = bool(re.search(r'深入|原理|机制', self.article_content))
        has_example = bool(re.search(r'应用|实例|例子', self.article_content))
        has_summary = bool(re.search(r'总结|回顾', self.article_content))
        
        structure_score = sum([has_intro, has_concept, has_depth, has_example, has_summary]) / 5
        
        # 必备元素
        has_author = bool(re.search(r'\*\*文\s*\|\s*三七\*\*', self.article_content))
        has_motto = bool(re.search(r'不积跬步无以至千里', self.article_content))
        has_knowledge_graph = bool(re.search(r'```mermaid', self.article_content))
        has_key_message = bool(re.search(r'如果今天你只记得一句话', self.article_content))
        
        completeness_score = sum([has_author, has_motto, has_knowledge_graph, has_key_message]) / 4
        
        # 可读性评分（基于代码示例和图表）
        readability_score = min(1.0, (code_blocks * 0.2 + diagrams * 0.3))
        
        # 参与友好度（基于阅读时长）
        if 8 <= reading_time <= 12:
            engagement_score = 1.0
        elif reading_time < 8:
            engagement_score = reading_time / 8
        else:
            engagement_score = max(0.5, 12 / reading_time)
        
        return {
            "accuracy_score": self.metadata.get("accuracy_score", 0.9),
            "completeness": round(completeness_score, 2),
            "structure_completeness": round(structure_score, 2),
            "readability": round(readability_score, 2),
            "engagement": round(engagement_score, 2),
            "reading_time_minutes": round(reading_time, 1),
            "code_blocks_count": code_blocks,
            "diagrams_count": diagrams,
            "char_count": char_count
        }
    
    def create_session_record(self) -> Dict:
        """创建会话记录"""
        
        title = self._extract_title()
        article_type = self._detect_article_type()
        quality_metrics = self._calculate_quality_metrics()
        
        session_record = {
            "session_id": f"{self.session_id}-{datetime.now().strftime('%Y%m%d%H%M')}-tech-article",
            "timestamp": self.timestamp,
            "article_file": str(self.article_file),
            "article_title": title,
            "article_type": article_type,
            
            "generation_details": {
                "structure_decisions": self.metadata.get("structure_decisions", "默认黄金五段式"),
                "content_choices": self.metadata.get("content_choices", "基于主题分析"),
                "example_selection": self.metadata.get("example_selection", "由浅入深"),
                "diagram_rationale": self.metadata.get("diagram_rationale", "辅助理解核心概念"),
                "writing_style": self.metadata.get("writing_style", "认知台阶+画面感")
            },
            
            "quality_metrics": quality_metrics,
            
            "user_feedback": {
                "explicit_feedback": self.metadata.get("explicit_feedback", ""),
                "corrections": self.metadata.get("corrections", []),
                "satisfaction_score": self.metadata.get("satisfaction_score", 8),
                "modification_count": self.metadata.get("modification_count", 0)
            },
            
            "generation_effectiveness": {
                "time_to_completion": self.metadata.get("time_to_completion", 0),
                "iteration_count": self.metadata.get("iteration_count", 1),
                "success_flag": self.metadata.get("success_flag", True)
            },
            
            "learning_indicators": {
                "novel_patterns": self.metadata.get("novel_patterns", []),
                "successful_strategies": self.metadata.get("successful_strategies", []),
                "failed_approaches": self.metadata.get("failed_approaches", []),
                "improvement_opportunities": self.metadata.get("improvement_opportunities", [])
            }
        }
        
        return session_record
    
    def save_session(self, output_dir: str = ".tech-article-writer/sessions"):
        """保存会话记录"""
        
        # 创建会话记录
        session_record = self.create_session_record()
        
        # 确保目录存在
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = f"{datetime.now().strftime('%Y-%m-%d-%H-%M')}-article-session.json"
        file_path = output_path / filename
        
        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_record, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 会话记录已保存: {file_path}")
        print(f"📊 会话ID: {session_record['session_id']}")
        print(f"📝 文章标题: {session_record['article_title']}")
        print(f"📁 文章类型: {session_record['article_type']}")
        print(f"⭐ 用户满意度: {session_record['user_feedback']['satisfaction_score']}/10")
        
        return file_path


def main():
    parser = argparse.ArgumentParser(description='记录文章生成会话')
    parser.add_argument('--article-file', required=True, help='文章Markdown文件路径')
    parser.add_argument('--metadata', help='元数据JSON文件路径')
    parser.add_argument('--output-dir', default='.tech-article-writer/sessions',
                       help='会话记录输出目录（根目录）')
    
    args = parser.parse_args()
    
    # 检查文章文件
    if not Path(args.article_file).exists():
        print(f"❌ 错误: 文章文件不存在: {args.article_file}")
        return 1
    
    # 读取元数据
    metadata = {}
    if args.metadata and Path(args.metadata).exists():
        with open(args.metadata, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    
    # 创建会话记录
    recorder = SessionRecorder(args.article_file, metadata)
    recorder.save_session(args.output_dir)
    
    return 0


if __name__ == "__main__":
    exit(main())
