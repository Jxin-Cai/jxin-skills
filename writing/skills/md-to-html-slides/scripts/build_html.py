#!/usr/bin/env python3
"""
build_html.py — 将结构化 JSON 内容注入 HTML 模板，生成自包含演示页面。

功能：
  1. 读取 template.html 模板
  2. 读取 sections.json（由 Claude 生成的结构化内容）
  3. 按 section type 渲染 HTML 片段
  4. 将本地图片转为 base64 data URI
  5. 输出自包含单文件 HTML

用法：
  python build_html.py --content sections.json --output presentation.html [--images-dir ./images]
"""

import argparse
import base64
import html
import json
import mimetypes
import sys
import urllib.request
from pathlib import Path


ACCENT_COLORS = ["blue", "green", "purple", "red", "orange"]


def img_to_base64(src, images_dir=None):
    """将图片路径或 URL 转为 base64 data URI。"""
    path = None
    if src.startswith("data:"):
        return src

    if src.startswith("http://") or src.startswith("https://"):
        try:
            resp = urllib.request.urlopen(src, timeout=10)
            data = resp.read()
            content_type = resp.headers.get("Content-Type", "image/png")
            b64 = base64.b64encode(data).decode()
            return f"data:{content_type};base64,{b64}"
        except Exception:
            return src

    if images_dir:
        path = Path(images_dir) / src
    if not path or not path.exists():
        path = Path(src)
    if not path.exists():
        return src

    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def escape(text):
    """HTML 转义。"""
    return html.escape(str(text)) if text else ""


def render_hero(section):
    title = escape(section.get("title", ""))
    subtitle = escape(section.get("subtitle", ""))
    meta = escape(section.get("meta", ""))
    parts = [
        '<div class="hero">',
        f'  <h1 class="hero-title animate-in">{title}</h1>',
    ]
    if subtitle:
        parts.append(f'  <p class="hero-subtitle animate-in">{subtitle}</p>')
    if meta:
        parts.append(f'  <p class="hero-meta animate-in">{meta}</p>')
    parts.append('</div>')
    return "\n".join(parts)


def render_summary(section):
    title = escape(section.get("title", ""))
    items = section.get("items", [])
    parts = [
        '<div class="section">',
        '  <div class="container">',
    ]
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    parts.append('    <div class="summary-card animate-in">')
    parts.append('      <ul class="summary-items">')
    for item in items:
        parts.append(f'        <li>{escape(item)}</li>')
    parts.append('      </ul>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_cards_grid(section, alt=False):
    label = escape(section.get("label", ""))
    title = escape(section.get("title", ""))
    subtitle = escape(section.get("subtitle", ""))
    items = section.get("items", [])
    columns = section.get("columns", 3)
    grid_class = f"grid-{min(columns, 4)}"

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
    ]
    if label:
        parts.append(f'    <p class="section-label animate-in">{label}</p>')
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    if subtitle:
        parts.append(f'    <p class="section-subtitle animate-in">{subtitle}</p>')
    parts.append(f'    <div class="{grid_class} stagger-group">')
    for i, item in enumerate(items):
        accent = item.get("accent", ACCENT_COLORS[i % len(ACCENT_COLORS)])
        card_title = escape(item.get("title", ""))
        card_desc = escape(item.get("description", ""))
        card_label = escape(item.get("label", ""))
        parts.append(f'      <div class="card card-accent-{accent} animate-in">')
        if card_label:
            parts.append(f'        <p class="card-label">{card_label}</p>')
        if card_title:
            parts.append(f'        <p class="card-title">{card_title}</p>')
        if card_desc:
            parts.append(f'        <p class="card-desc">{card_desc}</p>')
        parts.append('      </div>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_key_points(section, alt=False):
    label = escape(section.get("label", ""))
    title = escape(section.get("title", ""))
    items = section.get("items", [])

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
    ]
    if label:
        parts.append(f'    <p class="section-label animate-in">{label}</p>')
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    parts.append('    <div class="key-points stagger-group">')
    for i, item in enumerate(items):
        accent = item.get("accent", ACCENT_COLORS[i % len(ACCENT_COLORS)])
        point_title = escape(item.get("title", ""))
        point_desc = escape(item.get("description", ""))
        parts.append('      <div class="key-point animate-in">')
        parts.append(f'        <div class="key-point-marker" style="background: var(--accent-{accent})"></div>')
        parts.append('        <div class="key-point-content">')
        if point_title:
            parts.append(f'          <p class="key-point-title">{point_title}</p>')
        if point_desc:
            parts.append(f'          <p class="key-point-desc">{point_desc}</p>')
        parts.append('        </div>')
        parts.append('      </div>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_comparison(section, alt=False):
    label = escape(section.get("label", ""))
    title = escape(section.get("title", ""))
    headers = section.get("headers", [])
    rows = section.get("rows", [])

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
    ]
    if label:
        parts.append(f'    <p class="section-label animate-in">{label}</p>')
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    parts.append('    <div class="card animate-in" style="padding: 0; overflow: hidden;">')
    parts.append('      <table class="comparison-table">')
    if headers:
        parts.append('        <thead><tr>')
        for h in headers:
            parts.append(f'          <th>{escape(h)}</th>')
        parts.append('        </tr></thead>')
    parts.append('        <tbody>')
    for row in rows:
        parts.append('          <tr>')
        for cell in row:
            parts.append(f'            <td>{escape(cell)}</td>')
        parts.append('          </tr>')
    parts.append('        </tbody>')
    parts.append('      </table>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_flow(section, alt=False):
    label = escape(section.get("label", ""))
    title = escape(section.get("title", ""))
    steps = section.get("steps", [])

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
    ]
    if label:
        parts.append(f'    <p class="section-label animate-in">{label}</p>')
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    parts.append('    <div class="flow-steps stagger-group">')
    for i, step in enumerate(steps, 1):
        step_title = escape(step.get("title", ""))
        step_desc = escape(step.get("description", ""))
        parts.append('      <div class="flow-step animate-in">')
        parts.append(f'        <div class="flow-step-number">{i}</div>')
        parts.append('        <div class="flow-step-content">')
        if step_title:
            parts.append(f'          <p class="flow-step-title">{step_title}</p>')
        if step_desc:
            parts.append(f'          <p class="flow-step-desc">{step_desc}</p>')
        parts.append('        </div>')
        parts.append('      </div>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_code(section, alt=False):
    label = escape(section.get("label", ""))
    title = escape(section.get("title", ""))
    language = escape(section.get("language", ""))
    code = escape(section.get("code", ""))

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
    ]
    if label:
        parts.append(f'    <p class="section-label animate-in">{label}</p>')
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    parts.append('    <div class="code-block animate-in">')
    if language:
        parts.append(f'      <p class="code-block-label">{language}</p>')
    parts.append(f'      <pre>{code}</pre>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_diagram(section, images_dir=None, alt=False):
    label = escape(section.get("label", ""))
    title = escape(section.get("title", ""))
    src = section.get("src", "")
    caption = escape(section.get("caption", ""))

    if src:
        src = img_to_base64(src, images_dir)

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
    ]
    if label:
        parts.append(f'    <p class="section-label animate-in">{label}</p>')
    if title:
        parts.append(f'    <h2 class="section-heading animate-in">{title}</h2>')
    parts.append('    <div class="diagram animate-in">')
    if src:
        parts.append(f'      <img src="{src}" alt="{escape(caption or title)}">')
    if caption:
        parts.append(f'      <p class="diagram-caption">{caption}</p>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_quote(section, alt=False):
    text = escape(section.get("text", ""))
    source = escape(section.get("source", ""))

    bg_class = "section-alt" if alt else ""
    parts = [
        f'<div class="section {bg_class}">',
        '  <div class="container">',
        '    <div class="quote-block animate-in">',
        f'      <p class="quote-text">{text}</p>',
    ]
    if source:
        parts.append(f'      <p class="quote-source">— {source}</p>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_cta(section):
    title = escape(section.get("title", ""))
    description = escape(section.get("description", ""))
    parts = [
        '<div class="section">',
        '  <div class="container">',
        '    <div class="cta animate-in">',
        f'      <h2 class="cta-heading">{title}</h2>',
    ]
    if description:
        parts.append(f'      <p class="cta-desc">{description}</p>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


RENDERERS = {
    "hero": render_hero,
    "summary": render_summary,
    "cards-grid": render_cards_grid,
    "key-points": render_key_points,
    "comparison": render_comparison,
    "flow": render_flow,
    "code": render_code,
    "diagram": render_diagram,
    "quote": render_quote,
    "cta": render_cta,
}


def render_sections(sections, images_dir=None):
    """渲染所有 sections 为 HTML。"""
    html_parts = []
    for i, section in enumerate(sections):
        section_type = section.get("type", "key-points")
        renderer = RENDERERS.get(section_type)
        if not renderer:
            print(f"  ⚠️  Unknown section type: {section_type}, skipping")
            continue

        alt = (i % 2 == 1) and section_type not in ("hero", "cta")

        if section_type == "hero":
            html_parts.append(renderer(section))
        elif section_type == "diagram":
            html_parts.append(renderer(section, images_dir=images_dir, alt=alt))
        elif section_type in ("cta", "summary"):
            html_parts.append(renderer(section))
        else:
            html_parts.append(renderer(section, alt=alt))

    return "\n\n".join(html_parts)


def build(content_path, template_path, output_path, images_dir=None):
    """主构建流程。"""
    with open(content_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "Presentation")
    sections = data.get("sections", [])

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    sections_html = render_sections(sections, images_dir=images_dir)

    result = template.replace("{{TITLE}}", escape(title))
    result = result.replace("{{SECTIONS_HTML}}", sections_html)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"✅ HTML 演示页面已生成：{output_path}")
    print(f"   ├─ 标题：{title}")
    print(f"   ├─ 区块数：{len(sections)}")
    size_kb = Path(output_path).stat().st_size / 1024
    print(f"   └─ 文件大小：{size_kb:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="将结构化 JSON 内容注入 HTML 模板，生成自包含演示页面"
    )
    parser.add_argument("--content", required=True, help="sections.json 文件路径")
    parser.add_argument("--output", required=True, help="输出 HTML 文件路径")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).parent.parent / "assets" / "template.html"),
        help="HTML 模板路径（默认使用 assets/template.html）",
    )
    parser.add_argument("--images-dir", default=None, help="图片目录路径（用于 base64 转换）")
    args = parser.parse_args()

    content_path = Path(args.content)
    template_path = Path(args.template)
    output_path = Path(args.output)

    if not content_path.exists():
        print(f"❌ 内容文件不存在：{content_path}")
        sys.exit(1)
    if not template_path.exists():
        print(f"❌ 模板文件不存在：{template_path}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    build(str(content_path), str(template_path), str(output_path), args.images_dir)


if __name__ == "__main__":
    main()
