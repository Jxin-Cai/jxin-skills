# PPT 图片提示词工程参考

本文档指导如何为每个分镜编写高质量的图片生成提示词。

## 核心原则

### 描述场景，不描述布局

```
❌ 差的提示词（描述布局）：
"A PPT slide with white background. Title 'Digital Transformation' on the top left
in bold 48pt font. Three bullet points on the left side. A blue technology image
on the right side, taking 60% width."

✅ 好的提示词（描述场景）：
"A sweeping aerial view of a sprawling traditional city gradually transforming — the
left half shows old brick buildings, narrow streets, analog infrastructure; the right
half shows the same city reimagined with sleek glass structures, glowing data streams
flowing between buildings like rivers of light. The transition zone in the middle is
the most visually dynamic: construction cranes, half-transformed buildings, old walls
being peeled away to reveal luminous digital cores underneath.

Text overlay:
- Headline (top-left, white bold on dark overlay): '数字化转型的真实面貌'
- Subheadline: 'Not a switch to flip, but a city to rebuild'

The mood is one of ambitious transformation in progress — not utopian, but gritty
and real."
```

### 每个提示词都是一个完整的创作简报

把AI图片生成器想象成一个从未看过你其他页面的摄影师/画家。每个提示词都必须自包含地传达：

1. **画什么**（场景、对象、元素）
2. **什么感觉**（氛围、情绪、光线）
3. **什么文字**（需要出现的文字及其位置）
4. **什么构图**（焦点在哪、主次关系）
5. **什么风格**（配色、美学、品牌约束）

### 情绪词汇表

为不同情感目标提供精确的视觉描述词：

| 目标情感 | 光线 | 色温 | 空间 | 元素 |
|---------|------|------|------|------|
| 紧迫/焦虑 | 昏暗，局部高光 | 冷调（蓝灰） | 压缩，局促 | 裂痕、倒计时、狭窄通道 |
| 好奇/探索 | 柔和，有神秘感 | 暖冷交界 | 延伸，有深度 | 门、路径、地平线、问号 |
| 豁然开朗 | 突然明亮，穿透性光 | 暖金色 | 开阔 | 光束、云开、拨开迷雾 |
| 自信/确定 | 明亮均匀 | 中性偏暖 | 稳定，对称 | 坚实基座、清晰路径 |
| 兴奋/可能性 | 动态光，多光源 | 丰富多彩 | 广阔 | 火箭、浪潮、绽放 |
| 安心/信任 | 温暖柔和 | 暖调（金琥珀） | 舒适包围 | 握手、盾牌、锚 |
| 决心/行动 | 聚焦光，高对比 | 对比强烈 | 向前延伸 | 箭头、跑道、发射台 |

## 四层提示词架构详解

### 第一层：场景与叙事

这是提示词的灵魂。用2-4句话描述一个**有氛围的视觉场景**。

关键技巧：
- **用隐喻连接概念与画面**："技术债 → 一栋不断加盖却从未修缮基础的大楼"
- **用具体细节创造真实感**：不说"一个城市"，而说"黄昏时分雾气笼罩的东京天际线"
- **用光线传递情绪**：光线是画面情绪的最强调节器
- **用对比创造张力**：左暗右亮、上重下轻、旧与新

场景类型与适用：

| 场景类型 | 描述方式 | 适用页面 |
|---------|---------|---------|
| 全景俯瞰 | 高视角鸟瞰，展示全局 | 封面、愿景、战略总览 |
| 特写聚焦 | 微距细节，一个物体/瞬间 | 数据页、"啊哈时刻" |
| 对比分屏 | 左右或上下对比 | Before/After、方案对比 |
| 路径延伸 | 从近到远的纵深 | 路线图、时间线 |
| 抽象隐喻 | 几何、抽象、概念化 | 概念阐述、框架展示 |
| 人物场景 | 有人物互动的场景 | 案例、团队、协作 |

### 第二层：文字内容

文字必须精确标注位置、大小层级和语言。

**文字层级系统**：

```
Level 1 — Headline（标题）
  位置：通常 top-left 或 top-center
  字号：大（48-72pt 效果）
  字重：Bold
  作用：本页主题的一句话概括
  规则：演讲型尽量不超过 8 个中文字 / 6 个英文词；汇报型和教学型可适当放宽，但仍应简洁明确

Level 2 — Subheadline（副标题）
  位置：紧跟 Headline 下方
  字号：中（24-36pt 效果）
  字重：SemiBold
  作用：对标题的补充说明
  规则：演讲型保持简短；汇报型/教学型可用于补充范围、条件、定义

Level 3 — Key Metric / Quote（关键数据/金句）
  位置：视觉焦点位置（通常 center 或 center-right）
  字号：超大（80-120pt 效果）
  颜色：强调色（如 #FF6B9D）
  作用：视觉锤——一眼就能记住的那个数字或短句

Level 4 — Supporting Points（支撑要点）
  位置：内容区域
  字号：小（14-18pt 效果）
  字重：Regular
  作用：围绕同一主题提供解释、步骤、定义或注释
  规则：
    - 演讲型：0-2条，关键词式
    - 汇报型：2-5条，允许短句解释、图表注释、结论支撑
    - 教学型：3-6条，允许步骤说明、定义、示例、注意事项
```

## 场景化提示词策略

### 演讲型（Keynote）提示词策略

目标：制造记忆点和情绪张力。

写法要求：
- 场景描述更电影化、更具隐喻性
- Headline 极短，最好像一句口号或一记锤子
- 优先使用全屏场景、居中聚焦、金句页构图
- 尽量减少 Supporting Points，更多信息留给讲者说

推荐措辞：
- cinematic, bold, dramatic contrast, iconic, minimal text, high emotional tension

### 汇报型（Report）提示词策略

目标：让页面可讲、可看、可讨论。

写法要求：
- 场景描述仍要有视觉感，但不能压过信息结构
- Headline 直接表达结论，不要故弄玄虚
- 允许图表区、注释区、对比区、分析区同时存在
- 优先使用左文右图、对比分屏、图表增强型构图

推荐措辞：
- structured, analytical, executive-ready, evidence-based, clear hierarchy, boardroom style

### 教学型（Tutorial）提示词策略

目标：帮助理解和记忆，不只是制造美感。

写法要求：
- 场景描述服务于解释，如流程、拆解、层级、关系、步骤
- Headline 要像知识点标题
- 必须强化编号、箭头、框架、标签、步骤层次
- 优先使用步骤流、框架图、示例拆解、前后对照构图

推荐措辞：
- instructional, explanatory, step-by-step, labeled, didactic clarity, concept visualization

### 第三层：构图与层次

明确视觉元素的空间关系和视觉权重。

**常用构图模式**：

```
1. 全屏场景 + 文字叠加（封面、愿景、金句页）
   ┌─────────────────────────┐
   │  ██ Headline            │
   │  ░░ Subheadline         │
   │                         │
   │      [Full Scene]       │
   │                         │
   │              ████ Metric│
   │  🔷logo          page# │
   └─────────────────────────┘

2. 左文右图 (35/65)（内容页、方案页）
   ┌──────────┬──────────────┐
   │ Headline │              │
   │          │   [Visual    │
   │ Points:  │    Scene]    │
   │ • xxx    │              │
   │ • xxx    │              │
   │ • xxx    │              │
   │ logo     │        page# │
   └──────────┴──────────────┘

3. 居中聚焦（数据页、金句页）
   ┌─────────────────────────┐
   │                         │
   │      ░░ Context         │
   │                         │
   │      ████████           │
   │      ██ 73% ██          │
   │      ████████           │
   │                         │
   │      ░░ Explanation     │
   │ logo               page#│
   └─────────────────────────┘

4. 对比分屏（Before/After、方案对比）
   ┌────────────┬────────────┐
   │  ██ Before │ ██ After   │
   │            │            │
   │  [Dark,    │ [Bright,   │
   │   old,     │  new,      │
   │   heavy]   │  light]    │
   │            │            │
   │ logo              page# │
   └────────────┴────────────┘

5. 步骤流（教学型、流程型）
   ┌─────────────────────────┐
   │ ██ Step 1 → Step 2 → 3  │
   │                         │
   │ [Icon]   [Icon]   [Icon]│
   │ 说明1     说明2     说明3 │
   │                         │
   │ Key note / warning      │
   │ logo               page#│
   └─────────────────────────┘

6. 图表增强型（汇报型）
   ┌─────────────────────────┐
   │ ██ Conclusion headline  │
   │ ░ Supporting subtitle   │
   │                         │
   │ [Chart / table / graph] │
   │                         │
   │ • Annotation            │
   │ • Insight               │
   │ logo               page#│
   └─────────────────────────┘
```

**不同场景的构图偏好**：
- 演讲型：优先 1 / 3 / 4，减少解释区面积
- 汇报型：优先 2 / 4 / 6，保证结论和证据同页出现
- 教学型：优先 2 / 5 / 4，保证步骤关系和标签清晰

### 第四层：风格统一

每个样式模板生成的 `style-config.md` 都应包含以下完整内容，供注入每个提示词：

```markdown
## Global Style Config

### Dimensions
- Aspect ratio: 16:9 (1920x1080px)

### Color Palette
- Primary: [色值]
- Accent: [色值]
- Background (dark pages): [色值]
- Background (light pages): [色值]
- Text on dark: [色值]
- Text on light: [色值]
- Highlight/Metric: [色值]

### Typography
- Headline: [字体] [字重]
- Subheadline: [字体] [字重]
- Body: [字体] [字重]
- Metric/Highlight: [字体] [字重]

### Brand Elements
- Logo: [位置] [颜色] [大小]
- Page number: [位置] [字体] [颜色]

### Aesthetic
- Overall: [如 "Modern, cinematic, generous whitespace"]
- Dark pages: [如 "Rich, deep, atmospheric"]
- Light pages: [如 "Clean, airy, ample breathing room"]
- Illustrations: [如 "Flat design with subtle depth, geometric shapes"]

### Consistency Rules
- All scenes share the same color temperature range
- Visual motif elements use the accent color as their light source
- Text overlay areas always have sufficient contrast (semi-transparent gradient if needed)
- Brand logo appears on every page in the same position
```

## 分镜间连贯性保障

### 视觉过渡策略

相邻分镜之间的视觉过渡要自然：

| 前一页 → 后一页 | 过渡策略 |
|----------------|---------|
| 封面 → 第一幕首页 | 相同场景，拉远/推近镜头 |
| 同一幕内 | 相同场景不同角度，或相同光线不同对象 |
| 幕间转折 | 光线/色调剧变（如暗→亮），场景大切换 |
| 倒数第二页 → 结尾 | 视角拉到最高/最远，全景式 |

### 色彩情绪弧线

```
页码:  1    2    3    4    5    6    7    8    9   10   11   12
色调:  中 → 暗 → 暗 → 暗 ║ 亮! → 亮 → 亮 → 亮 → 暖 ║ 暖 → 暖 → 金
              第一幕      ║    第二幕                 ║   第三幕
```

第一幕用冷暗色调渲染问题的严峻，转折点用突然的亮色制造冲击，第二幕保持明亮展示解法，第三幕转为温暖金色调传递希望和行动力。

## 三种场景的完整提示词骨架

### 演讲型骨架

```markdown
## Scene & Narrative
[电影化场景 + 强隐喻 + 强情绪]

## Text Overlay
- Headline: [极短标题]
- Key metric / quote: [大数字或金句]

## Composition
- Full-bleed or center-focus
- One dominant focal point
- Minimal supporting text

## Global Style
[注入全局样式]
```

### 汇报型骨架

```markdown
## Scene & Narrative
[有视觉感但克制的场景，用来承托结论和证据]

## Text Overlay
- Headline: [结论句]
- Subheadline: [适用范围/背景说明]
- Chart title / labels: [图表标题与关键标注]
- Supporting points: [2-5条解释]

## Composition
- Structured layout with chart/table/diagram area
- Clear hierarchy: conclusion → evidence → explanation
- Enough negative space to avoid clutter

## Global Style
[注入全局样式]
```

### 教学型骨架

```markdown
## Scene & Narrative
[帮助理解概念或步骤的解释型场景]

## Text Overlay
- Headline: [知识点标题]
- Subheadline: [定义/目的]
- Step labels / framework labels: [步骤或模块标签]
- Supporting points: [3-6条步骤、定义、示例或注意事项]

## Composition
- Step-flow / framework / annotated layout
- Clear directional cues: arrows, numbers, groups
- Visuals must clarify relationships, not merely decorate

## Global Style
[注入全局样式]
```
