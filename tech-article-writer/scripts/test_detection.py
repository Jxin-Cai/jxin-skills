#!/usr/bin/env python3
"""
快速测试智能检测功能

使用方法：
    python test_detection.py
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入检测函数
from convert_diagrams import check_smart_image_generator

def main():
    print("=" * 70)
    print("智能检测功能测试")
    print("=" * 70)
    print()
    
    # 执行检测
    has_skill, skill_path = check_smart_image_generator()
    
    print()
    print("=" * 70)
    print("检测结果：")
    print("=" * 70)
    
    if has_skill:
        print(f"✅ 技能可用")
        print(f"📍 路径: {skill_path}")
        print()
        print("可以使用以下功能：")
        print("  - 自动生成专业图表")
        print("  - 批量转换Markdown图表")
    else:
        print(f"❌ 技能不可用")
        print()
        print("将使用回退方案：")
        print("  - Mermaid代码块")
        print("  - PlantUML代码块")
    
    print("=" * 70)
    
    return 0 if has_skill else 1

if __name__ == '__main__':
    sys.exit(main())
