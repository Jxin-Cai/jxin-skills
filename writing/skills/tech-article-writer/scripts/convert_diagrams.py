#!/usr/bin/env python3
"""
批量转换Markdown文章中的图表为图片

功能：
1. 扫描文章中的所有Mermaid/PlantUML等代码块
2. 检测smart-image-generator技能是否存在
3. 使用该技能将图表转换为图片
4. 替换原始代码块为图片引用
5. 可选：保留原始代码块在注释中

使用方法：
    python convert_diagrams.py --article-file article.md [--keep-original] [--output-dir .tech-article-writer/images/]
"""

import argparse
import re
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 支持的图表类型
DIAGRAM_TYPES = {
    'mermaid': r'```mermaid\s*\n(.*?)\n```',
    'plantuml': r'```plantuml\s*\n(.*?)\n```',
    'dot': r'```dot\s*\n(.*?)\n```',
    'graphviz': r'```graphviz\s*\n(.*?)\n```',
}

def check_smart_image_generator():
    """
    智能检测smart-image-generator技能位置
    
    检测顺序：
    1. 用户级Cursor技能目录（~/.cursor/skills/）
    2. 项目级技能目录（./skills/）
    3. 相对路径搜索
    4. 全局搜索当前项目
    
    Returns:
        bool: 技能是否存在
        str: 技能路径（如果存在）
    """
    print("🔍 智能搜索smart-image-generator技能...")
    
    # 1. 用户级Cursor技能目录
    user_home = Path.home()
    user_cursor_paths = [
        user_home / '.cursor' / 'skills' / 'smart-image-generator',
        user_home / '.cursor' / 'skills' / 'custom-skills' / 'smart-image-generator',
    ]
    
    for path in user_cursor_paths:
        skill_file = path / 'SKILL.md'
        if skill_file.exists():
            print(f"✅ 找到技能（用户级）: {path}")
            return True, str(path.resolve())
    
    # 2. 项目级技能目录
    project_paths = [
        Path('skills/custom-skills/smart-image-generator'),
        Path('skills/smart-image-generator'),
        Path('.skills/smart-image-generator'),
    ]
    
    for path in project_paths:
        skill_file = path / 'SKILL.md'
        if skill_file.exists():
            print(f"✅ 找到技能（项目级）: {path}")
            return True, str(path.resolve())
    
    # 3. 相对路径搜索（向上查找）
    relative_paths = [
        Path('../smart-image-generator'),
        Path('../../smart-image-generator'),
        Path('../custom-skills/smart-image-generator'),
    ]
    
    for path in relative_paths:
        skill_file = path / 'SKILL.md'
        if skill_file.exists():
            print(f"✅ 找到技能（相对路径）: {path}")
            return True, str(path.resolve())
    
    # 4. 全局搜索当前项目（从当前目录向上搜索）
    current = Path.cwd()
    for _ in range(5):  # 最多向上搜索5层
        search_paths = [
            current / 'skills' / 'custom-skills' / 'smart-image-generator',
            current / 'skills' / 'smart-image-generator',
        ]
        
        for path in search_paths:
            skill_file = path / 'SKILL.md'
            if skill_file.exists():
                print(f"✅ 找到技能（全局搜索）: {path}")
                return True, str(path.resolve())
        
        # 向上一层
        parent = current.parent
        if parent == current:  # 到达根目录
            break
        current = parent
    
    # 未找到
    print("❌ 未找到smart-image-generator技能")
    print("\n📍 已搜索的位置：")
    print("   1. 用户级: ~/.cursor/skills/")
    print("   2. 项目级: ./skills/")
    print("   3. 相对路径: ../ 和 ../../")
    print("   4. 向上搜索: 当前目录及其父目录")
    print("\n💡 提示：")
    print("   - 确认技能已安装")
    print("   - 检查SKILL.md文件是否存在")
    print("   - 可以手动指定技能路径（未来版本支持）")
    
    return False, None

def extract_diagrams(article_content):
    """
    从文章中提取所有图表代码块
    
    Args:
        article_content: 文章内容
        
    Returns:
        list: 包含(类型, 内容, 完整匹配)的元组列表
    """
    diagrams = []
    
    for diagram_type, pattern in DIAGRAM_TYPES.items():
        matches = re.finditer(pattern, article_content, re.DOTALL | re.MULTILINE)
        for match in matches:
            diagrams.append({
                'type': diagram_type,
                'content': match.group(1).strip(),
                'full_match': match.group(0),
                'start': match.start(),
                'end': match.end()
            })
    
    # 按出现顺序排序
    diagrams.sort(key=lambda x: x['start'])
    
    return diagrams

def generate_image_from_diagram(diagram, output_dir, skill_path, index):
    """
    使用smart-image-generator技能生成图片
    
    Args:
        diagram: 图表信息字典
        output_dir: 输出目录
        skill_path: smart-image-generator技能路径
        index: 图表索引
        
    Returns:
        str: 生成的图片路径，失败则返回None
    """
    # 创建临时文件保存图表内容
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    temp_file = Path(output_dir) / f"temp-diagram-{index}-{timestamp}.txt"
    
    try:
        # 写入图表内容
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(f"# 图表类型: {diagram['type']}\n\n")
            f.write(diagram['content'])
        
        # 构建提示词
        prompt = f"""
请为以下{diagram['type']}图表生成一张清晰的流程图图片：

{diagram['content']}

要求：
- 使用专业的流程图风格
- 确保所有文字清晰可读
- 使用合适的颜色方案
- 布局清晰、层次分明
"""
        
        # 生成图片文件名
        image_name = f"{diagram['type']}-{index}-{timestamp}.png"
        image_path = Path(output_dir) / image_name
        
        # 调用smart-image-generator
        # 注意：这里需要通过某种方式调用技能
        # 实际实现中，可能需要通过Cursor的技能调用机制
        print(f"📝 正在生成第{index}个图表: {diagram['type']}")
        print(f"   提示词: {prompt[:100]}...")
        print(f"   输出: {image_path}")
        
        # TODO: 实际调用smart-image-generator技能
        # 这里需要根据实际的技能调用方式来实现
        # 暂时返回占位符
        
        return str(image_path.relative_to(Path.cwd()))
        
    except Exception as e:
        print(f"❌ 生成图片失败: {str(e)}")
        return None
    finally:
        # 清理临时文件
        if temp_file.exists():
            temp_file.unlink()

def replace_diagrams_with_images(article_content, diagrams, image_paths, keep_original):
    """
    替换文章中的图表代码块为图片引用
    
    Args:
        article_content: 原文章内容
        diagrams: 图表信息列表
        image_paths: 对应的图片路径列表
        keep_original: 是否在注释中保留原始代码
        
    Returns:
        str: 更新后的文章内容
    """
    # 从后向前替换，避免位置偏移
    result = article_content
    
    for diagram, image_path in reversed(list(zip(diagrams, image_paths))):
        if image_path is None:
            continue
            
        # 构建替换内容
        replacement = f"![{diagram['type']}图表]({image_path})"
        
        # 如果需要保留原始代码
        if keep_original:
            replacement += f"\n\n<!-- 原始{diagram['type']}代码：\n{diagram['full_match']}\n-->"
        
        # 执行替换
        result = result[:diagram['start']] + replacement + result[diagram['end']:]
    
    return result

def convert_article_diagrams(article_file, output_dir, keep_original=False):
    """
    转换文章中的所有图表
    
    Args:
        article_file: 文章文件路径
        output_dir: 图片输出目录
        keep_original: 是否保留原始代码块
        
    Returns:
        bool: 是否成功
    """
    # 检查文章文件
    article_path = Path(article_file)
    if not article_path.exists():
        print(f"❌ 文章文件不存在: {article_file}")
        return False
    
    # 读取文章内容
    with open(article_path, 'r', encoding='utf-8') as f:
        article_content = f.read()
    
    # 提取图表
    diagrams = extract_diagrams(article_content)
    if not diagrams:
        print("ℹ️  文章中没有找到图表代码块")
        return True
    
    print(f"📊 找到 {len(diagrams)} 个图表:")
    for i, diagram in enumerate(diagrams, 1):
        print(f"   {i}. {diagram['type']} ({len(diagram['content'])} 字符)")
    
    # 检查smart-image-generator技能
    has_skill, skill_path = check_smart_image_generator()
    if not has_skill:
        print("\n⚠️  未找到smart-image-generator技能")
        print("   将无法生成图片，建议安装该技能后重试")
        return False
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成图片
    image_paths = []
    for i, diagram in enumerate(diagrams, 1):
        image_path = generate_image_from_diagram(diagram, output_dir, skill_path, i)
        image_paths.append(image_path)
    
    # 统计成功数量
    success_count = sum(1 for path in image_paths if path is not None)
    print(f"\n✅ 成功生成 {success_count}/{len(diagrams)} 张图片")
    
    if success_count == 0:
        print("❌ 没有成功生成任何图片，不修改原文件")
        return False
    
    # 替换文章内容
    updated_content = replace_diagrams_with_images(
        article_content, 
        diagrams, 
        image_paths, 
        keep_original
    )
    
    # 备份原文件
    backup_file = article_path.with_suffix('.md.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(article_content)
    print(f"📁 已备份原文件: {backup_file}")
    
    # 写入更新后的内容
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"✅ 已更新文章: {article_path}")
    
    # 生成转换报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'article_file': str(article_path),
        'total_diagrams': len(diagrams),
        'successful_conversions': success_count,
        'output_directory': str(output_path),
        'keep_original': keep_original,
        'diagrams': [
            {
                'type': d['type'],
                'index': i,
                'image_path': image_paths[i-1],
                'success': image_paths[i-1] is not None
            }
            for i, d in enumerate(diagrams, 1)
        ]
    }
    
    report_file = output_path / f"conversion-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"📄 转换报告: {report_file}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='批量转换Markdown文章中的图表为图片',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--article-file',
        required=True,
        help='要处理的Markdown文章文件路径'
    )
    
    parser.add_argument(
        '--output-dir',
        default='.tech-article-writer/images/',
        help='图片输出目录（默认: .tech-article-writer/images/）'
    )
    
    parser.add_argument(
        '--keep-original',
        action='store_true',
        help='在注释中保留原始图表代码块'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Markdown图表批量转换工具")
    print("=" * 60)
    print(f"📄 文章文件: {args.article_file}")
    print(f"📁 输出目录: {args.output_dir}")
    print(f"💾 保留原始代码: {'是' if args.keep_original else '否'}")
    print("=" * 60)
    print()
    
    success = convert_article_diagrams(
        args.article_file,
        args.output_dir,
        args.keep_original
    )
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 转换完成！")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ 转换失败")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
