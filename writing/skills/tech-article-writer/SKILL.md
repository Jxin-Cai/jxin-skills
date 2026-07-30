---
name: tech-article-writer
description: 专业技术文章创作与增量修改工作流。用于写技术博客、教程、架构解析、工具评测、实践复盘或修改已有 Markdown 技术文章；包含多视角联网调研、可追溯引用、黄金五段式/动态大纲、风格指纹、中文去 AI 味两遍审计、版本快照与局部重写。仅在用户显式调用 /jxin-writing:article 时使用，不根据普通写作请求自动触发。
---

# Tech Article Writer

面向中文技术文章的完整创作技能。文章要专业、可验证、好读，并保留作者自己的判断。不要把文章写成百科词条、产品宣传稿或模板化 AI 长文。

## 参考文件加载

按任务需要读取，不要一次性把所有参考文件加载进上下文：

- 新文章基础结构：[article-structure.md](references/article-structure.md)
- 写作语言与案例原则：[writing-guidelines.md](references/writing-guidelines.md)
- Markdown 规范：[markdown-rules.md](references/markdown-rules.md)
- 自动调研与引用：[research-phase.md](references/research-phase.md)
- 中文 AI 模式审计：[anti-ai-patterns.md](references/anti-ai-patterns.md)
- 复杂主题动态规划：[dynamic-outline.md](references/dynamic-outline.md)
- 风格 profile：[style-profiles/README.md](references/style-profiles/README.md)
- 图片与架构图：[diagram-integration.md](references/diagram-integration.md)
- 会话与用户偏好：[memory-system.md](references/memory-system.md)

默认风格是 [default-sanqi.yaml](references/style-profiles/default-sanqi.yaml)。用户要求正式、克制的技术文档风格时加载 [formal-tech.yaml](references/style-profiles/formal-tech.yaml)。

## 创作新文章

### 1. 明确任务

先从用户输入中提取：

- 主题、目标读者、发布渠道
- 写作目标与核心结论
- 期望字数、截止时间、是否需要代码/图片
- 用户提供的材料、代码、链接和事实边界

只有真正影响方案的缺口才提问。用户已给出明确要求时直接执行。

### 2. 选择风格

- 未指定时使用 `default-sanqi.yaml`。
- 用户指定 profile 时读取对应 YAML。
- 用户提供 3 篇以上历史文章并要求模仿时，先运行：

```bash
python scripts/extract_style.py \
  --articles-dir <历史文章目录> \
  --output <custom-profile.yaml>
```

提取结果是风格草稿。检查并删除偶然高频词、隐私和不应固化的表达后再使用。

### 3. 确认写作策略

用简短清单给出：

- 文章定位与读者
- 建议结构模式
- 预计字数与代码/图片数量
- 当前风格 profile
- 是否联网调研

用户要求直接完成时，自行检查后继续，不要把流程变成连续审批。

### 4. 自动调研

除非用户明确跳过，按照 [research-phase.md](references/research-phase.md) 执行：

1. 从实践者、架构师、初学者三个视角生成搜索问题。
2. 使用 `WebSearch` 搜索，使用 `WebFetch` 阅读关键原文。
3. 优先官方文档、标准、论文和一线工程团队复盘。
4. 建立 3-5 张高价值素材卡，保存为 `<article>.materials.json`。
5. 关键数字和强结论至少交叉验证一次。

无法联网时说明限制，不编造引用、URL、数字或“业内共识”。

### 5. 选择大纲模式

- 普通教程、单一工具介绍、短篇文章：黄金五段式。
- 多子系统、方案权衡、5000 字以上或强依赖主题：按照 [dynamic-outline.md](references/dynamic-outline.md) 使用动态大纲。

动态大纲仍以五个根节点保持叙事节奏，但允许 2-3 层子节点。每个节点标注：摘要、预计字数、内容类型、素材卡和依赖。

先生成骨架：每个叶节点只写 1-2 句摘要。确认逻辑完整后再展开正文。

### 6. 创建初始版本

首次落盘后立即创建快照：

```bash
python scripts/version_manager.py \
  --action snapshot \
  --article-file <article.md> \
  --note "初始骨架"
```

### 7. 分节写作

按大纲依赖顺序展开，不机械按标题顺序填充。每节都要有信息增量：

- 概念必须说明边界和适用条件。
- 技术判断必须说明依据和权衡。
- 代码示例必须最小可运行，关键行带中文解释。
- 案例必须有场景、动作和结果，不能只写“效果显著”。
- 图片服务于理解；需要时遵循 [diagram-integration.md](references/diagram-integration.md)。

写完一节后检查它是否兑现骨架摘要，并与依赖节点一致。

### 8. 处理引用

正文中的外部事实、数字和第三方结论使用 `[1]`、`[2]` 连续标记。文末生成 `## 参考引用`。

完成后运行：

```bash
python scripts/format_citations.py \
  --article-file <article.md> \
  --citations <article.materials.json> \
  --output <article-cited.md>
```

没有外部引用时不要创建空的引用列表。

### 9. 两遍去 AI 味

按照 [anti-ai-patterns.md](references/anti-ai-patterns.md) 执行：

1. 第一遍按高权重到低权重审计并重写，用事实、场景、数据和明确判断替换套话。
2. 第二遍从头复读，检查重写是否破坏技术含义、引用、逻辑和作者语气。

运行检测器：

```bash
python scripts/humanize_check.py \
  --article-file <article.md> \
  --threshold 40 \
  --verbose
```

不要为降低评分机械删词。准确术语、必要总结和引用原文可保留。

### 10. 发布门禁

运行统一检查：

```bash
python scripts/check_article_quality.py \
  --article-file <article.md> \
  --style-profile references/style-profiles/default-sanqi.yaml \
  --report <quality-report.json>
```

只有以下条件满足时才声明文章完成：

- 一级标题唯一，Markdown 与代码块闭合。
- 结构完整，段落和示例不是占位符。
- AI 痕迹评分不高于 40。
- 引用编号连续且文末条目齐全。
- 风格 profile 的禁用表达、句长和段落节奏检查通过。
- 关键技术结论与引用已人工复核。

检查失败时修复具体问题后重跑，不要用“整体润色”掩盖失败项。

### 11. 生成配套内容

需要时运行：

```bash
python scripts/generate_cover_prompt.py --article-file <article.md> --output <cover-prompt.txt>
python scripts/generate_summary.py --article-file <article.md> --output <summary.md>
python scripts/record_session.py \
  --article-file <article.md> \
  --quality-score <score> \
  --style-profile <profile-name> \
  --version-count <count>
```

## 修改现有文章

不要默认全文重写。使用以下增量流程：

### 1. 修改前快照

```bash
python scripts/version_manager.py \
  --action snapshot \
  --article-file <article.md> \
  --note "修改前：<用户要求摘要>"
```

### 2. 影响分析

```bash
python scripts/version_manager.py \
  --action smart-edit \
  --article-file <article.md> \
  --edit-description "<用户要求>"
```

把章节分为：

- `regenerate`：直接受影响，允许重写。
- `consistency_check`：逻辑上下游，只检查并做必要微调。
- `skip`：无关章节，保持原文。

脚本按标题关键词做初筛；Claude 还要根据动态大纲依赖和正文逻辑修正分组。

### 3. 局部编辑

只修改前两组。保留未受影响段落的措辞、引用编号和作者风格。若修改改变核心结论，再扩大影响范围并说明原因。

### 4. 差异与复查

修改后再创建快照，然后输出差异：

```bash
python scripts/version_manager.py --action snapshot --article-file <article.md> --note "完成修改"
python scripts/version_manager.py --action diff --article-file <article.md> --version <修改前版本>
```

向用户报告：重写了哪些章节、一致性调整了哪些章节、跳过了哪些章节，以及质量门禁结果。

### 5. 回滚

用户明确要求回滚时执行：

```bash
python scripts/version_manager.py \
  --action rollback \
  --article-file <article.md> \
  --version <N>
```

回滚前脚本会自动保存当前内容。每篇文章默认保留最近 10 个版本。

## 交付格式

新文章至少交付：

- Markdown 正文
- 使用的风格 profile 名称
- 调研素材卡（执行联网调研时）
- 质量检查结果
- 本次版本号

修改文章额外交付 diff 摘要。不要声称已验证没有实际运行过的脚本或检查。

## 核心原则

1. **事实先于文采**：不确定的事实先调研，无法验证就标注限制。
2. **结构服务论点**：黄金五段式是默认，不是不可改变的模板。
3. **风格可描述、不可表演**：profile 控制节奏，不制造虚假经历。
4. **局部修改保持稳定**：小修改不应让整篇文章面目全非。
5. **评分是门禁，不是目标**：检测器帮助发现模式，最终判断仍看准确性和可读性。
