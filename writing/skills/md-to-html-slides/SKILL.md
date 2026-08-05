---
name: md-to-html-slides
description: 将 Markdown 文档转化为 HTML 长滚动演示页面。自动重组叙事结构，生成带滚动动画的自包含 HTML 文件，图片转 base64 方便直接复制分享。当用户说"把这个 md 做成演示"、"生成 HTML slides"、"把文档转成网页 PPT"、"做个滚动式演示页面"、"markdown to slides"时使用此技能。即使用户只是给了一个 md 文件并要求做成可展示的页面，也应触发。
---

# Markdown → HTML 滚动演示

将 Markdown 文档转化为一份精美的长滚动 HTML 演示页面——不是简单的格式转换，而是把线性文档重组为有节奏感的视觉叙事。

输出是一个**自包含单文件 HTML**，内置样式和 GSAP 滚动动画，所有图片转为 base64 data URI，可以直接在浏览器打开或复制给别人。

## 执行流程

### Step 1: 读取输入

获取 Markdown 文件路径（必需）。如果用户没有指定文件，用 AskUserQuestion 询问。

读取文件内容，确认可以正常解析。

### Step 2: 分析文档结构

扫描 Markdown 内容，识别：
- 标题层级（H1 / H2 / H3）
- 段落文本
- 列表（有序 / 无序）
- 表格
- 代码块（含语言标记）
- 图片引用（`![alt](src)`）
- 引用块（`>`）

### Step 3: 叙事重组

这是核心步骤。不是逐段翻译 Markdown 为 HTML，而是**重新编排叙事结构**使其适合演示场景。

**重组规则**：

1. **提取核心主题**：从 H1 和首段提炼演示标题 + 一句话主旨
2. **归纳核心论点**：全文通读后提炼 2-4 条最重要的判断，作为 summary
3. **章节拆分**：
   - 每个 H2 → 一个独立 section
   - H2 下有 3+ 个 H3 → `cards-grid`（并列概念适合卡片展示）
   - H2 下是线性论述 → `key-points`（提炼为 ≤3 条要点）
4. **内容精简**：
   - 长段落（>100 字）→ 提炼为要点，每条 ≤ 30 字
   - 去掉过渡句、铺垫、重复论述
   - 保留关键数据、案例、结论
5. **特殊内容映射**：
   - Markdown 表格 → `comparison`
   - 有序列表（步骤性质）→ `flow`
   - 代码块 → `code`
   - 图片 → `diagram`
   - 引用块 → `quote`
6. **结尾处理**：最后一个 H2 如果是总结/展望性质 → `cta`

**叙事节奏**：
- hero → summary → 正文 sections（交替白色/浅灰背景）→ cta
- 避免连续 3 个以上相同 type 的 section
- 内容密集区之间插入 `quote` 或 `diagram` 制造呼吸感

### Step 4: 选择呈现模式

为每个 section 选择最合适的 type。参考 `references/section-patterns.md` 获取完整的 type 列表和 JSON schema。

优先级：
1. 内容形态决定 type（表格→comparison，代码→code，图片→diagram）
2. 信息关系决定 type（并列→cards-grid，递进→flow，论点→key-points）
3. 同类 type 避免连续出现

### Step 5: 输出 sections.json

在用户工作目录生成 `sections.json` 文件，结构如下：

```json
{
  "title": "演示标题",
  "sections": [
    {"type": "hero", "title": "...", "subtitle": "..."},
    {"type": "summary", "items": ["...", "..."]},
    {"type": "cards-grid", "label": "...", "title": "...", "columns": 3, "items": [...]},
    ...
  ]
}
```

每个 section 的具体 schema 见 `references/section-patterns.md`。

### Step 6: 生成 HTML

运行构建脚本：

```bash
python <skill_path>/scripts/build_html.py \
  --content sections.json \
  --output presentation.html \
  --images-dir <markdown文件同级目录或用户指定>
```

脚本会：
- 读取 sections.json
- 按 type 渲染为 HTML 片段
- 注入模板（含完整 CSS + GSAP 动画）
- 将本地图片转为 base64 data URI
- 输出自包含 HTML 文件

### Step 7: 返回结果

```
✅ HTML 演示页面已生成！

📄 文件：presentation.html
📊 区块数：N 个 section
📦 文件大小：xxx KB（自包含，可直接分享）

在浏览器中打开即可查看，支持滚动动画效果。
```

## 输出规范

- 输出目录：Markdown 文件同级目录，或用户指定路径
- 文件名：默认 `presentation.html`，用户可自定义
- 中间文件：`sections.json`（保留，方便后续微调）
- 所有图片嵌入为 base64，HTML 完全自包含

## 注意事项

1. **重组而非逐段转译** — 演示不是文章的 HTML 版本，而是重新组织的视觉叙事
2. **精简为王** — 每条要点 ≤ 30 字，标题 ≤ 20 字，去除一切冗余
3. **视觉节奏** — 交替白色/浅灰背景，避免同 type 连续出现
4. **图片自包含** — 所有图片必须转 base64，确保 HTML 单文件可携带
5. **不修改源文件** — 只读取 Markdown，不做任何修改
