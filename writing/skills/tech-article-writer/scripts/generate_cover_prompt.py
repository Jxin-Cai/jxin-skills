#!/usr/bin/env python3
"""
封面图片提示词生成脚本

功能：
1. 分析文章主题和内容
2. 提取关键技术元素
3. 生成AI绘图提示词（100字以内）
4. 输出到独立文件

使用方法：
python generate_cover_prompt.py --article-file article.md --output cover_prompt.txt
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime


class CoverPromptGenerator:
    """封面图片提示词生成器"""
    
    def __init__(self, article_file: str):
        self.article_file = Path(article_file)
        self.article_content = self._read_article()
        self.title = self._extract_title()
        self.article_type = self._detect_article_type()
        self.key_concepts = self._extract_key_concepts()
    
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
        
        # 通过关键词判断文章类型
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
    
    def _extract_key_concepts(self) -> list:
        """提取关键技术概念"""
        # 提取所有二级和三级标题作为关键概念
        concepts = []
        
        # 提取二级标题
        h2_matches = re.findall(r'^##\s+(.+)$', self.article_content, re.MULTILINE)
        concepts.extend(h2_matches[:3])  # 只取前3个
        
        # 提取代码块中的技术关键词
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', self.article_content, re.DOTALL)
        for code in code_blocks[:2]:  # 只看前2个代码块
            # 提取类名、函数名等
            class_matches = re.findall(r'\b(?:class|interface)\s+(\w+)', code)
            concepts.extend(class_matches[:2])
        
        return concepts[:5]  # 最多5个关键概念
    
    def generate_prompt(self) -> str:
        """生成封面图片提示词"""
        
        # 根据文章类型选择视觉风格
        style_mapping = {
            "科普型": {
                "style": "简洁明快的插画风格",
                "colors": "蓝色、绿色、白色",
                "elements": "图标、流程图、概念可视化",
                "mood": "清晰易懂、教育性强"
            },
            "问题解决型": {
                "style": "对比鲜明的图形设计",
                "colors": "红色、橙色、蓝色",
                "elements": "对比图、箭头、解决方案可视化",
                "mood": "问题聚焦、解决方案明确"
            },
            "经验总结型": {
                "style": "温暖专业的插画风格",
                "colors": "暖色调、金色、深蓝",
                "elements": "时间轴、里程碑、经验图谱",
                "mood": "专业可信、经验沉淀"
            },
            "趋势分析型": {
                "style": "未来感科技风格",
                "colors": "紫色、蓝色、银色",
                "elements": "数据图表、趋势线、未来场景",
                "mood": "前瞻性、科技感"
            },
            "综合型": {
                "style": "现代简约的科技风格",
                "colors": "蓝色、灰色、白色",
                "elements": "技术图标、连接线、数据元素",
                "mood": "专业、现代、科技"
            }
        }
        
        style = style_mapping.get(self.article_type, style_mapping["综合型"])
        
        # 构建提示词
        prompt_parts = []
        
        # 1. 主题描述
        theme_desc = f"一幅关于'{self.title}'的技术插画"
        prompt_parts.append(theme_desc)
        
        # 2. 核心元素
        if self.key_concepts:
            concepts_str = "、".join(self.key_concepts[:3])
            element_desc = f"展示{concepts_str}等核心概念"
            prompt_parts.append(element_desc)
        
        # 3. 视觉风格
        prompt_parts.append(style["style"])
        
        # 4. 构图和元素
        composition = self._generate_composition(style["elements"])
        prompt_parts.append(composition)
        
        # 5. 色彩方案
        prompt_parts.append(f"色调以{style['colors']}为主")
        
        # 6. 氛围
        prompt_parts.append(f"整体呈现{style['mood']}的视觉效果")
        
        # 组合成完整提示词
        full_prompt = "，".join(prompt_parts) + "。"
        
        # 确保在100字以内
        if len(full_prompt) > 100:
            full_prompt = full_prompt[:97] + "..."
        
        return full_prompt
    
    def _generate_composition(self, elements: str) -> str:
        """生成构图描述"""
        compositions = [
            f"画面中心突出显示{elements}",
            f"采用层次化布局展示{elements}",
            f"用现代化图形呈现{elements}",
            f"以立体方式表现{elements}"
        ]
        
        # 根据文章类型选择
        import random
        return random.choice(compositions)
    
    def save_to_file(self, output_file: str):
        """保存提示词到文件"""
        prompt = self.generate_prompt()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        # 同时生成JSON格式的元数据
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "article_file": str(self.article_file),
            "article_title": self.title,
            "article_type": self.article_type,
            "key_concepts": self.key_concepts,
            "prompt": prompt
        }
        
        metadata_file = output_path.with_suffix('.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 封面图片提示词已生成: {output_path}")
        print(f"✅ 元数据已保存: {metadata_file}")
        print(f"\n📝 提示词内容:\n{prompt}")
        print(f"\n📊 字数统计: {len(prompt)} 字")


def main():
    parser = argparse.ArgumentParser(description='生成文章封面图片提示词')
    parser.add_argument('--article-file', required=True, help='文章Markdown文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 检查文章文件是否存在
    if not Path(args.article_file).exists():
        print(f"❌ 错误: 文章文件不存在: {args.article_file}")
        return 1
    
    # 生成封面提示词
    generator = CoverPromptGenerator(args.article_file)
    generator.save_to_file(args.output)
    
    return 0


if __name__ == "__main__":
    exit(main())
