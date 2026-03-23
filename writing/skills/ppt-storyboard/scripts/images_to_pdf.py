#!/usr/bin/env python3
"""
将分镜图片合成为 PDF 文件。

用法:
    python images_to_pdf.py --images-dir <图片目录> --output <输出PDF路径> [--title <标题>]

功能:
    - 按文件名排序读取目录下所有 PNG/JPG 图片
    - 每张图片铺满一页（横向 16:9 比例）
    - 输出单个 PDF 文件
"""

import argparse
import os
import sys
import subprocess


def ensure_dependencies():
    """确保必要的 Python 依赖已安装"""
    try:
        import reportlab  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        print("正在安装依赖: reportlab, Pillow ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "reportlab", "Pillow"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


ensure_dependencies()

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image


# 16:9 比例页面尺寸 (宽 x 高)
PAGE_WIDTH = 16 * inch
PAGE_HEIGHT = 9 * inch
PAGE_SIZE = (PAGE_WIDTH, PAGE_HEIGHT)


def get_sorted_images(images_dir: str) -> list[str]:
    """获取目录下所有图片文件，按文件名排序"""
    supported_ext = {".png", ".jpg", ".jpeg", ".webp"}
    images = []

    for f in os.listdir(images_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext in supported_ext:
            images.append(os.path.join(images_dir, f))

    images.sort(key=lambda p: os.path.basename(p))
    return images


def images_to_pdf(images_dir: str, output_path: str, title: str = "Presentation"):
    """将图片目录合成为 PDF"""

    image_paths = get_sorted_images(images_dir)

    if not image_paths:
        print(f"错误: 目录 {images_dir} 下没有找到图片文件")
        sys.exit(1)

    print(f"找到 {len(image_paths)} 张图片，开始生成 PDF...")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=PAGE_SIZE)
    c.setTitle(title)
    c.setAuthor("ppt-storyboard")

    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            img_width, img_height = img.size

            # 计算缩放比例，让图片铺满页面（保持宽高比）
            scale_w = PAGE_WIDTH / img_width
            scale_h = PAGE_HEIGHT / img_height
            scale = min(scale_w, scale_h)

            draw_width = img_width * scale
            draw_height = img_height * scale

            # 居中放置
            x = (PAGE_WIDTH - draw_width) / 2
            y = (PAGE_HEIGHT - draw_height) / 2

            c.drawImage(img_path, x, y, draw_width, draw_height, preserveAspectRatio=True)

            if i < len(image_paths) - 1:
                c.showPage()

            print(f"  ✅ 第 {i + 1}/{len(image_paths)} 页已添加: {os.path.basename(img_path)}")

        except Exception as e:
            print(f"  ❌ 第 {i + 1} 页处理失败 ({os.path.basename(img_path)}): {e}")
            if i < len(image_paths) - 1:
                c.showPage()

    c.save()
    print(f"\n✅ PDF 生成完成: {output_path}")
    print(f"   共 {len(image_paths)} 页")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将分镜图片合成为 PDF 文件")
    parser.add_argument("--images-dir", required=True, help="图片目录路径")
    parser.add_argument("--output", required=True, help="输出 PDF 文件路径")
    parser.add_argument("--title", default="Presentation", help="PDF 标题")

    args = parser.parse_args()

    if not os.path.isdir(args.images_dir):
        print(f"错误: 图片目录不存在: {args.images_dir}")
        sys.exit(1)

    images_to_pdf(args.images_dir, args.output, args.title)
