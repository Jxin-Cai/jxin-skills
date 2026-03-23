#!/usr/bin/env python3
"""
Resume Craft - Markdown 简历转 PDF 转换器

将 Markdown 格式的简历转换为高端专家级风格的精美 PDF。
开场即呈现候选人画像，让面试官一眼掌握全貌与重点。

用法:
    python3 convert_resume_to_pdf.py /path/to/resume.md
    python3 convert_resume_to_pdf.py /path/to/resume.md --output /path/to/output.pdf
    python3 convert_resume_to_pdf.py /path/to/resume.md --theme classic
    python3 convert_resume_to_pdf.py /path/to/resume.md --verify
    python3 convert_resume_to_pdf.py /path/to/resume.md --encrypt mypassword

依赖:
    pip install markdown playwright pypdf
    playwright install chromium

可选依赖:
    pip install weasyprint        # Playwright 不可用时的降级方案
    pip install pdf2image         # PDF 验证预览（需要 poppler）
    pip install pypdfium2         # PDF 验证预览（备选，无需 poppler）
"""

import argparse
import base64
import os
import re
import sys
import asyncio
from pathlib import Path

try:
    import markdown
except ImportError:
    print("❌ 缺少依赖: markdown")
    print("   请运行: pip install markdown")
    sys.exit(1)

# ============================================================
# 配色方案
# ============================================================

THEMES = {
    "dark": {
        "name": "琥珀深邃",
        # 画像区 — 深炭底 + 橙色点睛
        "profile_bg_from": "#1C1C1E",
        "profile_bg_to": "#2C2C2E",
        "profile_name_color": "#FFFFFF",
        "profile_text": "rgba(255,255,255,0.88)",
        "profile_muted": "rgba(255,255,255,0.6)",
        # 橙色体系
        "accent": "#E8740C",
        "accent_warm": "#F5A623",
        "accent_glow": "rgba(232,116,12,0.12)",
        "accent_border": "rgba(232,116,12,0.35)",
        # 标签
        "tag_bg": "rgba(232,116,12,0.10)",
        "tag_text": "#E8740C",
        "tag_border": "rgba(232,116,12,0.30)",
        # 正文区
        "bg": "#FFFFFF",
        "text_body": "#2D2D2D",
        "text_heading": "#1C1C1E",
        "text_muted": "#6B6B6B",
        "section_bg": "#FFF9F3",
        "border": "#F0E6DA",
        "link": "#C8640A",
    },
    "classic": {
        "name": "经典暖橙",
        # 画像区 — 暖白底 + 左侧橙色粗边
        "profile_bg_from": "#FFFAF5",
        "profile_bg_to": "#FFF5EB",
        "profile_name_color": "#1C1C1E",
        "profile_text": "#3D3D3D",
        "profile_muted": "#6B6B6B",
        # 橙色体系
        "accent": "#D4661E",
        "accent_warm": "#E8891C",
        "accent_glow": "rgba(212,102,30,0.08)",
        "accent_border": "rgba(212,102,30,0.25)",
        # 标签
        "tag_bg": "rgba(212,102,30,0.08)",
        "tag_text": "#C25A1A",
        "tag_border": "rgba(212,102,30,0.22)",
        # 正文区
        "bg": "#FFFFFF",
        "text_body": "#2D2D2D",
        "text_heading": "#1C1C1E",
        "text_muted": "#6B6B6B",
        "section_bg": "#FEFBF7",
        "border": "#EDE4D9",
        "link": "#B85518",
    },
}

# ============================================================
# CSS 样式模板
# ============================================================


def get_css(theme: dict) -> str:
    """生成高端专家级简历 CSS"""
    return f"""
    /* ===== 全局基础 ===== */
    @page {{
        size: A4;
        margin: 12mm 16mm 14mm 16mm;
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
        font-family: "PingFang SC", "Noto Sans SC", "Microsoft YaHei",
                     -apple-system, "Helvetica Neue", sans-serif;
        font-size: 12.5px;
        line-height: 1.65;
        color: {theme["text_body"]};
        background: {theme["bg"]};
        -webkit-font-smoothing: antialiased;
    }}

    /* ============================================================
       候选人画像 — 开场第一屏，高端名片式设计
       ============================================================ */
    .profile-snapshot {{
        background: linear-gradient(160deg, {theme["profile_bg_from"]} 0%, {theme["profile_bg_to"]} 100%);
        color: {theme["profile_text"]};
        padding: 30px 32px 26px;
        border-radius: 6px;
        margin-bottom: 24px;
        page-break-inside: avoid;
        border-left: 5px solid {theme["accent"]};
        position: relative;
        overflow: hidden;
    }}

    /* 右上角装饰光晕 */
    .profile-snapshot::after {{
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 160px;
        height: 160px;
        background: radial-gradient(circle, {theme["accent_glow"]} 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }}

    .profile-snapshot h1 {{
        color: {theme["profile_name_color"]};
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 2px;
        position: relative;
    }}

    /* 姓名下方橙色装饰线 */
    .profile-snapshot h1::after {{
        content: "";
        display: block;
        width: 48px;
        height: 3px;
        background: linear-gradient(to right, {theme["accent"]}, {theme["accent_warm"]});
        border-radius: 2px;
        margin-top: 8px;
    }}

    .profile-snapshot .basic-info {{
        color: {theme["profile_text"]};
        font-size: 13px;
        margin-top: 10px;
        margin-bottom: 4px;
        line-height: 1.7;
    }}

    .profile-snapshot .basic-info a {{
        color: {theme["accent"]};
        text-decoration: none;
        border-bottom: 1px dotted {theme["accent_border"]};
    }}

    .profile-snapshot p {{
        margin-bottom: 4px;
        line-height: 1.65;
    }}

    .profile-snapshot strong {{
        color: {theme["profile_name_color"]};
        font-weight: 600;
    }}

    /* 技能标签 — 画像区内 */
    .profile-snapshot .skill-tag {{
        display: inline-block;
        background: {theme["tag_bg"]};
        color: {theme["tag_text"]};
        font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Consolas", monospace;
        font-size: 10.5px;
        font-weight: 500;
        padding: 3px 11px;
        border-radius: 14px;
        margin: 3px 5px 3px 0;
        border: 1px solid {theme["tag_border"]};
        letter-spacing: 0.3px;
    }}

    /* 一句话定位 — 画像区的灵魂 */
    .profile-snapshot .tagline {{
        color: {theme["accent"]};
        font-size: 14px;
        font-weight: 500;
        font-style: normal;
        border-left: 3px solid {theme["accent"]};
        padding: 8px 0 8px 14px;
        margin-top: 14px;
        line-height: 1.55;
        letter-spacing: 0.5px;
        background: {theme["accent_glow"]};
        border-radius: 0 4px 4px 0;
    }}

    /* ============================================================
       章节标题
       ============================================================ */
    h2 {{
        font-size: 16px;
        font-weight: 700;
        color: {theme["text_heading"]};
        padding-left: 14px;
        margin-top: 22px;
        margin-bottom: 10px;
        page-break-after: avoid;
        position: relative;
        letter-spacing: 0.5px;
    }}

    h2::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 2px;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, {theme["accent"]}, {theme["accent_warm"]});
        border-radius: 2px;
    }}

    h3 {{
        font-size: 14px;
        font-weight: 600;
        color: {theme["text_heading"]};
        margin-top: 14px;
        margin-bottom: 5px;
        page-break-after: avoid;
    }}

    /* ============================================================
       正文内容
       ============================================================ */
    p {{
        margin-bottom: 5px;
        line-height: 1.7;
    }}

    strong {{
        color: {theme["text_heading"]};
        font-weight: 600;
    }}

    /* 加粗数字高亮 — 让量化成就更醒目 */
    strong em, em strong {{
        color: {theme["accent"]};
        font-style: normal;
        font-weight: 700;
    }}

    /* ============================================================
       列表
       ============================================================ */
    ul, ol {{
        padding-left: 18px;
        margin-bottom: 6px;
    }}

    li {{
        margin-bottom: 4px;
        line-height: 1.65;
    }}

    li::marker {{
        color: {theme["accent"]};
        font-weight: bold;
    }}

    /* ============================================================
       行内代码（正文中的技能标签）
       ============================================================ */
    code {{
        display: inline-block;
        background: {theme["tag_bg"]};
        color: {theme["tag_text"]};
        font-family: "SF Mono", "JetBrains Mono", "Fira Code", monospace;
        font-size: 10.5px;
        font-weight: 500;
        padding: 2px 9px;
        border-radius: 10px;
        border: 1px solid {theme["tag_border"]};
        margin: 1px 2px;
    }}

    /* ============================================================
       代码块
       ============================================================ */
    pre {{
        background: #1E1E1E;
        color: #D4D4D4;
        padding: 14px 16px;
        border-radius: 6px;
        font-family: "SF Mono", "JetBrains Mono", "Fira Code", monospace;
        font-size: 11px;
        line-height: 1.5;
        overflow-x: auto;
        margin: 8px 0;
        page-break-inside: avoid;
        border-left: 3px solid {theme["accent"]};
    }}

    pre code {{
        background: transparent;
        color: inherit;
        border: none;
        padding: 0;
        margin: 0;
        border-radius: 0;
        font-size: inherit;
    }}

    /* ============================================================
       引用块
       ============================================================ */
    blockquote {{
        border-left: 3px solid {theme["accent"]};
        padding: 4px 0 4px 14px;
        margin: 6px 0;
        color: {theme["text_muted"]};
        font-size: 12px;
    }}

    blockquote p {{
        margin-bottom: 2px;
    }}

    /* ============================================================
       表格
       ============================================================ */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 12px;
    }}

    th {{
        background: {theme["section_bg"]};
        color: {theme["text_heading"]};
        font-weight: 600;
        padding: 8px 12px;
        text-align: left;
        border-bottom: 2px solid {theme["accent"]};
    }}

    td {{
        padding: 6px 12px;
        border-bottom: 1px solid {theme["border"]};
    }}

    tr:hover td {{
        background: {theme["accent_glow"]};
    }}

    /* ============================================================
       分隔线 — 优雅的渐变
       ============================================================ */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(
            to right,
            transparent,
            {theme["accent_border"]},
            {theme["accent"]},
            {theme["accent_border"]},
            transparent
        );
        margin: 18px 0;
    }}

    /* ============================================================
       链接
       ============================================================ */
    a {{
        color: {theme["link"]};
        text-decoration: none;
    }}

    /* ============================================================
       图片
       ============================================================ */
    img {{
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        margin: 8px 0;
    }}

    /* 画像区头像 — 右上角圆形头像 */
    .profile-snapshot img {{
        width: 96px;
        height: 96px;
        object-fit: cover;
        border-radius: 50%;
        border: 3px solid {theme["accent"]};
        float: right;
        margin: 0 0 10px 16px;
        shape-outside: circle();
    }}

    /* ============================================================
       打印适配
       ============================================================ */
    @media print {{
        body {{
            margin: 0;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        .profile-snapshot {{
            break-inside: avoid;
            -webkit-print-color-adjust: exact !important;
        }}
        h2, h3 {{ break-after: avoid; }}
        li {{ break-inside: avoid; }}
        a {{ color: inherit; }}
        a[href]::after {{ content: none; }}
    }}
    """


# ============================================================
# HTML 模板
# ============================================================


def get_html_template(title: str, css: str, body: str) -> str:
    """生成完整的 HTML 文档"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad: true, theme: 'dark'}});</script>
</head>
<body>
{body}
</body>
</html>"""


# ============================================================
# Markdown 处理
# ============================================================


def convert_local_images_to_base64(html: str, base_dir: str) -> str:
    """将本地图片引用转换为 base64 内联格式"""
    img_pattern = re.compile(r'<img\s+([^>]*?)src="([^"]+)"([^>]*?)>', re.IGNORECASE)

    def replace_img(match):
        prefix = match.group(1)
        src = match.group(2)
        suffix = match.group(3)

        # 跳过远程图片和已内联的图片
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)

        # 解析本地路径
        img_path = Path(base_dir) / src
        if not img_path.exists():
            print(f"  ⚠️ 图片未找到: {src}")
            return match.group(0)

        # 读取并编码
        ext = img_path.suffix.lower().lstrip(".")
        mime_map = {
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml",
            "bmp": "image/bmp",
        }
        mime = mime_map.get(ext, "application/octet-stream")

        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        print(f"  ✅ 内联图片: {src}")
        return f'<img {prefix}src="data:{mime};base64,{data}"{suffix}>'

    return img_pattern.sub(replace_img, html)


def enhance_resume_html(html: str) -> str:
    """增强简历 HTML 结构，添加语义化 CSS 类"""

    # 检测候选人画像区域（从 h1 到第一个 h2 或第一个 hr）
    h1_match = re.search(r"<h1>(.*?)</h1>", html)
    h2_match = re.search(r"<h2>", html)
    hr_match = re.search(r"<hr\s*/?>", html)

    # 画像区域结束位置：取 h2 和 hr 中较早出现的
    end_pos = None
    if h2_match:
        end_pos = h2_match.start()
    if hr_match and (end_pos is None or hr_match.start() < end_pos):
        end_pos = hr_match.start()

    if h1_match and end_pos:
        start = h1_match.start()
        profile_content = html[start:end_pos].strip()
        rest_content = html[end_pos:]
        before_content = html[:start]

        # 在 profile 区域内，将行内 code 转换为 skill-tag
        profile_enhanced = profile_content.replace("<code>", '<span class="skill-tag">')
        profile_enhanced = profile_enhanced.replace("</code>", "</span>")

        # 检测「一句话定位」（中文书名号引号包裹的内容）
        profile_enhanced = re.sub(
            r"<blockquote>\s*<p>\s*「(.*?)」\s*</p>\s*</blockquote>",
            r'<div class="tagline">「\1」</div>',
            profile_enhanced,
            flags=re.DOTALL,
        )

        # 检测引用块中的基本信息
        profile_enhanced = re.sub(
            r"<blockquote>\s*<p>(.*?)</p>\s*</blockquote>",
            lambda m: '<div class="basic-info">' + m.group(1) + "</div>",
            profile_enhanced,
            flags=re.DOTALL,
        )

        html = (
            before_content
            + '<div class="profile-snapshot">\n'
            + profile_enhanced
            + "\n</div>\n"
            + rest_content
        )

    return html


def md_to_html(md_content: str, base_dir: str) -> str:
    """将 Markdown 转换为增强的 HTML"""
    extensions = [
        "extra",       # 表格、代码块等
        "codehilite",  # 代码高亮
        "toc",         # 目录
        "nl2br",       # 换行转 <br>
        "sane_lists",  # 合理的列表处理
    ]
    extension_configs = {
        "codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        }
    }

    html = markdown.markdown(
        md_content,
        extensions=extensions,
        extension_configs=extension_configs,
    )

    # 转换本地图片为 base64
    html = convert_local_images_to_base64(html, base_dir)

    # 增强简历结构
    html = enhance_resume_html(html)

    return html


# ============================================================
# PDF 生成
# ============================================================


async def html_to_pdf_playwright(html_path: str, pdf_path: str):
    """使用 Playwright 将 HTML 转换为 PDF"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 加载 HTML 文件
        await page.goto(f"file://{html_path}", wait_until="networkidle")

        # 等待 Mermaid 图表渲染（如果有）
        await page.wait_for_timeout(2000)

        # 生成 PDF
        await page.pdf(
            path=pdf_path,
            format="A4",
            margin={
                "top": "12mm",
                "right": "16mm",
                "bottom": "14mm",
                "left": "16mm",
            },
            print_background=True,
        )

        await browser.close()


# ============================================================
# PDF 降级方案：weasyprint
# ============================================================


def html_to_pdf_weasyprint(html_path: str, pdf_path: str):
    """使用 weasyprint 作为 Playwright 不可用时的降级方案"""
    from weasyprint import HTML
    HTML(filename=html_path).write_pdf(pdf_path)


# ============================================================
# PDF 后处理
# ============================================================


def set_pdf_metadata(pdf_path: str, title: str):
    """为 PDF 添加专业元数据（标题、作者、主题等）"""
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({
        "/Title": title,
        "/Author": "Resume Craft",
        "/Subject": "Professional Resume",
        "/Creator": "Resume Craft - Expert Resume PDF Generator",
    })
    with open(pdf_path, "wb") as f:
        writer.write(f)


def encrypt_pdf(pdf_path: str, password: str):
    """为 PDF 添加密码保护"""
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with open(pdf_path, "wb") as f:
        writer.write(f)


def verify_pdf(pdf_path: str) -> str:
    """将 PDF 首页转为图片用于视觉验证，返回预览图路径"""
    preview_path = str(Path(pdf_path).with_suffix(".preview.png"))

    # 方案一：pdf2image（需要 poppler）
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
        images[0].save(preview_path)
        return preview_path
    except ImportError:
        pass

    # 方案二：pypdfium2（纯 Python，无需 poppler）
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        bitmap = page.render(scale=2.0)
        img = bitmap.to_pil()
        img.save(preview_path)
        return preview_path
    except ImportError:
        pass

    raise ImportError(
        "PDF 验证需要 pdf2image 或 pypdfium2，请安装其中之一：\n"
        "  pip install pdf2image    # 需要系统安装 poppler\n"
        "  pip install pypdfium2    # 纯 Python，推荐"
    )


# ============================================================
# 主流程
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        description="Resume Craft - 将 Markdown 简历转换为高端专家级 PDF",
        epilog="示例: python3 convert_resume_to_pdf.py resume.md --theme dark",
    )
    parser.add_argument("input", help="输入的 Markdown 简历文件路径")
    parser.add_argument("--output", "-o", help="输出的 PDF 文件路径（默认与输入同目录）")
    parser.add_argument(
        "--theme", "-t",
        choices=["dark", "classic"],
        default="dark",
        help="主题: dark(琥珀深邃/深色) 或 classic(经典暖橙/浅色) (默认: dark)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="仅生成 HTML，不生成 PDF（用于调试样式）",
    )
    parser.add_argument(
        "--encrypt",
        metavar="PASSWORD",
        help="为生成的 PDF 设置密码保护",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="生成后将 PDF 首页转为图片验证渲染效果",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="不写入 PDF 元数据（默认自动写入标题、作者等）",
    )

    args = parser.parse_args()

    # 验证输入文件
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)

    if not input_path.suffix.lower() in (".md", ".markdown"):
        print(f"⚠️ 输入文件可能不是 Markdown 格式: {input_path.suffix}")

    # 确定输出路径
    if args.output:
        pdf_path = Path(args.output).resolve()
    else:
        pdf_path = input_path.with_suffix(".pdf")

    html_path = pdf_path.with_suffix(".html")

    # 选择主题
    theme = THEMES[args.theme]

    print(f"🎨 Resume Craft - 专家级简历 PDF 生成器")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📄 输入: {input_path}")
    print(f"🎭 主题: {theme['name']}")
    print(f"📁 输出: {pdf_path}")
    print()

    # Step 1: 读取 Markdown
    print("📖 Step 1: 读取 Markdown 文件...")
    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    print(f"  ✅ 读取完成 ({len(md_content)} 字符)")

    # Step 2: 转换为 HTML
    print("🔄 Step 2: 转换为 HTML（候选人画像优先布局）...")
    base_dir = str(input_path.parent)
    html_body = md_to_html(md_content, base_dir)

    # 提取标题
    title_match = re.search(r"<h1>(.*?)</h1>", html_body)
    title = title_match.group(1) if title_match else "Resume"

    # 生成完整 HTML
    css = get_css(theme)
    full_html = get_html_template(title, css, html_body)

    # 保存 HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"  ✅ HTML 生成完成: {html_path}")

    if args.html_only:
        print()
        print(f"✨ 仅生成 HTML 完成！")
        print(f"   📄 {html_path}")
        print(f"   💡 可在浏览器中打开预览效果")
        return

    # Step 3: 生成 PDF（三级降级：Playwright → weasyprint → 手动打印提示）
    print("📑 Step 3: 渲染 PDF...")
    pdf_generated = False

    # 尝试方案一：Playwright
    try:
        asyncio.run(html_to_pdf_playwright(str(html_path), str(pdf_path)))
        print(f"  ✅ PDF 生成完成 (Playwright): {pdf_path}")
        pdf_generated = True
    except ImportError:
        print("  ⚠️ Playwright 不可用，尝试降级方案...")
    except Exception as e:
        print(f"  ⚠️ Playwright 渲染失败: {e}")
        print("  尝试降级方案...")

    # 尝试方案二：weasyprint
    if not pdf_generated:
        try:
            html_to_pdf_weasyprint(str(html_path), str(pdf_path))
            print(f"  ✅ PDF 生成完成 (weasyprint): {pdf_path}")
            pdf_generated = True
        except ImportError:
            print("  ⚠️ weasyprint 也不可用")
        except Exception as e:
            print(f"  ⚠️ weasyprint 渲染失败: {e}")

    # 所有方案都不可用
    if not pdf_generated:
        print()
        print("❌ PDF 生成失败：无可用渲染引擎")
        print()
        print("💡 请安装以下任一方案：")
        print("   方案一（推荐）: pip install playwright && playwright install chromium")
        print("   方案二（降级）: pip install weasyprint")
        print()
        print("   或直接在浏览器中打开 HTML 文件，使用 Ctrl+P 打印为 PDF：")
        print(f"   📄 {html_path}")
        sys.exit(1)

    # Step 4: PDF 后处理
    # 4a) 写入元数据
    if not args.no_metadata:
        print("📝 Step 4a: 写入 PDF 元数据...")
        try:
            set_pdf_metadata(str(pdf_path), title)
            print(f"  ✅ 元数据已写入（标题: {title}）")
        except ImportError:
            print("  ⚠️ 跳过元数据写入（缺少 pypdf，请运行: pip install pypdf）")
        except Exception as e:
            print(f"  ⚠️ 元数据写入失败: {e}")

    # 4b) 加密保护
    if args.encrypt:
        print("🔒 Step 4b: 加密 PDF...")
        try:
            encrypt_pdf(str(pdf_path), args.encrypt)
            print("  ✅ PDF 已加密")
        except ImportError:
            print("  ❌ 加密失败（缺少 pypdf，请运行: pip install pypdf）")
            sys.exit(1)
        except Exception as e:
            print(f"  ❌ 加密失败: {e}")
            sys.exit(1)

    # 4c) 验证预览
    if args.verify:
        print("🔍 Step 4c: 生成 PDF 预览图...")
        try:
            preview_path = verify_pdf(str(pdf_path))
            print(f"  ✅ 预览图已生成: {preview_path}")
        except ImportError as e:
            print(f"  ⚠️ {e}")
        except Exception as e:
            print(f"  ⚠️ 预览生成失败: {e}")

    print()
    print(f"✨ 转换完成！")
    print(f"   📄 PDF: {pdf_path}")
    print(f"   📄 HTML: {html_path}")
    if args.encrypt:
        print(f"   🔒 PDF 已加密保护")
    if args.verify and 'preview_path' in locals():
        print(f"   🖼️  预览: {preview_path}")
    print(f"   💡 如需调整样式，可编辑 HTML 后在浏览器中打印为 PDF")


if __name__ == "__main__":
    main()
