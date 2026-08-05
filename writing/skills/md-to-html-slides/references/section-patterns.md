# Section 类型规范

本文档定义了 `md-to-html-slides` 技能所支持的所有 section 类型。Claude 在 Step 5 输出的 JSON 必须严格遵循这些 schema。

## JSON 整体结构

```json
{
  "title": "演示标题",
  "sections": [
    { "type": "hero", ... },
    { "type": "summary", ... },
    ...
  ]
}
```

---

## hero — 封面 / 大标题

**适用场景**：演示首页，展示主题和元信息。每份演示有且仅有一个 hero。

```json
{
  "type": "hero",
  "title": "主标题（≤20字）",
  "subtitle": "一句话阐述主题价值（≤50字）",
  "meta": "作者 / 日期 / 场合（可选）"
}
```

---

## summary — 核心摘要

**适用场景**：紧跟 hero 之后，用 2-4 条要点概括全文核心论点。

```json
{
  "type": "summary",
  "title": "核心观点（可选标题）",
  "items": [
    "论点一：一句话",
    "论点二：一句话",
    "论点三：一句话"
  ]
}
```

**精简规则**：每条 item ≤ 30 字，不写完整句子，去掉修饰词，只保留判断。

---

## cards-grid — 卡片网格

**适用场景**：并列概念、功能列表、对比要素（3-6 项等量信息）。

```json
{
  "type": "cards-grid",
  "label": "SECTION LABEL（英文大写，≤3词）",
  "title": "区块标题",
  "subtitle": "补充说明（可选）",
  "columns": 3,
  "items": [
    {
      "title": "卡片标题",
      "description": "1-2句简要描述",
      "label": "卡片上方小标签（可选）",
      "accent": "blue"
    }
  ]
}
```

- `columns`: 2 / 3 / 4，根据 items 数量选择
- `accent`: blue / green / purple / red / orange，不指定时自动轮转

---

## key-points — 要点列表

**适用场景**：线性展开的核心观点、优势、特性描述。每项有明确的标题 + 解释。

```json
{
  "type": "key-points",
  "label": "SECTION LABEL（可选）",
  "title": "区块标题",
  "items": [
    {
      "title": "要点标题（≤15字）",
      "description": "解释说明（≤50字）",
      "accent": "blue"
    }
  ]
}
```

**精简规则**：title 是结论本身，description 补充"为什么"或"怎么做"。

---

## comparison — 表格对比

**适用场景**：Markdown 表格内容、多维度对比、规格参数。

```json
{
  "type": "comparison",
  "label": "SECTION LABEL（可选）",
  "title": "对比标题",
  "headers": ["维度", "方案A", "方案B"],
  "rows": [
    ["性能", "高", "中"],
    ["成本", "低", "高"]
  ]
}
```

---

## flow — 步骤流程

**适用场景**：有序步骤、实施路径、操作流程。

```json
{
  "type": "flow",
  "label": "SECTION LABEL（可选）",
  "title": "流程标题",
  "steps": [
    {
      "title": "步骤标题",
      "description": "简要说明（≤40字）"
    }
  ]
}
```

---

## code — 代码展示

**适用场景**：Markdown 中的代码块、配置文件、命令示例。

```json
{
  "type": "code",
  "label": "SECTION LABEL（可选）",
  "title": "代码标题（可选）",
  "language": "python",
  "code": "def hello():\n    print('world')"
}
```

---

## diagram — 图示 / 图片

**适用场景**：Markdown 中引用的图片、架构图、示意图。

```json
{
  "type": "diagram",
  "label": "SECTION LABEL（可选）",
  "title": "图示标题（可选）",
  "src": "path/to/image.png 或 https://...",
  "caption": "图片说明（可选）"
}
```

`src` 支持本地路径和远程 URL，build_html.py 会自动转为 base64。

---

## quote — 引用 / 金句

**适用场景**：重要引语、核心洞察、点睛之笔。

```json
{
  "type": "quote",
  "text": "引用文本",
  "source": "来源（可选）"
}
```

---

## cta — 结语 / 行动号召

**适用场景**：演示结尾，总结核心信息或呼吁行动。每份演示最多一个 cta。

```json
{
  "type": "cta",
  "title": "核心结论或行动号召（≤20字）",
  "description": "补充说明（可选，≤50字）"
}
```

---

## 选择指导

| Markdown 原始内容 | 推荐 section type |
|------------------|------------------|
| H1 标题 | `hero` |
| 开头段落的核心论点 | `summary` |
| H2 下 3+ 个 H3 子节 | `cards-grid` |
| H2 下的要点列表 | `key-points` |
| Markdown 表格 | `comparison` |
| 有序列表（步骤性质） | `flow` |
| 代码块 | `code` |
| 图片引用 | `diagram` |
| 引用块（>） | `quote` |
| 最后一个总结性 H2 | `cta` |
| 长段落（>100字） | 提炼为 `key-points`（≤3 条） |
