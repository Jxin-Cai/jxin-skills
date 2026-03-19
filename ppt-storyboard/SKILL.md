---
name: ppt-storyboard
description: PPT叙事分镜设计技能。传入文章内容和叙事对象（如管理层、投资方、技术团队），围绕文章内容设计叙述分镜，每个分镜包含一页PPT的内容和图片生成提示词。确认后逐个调用 gemini-image-gen 技能生成图片，最后自动合成 PDF 文件。当用户需要制作PPT、演示文稿、做汇报材料、生成演示分镜时使用此技能。即使用户只说"帮我做个PPT"或"把这篇文章做成演示"，也应该触发此技能。
---

# PPT 叙事分镜设计器

将文章内容转化为一场有叙事弧线的演示——不是信息罗列，而是一部有铺垫、冲突、高潮和回响的三幕剧。

## 核心理念

> "People who know what they're talking about don't need PowerPoint." — Steve Jobs

一份好的演示不是把文章搬到幻灯片上。它是一场**导演过的体验**：

1. **一页只说一件事** — 观众的注意力是稀缺资源，每页只传递一个核心信息
2. **叙事弧线驱动** — 每一页都有"为什么在这里"的理由，整体构成起承转合
3. **视觉即论证** — 图片不是装饰，是论点本身的一部分，观众看到图就能领会意思
4. **情感先于信息** — 先决定这一页要让观众感受到什么，再决定放什么内容
5. **视觉母题贯穿** — 用一个反复出现的意象串联整个演示，形成记忆锚点

## 执行流程

### Step 1: 获取输入

需要三个关键输入：

1. **文章内容**（必需）：Markdown 文件路径、URL、或直接粘贴的文本
2. **叙事对象**（必需）：演示的目标受众
3. **核心主张**（可选）：用户希望这场演示最终传达的一句话结论

如果用户没有指定叙事对象，**必须先澄清**。用 AskUserQuestion 询问：

```
这份演示是给谁看的？不同受众会影响叙事策略和信息密度。

常见受众类型：
- 管理层 / C-Level：关注战略价值、ROI、风险
- 投资方：关注商业模式、市场规模、增长潜力
- 技术团队：关注架构、实现细节、技术选型
- 客户/合作伙伴：关注价值主张、案例、落地效果
- 通用受众：平衡各方面信息
```

### Step 2: 提炼核心主张与叙事弧线

**不要急着拆分内容。先回答一个问题：观众听完这场演示，脑子里应该留下的那一句话是什么？**

这就是**核心主张（One Message）**。所有分镜都是为这句话服务的论据。

然后基于文章内容和受众特征，设计**三幕式叙事弧线**：

```
第一幕：建立（Setup）      — 让观众意识到"这件事跟我有关"
  ├── 共鸣点：一个观众感同身受的现状/痛点/问题
  ├── 冲突点：揭示真正的矛盾——为什么现状不可持续
  └── 情感目标：好奇 → 紧迫

第二幕：展开（Confrontation）— 展示解法，用证据构建信念
  ├── 核心洞察：打破旧认知的关键转折
  ├── 论证链：支撑核心主张的2-3条证据线
  ├── "啊哈时刻"：一个让人眼前一亮的数据/类比/演示
  └── 情感目标：好奇 → 认同 → 兴奋

第三幕：收束（Resolution）  — 把能量转化为行动
  ├── 愿景：如果采纳方案，未来会怎样
  ├── 行动召唤：明确的下一步
  └── 情感目标：兴奋 → 确信 → 行动意愿
```

**受众适配策略**：

| 受众类型 | 信息密度 | 叙事重心 | "啊哈时刻"偏好 | 行动召唤类型 |
|---------|---------|---------|--------------|------------|
| 管理层 | 极低（每页1个数字或1句话） | 战略价值、风险规避 | 一个惊人的ROI数字 | 审批/拍板决策 |
| 投资方 | 低-中（数据+叙事） | 增长飞轮、护城河 | 市场规模对比图 | 投资/合作 |
| 技术团队 | 中（可含架构细节） | 技术优雅性、可行性 | 架构对比before/after | 技术选型/启动开发 |
| 客户 | 低（聚焦价值） | 痛点→方案→效果 | 客户案例的量化成果 | 签约/试用 |
| 通用受众 | 低-中 | 故事线清晰 | 一个直观的类比 | 理解/认同 |

### Step 3: 选择视觉母题

**视觉母题（Visual Motif）** 是贯穿整个演示的核心意象，它像电影的主旋律一样反复出现、逐步演变。

基于核心主张，选择一个视觉母题。例如：

- 谈"数字化转型" → 母题：**从迷雾到清晰** — 第一幕朦胧模糊，逐渐变得锐利清晰
- 谈"增长" → 母题：**种子到大树** — 从一粒种子开始，逐步展开成参天大树
- 谈"效率提升" → 母题：**齿轮到火箭** — 从笨重的齿轮组逐渐变为流线型火箭
- 谈"创新" → 母题：**打破边界** — 从框内到框外，从二维到三维

母题在分镜中的体现方式：
- **封面**：母题的起始状态（如迷雾中的一束光）
- **第一幕**：母题的困境态（如被迷雾笼罩的城市）
- **转折页**：母题的突破瞬间（如光芒穿透迷雾）
- **第二幕**：母题逐渐展开（如迷雾消散，轮廓渐清）
- **高潮页**：母题的完成态（如清晰的全景）
- **结尾**：母题的升华（如晴空万里，远方更广阔）

### Step 4: 设计分镜

基于三幕叙事弧线，将文章内容拆分为分镜序列。每个分镜对应PPT的一页。

**每个分镜必须包含以下字段**：

```
分镜 N: [页面类型]
├── 叙事角色：这页在三幕剧中的位置和功能
│   └── 例："第一幕·冲突点 — 揭示当前方案的致命缺陷"
├── 情感目标：观众看完这页应该感受到什么
│   └── 例："焦虑 → 紧迫感"
├── 核心信息：这页传递的唯一核心信息（只能有一条）
│   └── 例："当前架构的技术债已到临界点"
├── 母题状态：视觉母题在这一页的演变阶段
│   └── 例："齿轮组开始出现裂痕"
├── 过渡逻辑：从上一页到这一页的逻辑衔接
│   └── 例："上一页展示了市场机会，这页揭示我们还没准备好抓住它"
└── 图片提示词：（见下方提示词架构）
```

**分镜数量指导**：

| 演示时长 | 管理层 | 技术团队 | 投资方 | 客户 |
|---------|--------|---------|--------|------|
| 10分钟 | 8-10页 | 10-14页 | 8-12页 | 8-10页 |
| 20分钟 | 12-16页 | 16-22页 | 14-18页 | 12-16页 |
| 30分钟 | 18-22页 | 22-30页 | 18-24页 | 16-20页 |

**节奏设计原则**：

1. **信息页与呼吸页交替** — 每2-3页密集内容后，插入一页留白/过渡/金句页
2. **幕间有转折页** — 第一幕到第二幕之间必须有一个"转折页"（通常是一个反问或数据炸弹）
3. **高潮前有蓄力** — 最重要的一页之前，放一个安静的、制造期待的页面
4. **结尾要余韵** — 不要结束在细节上，最后一页要拉高视角、留下回响

### Step 5: 构建图片提示词

**提示词不是在描述"一张PPT的排版"，而是在指导AI创作"一帧视觉叙事"。**

每个分镜的提示词由四层构成：

#### 第一层：场景与叙事（最重要）

描述这一页要呈现的**视觉场景**，它必须直接服务于本页的核心信息和情感目标。

```
例（好）：A vast, fog-covered cityscape at dusk. Towering buildings are barely visible
through thick gray haze. One building in the center has a single bright window — a
warm golden light cutting through the murk. The mood is tense, suffocating, yet
that single light creates a sense of quiet hope.

例（差）：A PPT slide with a city image on the right side, title on the left,
white background.
```

**核心区别**：好的提示词描述的是一个有氛围、有情绪、有视觉焦点的**场景**；差的提示词描述的是一个**布局**。

#### 第二层：文字内容层

明确指定需要出现在画面中的文字及其层级关系。

```
Text overlay:
- Headline (top-left, large, bold): "技术债的临界点"
- Subheadline (below headline, medium): "The tipping point of technical debt"
- Key metric (center-right, very large, highlighted): "73%"
- Metric label (below metric, small): "系统维护成本占比"
```

**文字规则**：
- 主标题（Headline）：每页必须有，是本页核心信息的一句话提炼
- 支撑数据/金句：如果有，用突出的方式展示（大字号、对比色）
- 正文要点：最多2-3条，关键词式，不写长句
- 中文标题 + 英文副标题的双语模式是默认推荐（除非用户指定）

#### 第三层：构图与层次

指定视觉元素的空间关系、主次层级。

```
Composition:
- Layout: Split — left 35% text area (dark overlay for readability), right 65% visual scene
- Visual hierarchy: Metric "73%" is the dominant element (largest, brightest)
- Depth: Foreground = text + metric, Midground = lit building, Background = fog-covered city
- Focal point: The single golden window draws the eye first, then up to the metric
```

#### 第四层：风格统一层

确保与整个演示的视觉系统一致。这一层在所有分镜中保持相同（从选定的样式配置中注入）。

```
Global style:
- Aspect ratio: 16:9 (1920x1080)
- Color palette: [从样式配置注入]
- Typography: [从样式配置注入]
- Brand elements: [从样式配置注入]
- Overall aesthetic: Modern, clean, generous whitespace, flat design with subtle depth
```

**完整提示词示例**：

```markdown
# Slide 3 — The Tipping Point（第一幕·冲突点）

## Scene & Narrative
A vast, fog-covered cityscape at dusk, viewed from a high vantage point. Dense gray
haze blankets the city — buildings are barely visible silhouettes. In the center, one
building has a single bright window emitting warm golden light that cuts through the
murk like a beacon. The atmosphere is heavy and tense, but that one light creates a
quiet sense of urgency — something must change.

This visual is a metaphor: the fog represents accumulated technical debt obscuring the
path forward; the golden light is the opportunity that's still within reach but fading.

## Text Overlay
- Headline (top-left, white, bold, large): "技术债的临界点"
- Subheadline (below headline, white, medium, 70% opacity): "When maintenance cost exceeds innovation capacity"
- Key metric (center-right, #FF6B9D highlight, very large 120pt): "73%"
- Metric label (below metric, white, small): "of engineering time spent on maintenance"

## Composition
- Layout: Full-bleed background image with text overlay on left 35% (semi-transparent dark gradient for readability)
- Visual hierarchy: "73%" is the dominant visual element → golden window → headline
- Depth: Text layer (foreground) → single lit building (midground) → fog city (background)
- Focal point: Golden window at center-right, naturally draws eye to the metric above it

## Global Style
- Aspect ratio: 16:9 (1920x1080px)
- Primary colors: Teal #003B4D, Pink #FF6B9D
- Headline font: Bitter Bold
- Body font: Inter Regular / SemiBold
- Aesthetic: Modern, cinematic, generous whitespace where text appears
- Brand: Thoughtworks logo, bottom-left, small, white
```

### Step 6: 展示分镜计划，等待用户确认

将分镜计划以**叙事弧线视图**展示给用户，不仅展示每页内容，更要展示整体叙事结构：

```
📋 叙事分镜计划

🎯 叙事对象：管理层
📄 文章来源：xxx.md
💬 核心主张："AI不是工具升级，是研发模式的范式转移"
🎭 视觉母题：从迷雾到清晰 — 模糊的轮廓逐渐变为锐利的全景
📊 共 12 页分镜

━━━━━━ 第一幕：建立（为什么这件事很紧迫）━━━━━━

 1. 🎬 封面 — "穿越迷雾"
    核心信息：演示主题 | 情感：期待
    母题：晨雾中若隐若现的城市轮廓

 2. 🌫️ 现状 — "我们都感受到了效率瓶颈"
    核心信息：研发效率连续3年下降 | 情感：共鸣
    母题：浓雾中的建筑群，视线受阻

 3. 💥 冲突 — "73%的时间花在维护，不是创新"
    核心信息：技术债已到临界点 | 情感：紧迫
    母题：雾中唯一亮着灯的窗户

 4. ❓ 转折 — "如果不改变，12个月后会怎样？"
    核心信息：不行动的代价 | 情感：焦虑→求变
    母题：迷雾加厚，连最后的光也快消失

━━━━━━ 第二幕：展开（解法与证据）━━━━━━

 5. 💡 洞察 — "AI改变的不是效率，是研发模式本身"
    核心信息：范式转移而非工具升级 | 情感：豁然开朗
    母题：一束强光穿透迷雾

 6. 📐 方案-1 — "代码生成：从写代码到验证代码"
    ...

...

━━━━━━ 第三幕：收束（行动与愿景）━━━━━━

11. 🚀 愿景 — "12个月后的研发团队"
    核心信息：变革后的状态 | 情感：向往
    母题：迷雾完全消散，城市全景清晰可见

12. 🎯 行动 — "三步启动：下周就可以开始"
    核心信息：具体的下一步 | 情感：确信→行动
    母题：清晨的城市，阳光普照，远方更广阔

是否满意这个分镜计划？
- 满意 → 接下来选择视觉样式
- 需要调整 → 请告诉我要修改哪些分镜
```

**重要**：此步骤必须等待用户明确确认，不可自动跳过。

### Step 7: 选择视觉样式

用户确认分镜后，引导用户选择或描述样式。用 AskUserQuestion 提供选项：

```
请选择 PPT 的视觉样式：

1. Thoughtworks 企业风格 - 深青+粉红配色，专业咨询感（参考 references/thoughtworks-style.md）
2. 专业商务 - 蓝灰色系，稳重大气
3. 现代简约 - 黑白为主，强调留白
4. 自定义 - 描述你想要的样式
```

如果用户选择 Thoughtworks 风格，读取 `references/thoughtworks-style.md` 获取完整的品牌规范。

选定样式后，生成一个 `style-config.md` 保存到输出目录的 `prompts/` 下，作为所有分镜提示词的"第四层·风格统一层"模板。

### Step 8: 生成完整提示词文件

基于确认的分镜计划和样式配置，为每个分镜生成完整的四层提示词文件。

**提示词文件命名**：`prompts/01-cover.md`, `prompts/02-status-quo.md`, ... （编号+语义名）

**提示词生成检查清单**：

对每个提示词，确认：
- [ ] 场景描述是否创造了与情感目标匹配的氛围？
- [ ] 视觉母题是否按计划演变？
- [ ] 核心信息是否被视觉化为画面中最突出的元素？
- [ ] 文字层是否只有一个核心信息（而非塞了多条）？
- [ ] 与前一页和后一页的视觉过渡是否自然？
- [ ] 风格层是否与全局样式一致？

### Step 9: 生成图片

开始逐个分镜调用 `gemini-image-gen` 技能生成图片。

**关键执行步骤**：

1. 创建输出目录：`<用户指定路径或当前目录>/ppt-<名称>/`
2. 在 `prompts/` 子目录保存样式配置和每个分镜的提示词文件
3. 在 `images/` 子目录存放生成的图片

**调用方式**：

```bash
# 逐个调用 gemini-image-gen 生成图片
cd <gemini-image-gen 技能目录>

# 第1张
bun scripts/generate-image.ts -p <prompts/01-cover.md 的绝对路径> -o <images/01.png 的绝对路径>

# 等待 15-20 秒（防风控）
sleep 18

# 第2张
bun scripts/generate-image.ts -p <prompts/02-status-quo.md 的绝对路径> -o <images/02.png 的绝对路径>

# 每生成一张，向用户报告进度
# ✅ 分镜 1/12 已生成 — 封面「穿越迷雾」
# ⏳ 等待中...
# ⏳ 正在生成分镜 2/12 — 现状「效率瓶颈」...
```

**每5张额外等待**：每生成5张后，额外等待 30 秒。

**失败重试**：如果某张生成失败，等待 60 秒后重试，最多重试 2 次。如果仍然失败，跳过该分镜并记录，继续生成后续分镜。最后汇总告知用户哪些失败了。

### Step 10: 生成 PDF

所有图片生成完成后，将图片合成为一份 PDF 文件。

```python
python scripts/images_to_pdf.py \
  --images-dir <images 目录路径> \
  --output <输出 PDF 文件路径> \
  --title "<PPT标题>"
```

### Step 11: 返回结果

```
✅ PPT 生成完成！

📁 输出目录：ppt-AI驱动的研发效率提升/
📄 PDF 文件：ppt-AI驱动的研发效率提升/presentation.pdf
📂 分镜提示词：ppt-AI驱动的研发效率提升/prompts/ (12个文件)
🖼️ 分镜图片：ppt-AI驱动的研发效率提升/images/ (12张)

共 12 页，其中 12 页生成成功，0 页失败

🎭 叙事弧线：三幕12页
💬 核心主张："AI不是工具升级，是研发模式的范式转移"
🎨 视觉母题：从迷雾到清晰
```

## 输出目录结构

```
ppt-<名称>/
├── prompts/
│   ├── style-config.md          # 全局样式配置
│   ├── 01-cover.md              # 分镜1 提示词（含四层结构）
│   ├── 02-status-quo.md         # 分镜2 提示词
│   └── ...
├── images/
│   ├── 01.png
│   ├── 02.png
│   └── ...
├── storyboard.json              # 完整分镜计划（含叙事弧线、母题、情感曲线）
└── presentation.pdf             # 最终 PDF 文件
```

## 依赖

- **gemini-image-gen 技能**：用于生成每个分镜的图片
- **Python 3 + reportlab**：用于将图片合成 PDF（如果没装 reportlab，脚本会自动 pip install）
- **Pillow**：图片处理

## 注意事项

1. **核心主张先行** — 不要在没有提炼核心主张的情况下就开始设计分镜
2. **一页一信息** — 如果发现一页想说两件事，拆成两页
3. **叙事对象不可跳过** — 不同受众决定了整个演示的基调
4. **视觉母题要贯穿** — 每个分镜都要标注母题的演变状态
5. **提示词描述场景，不描述布局** — 让AI生成有氛围的画面，而非排版示意图
6. **情感节奏要设计** — 不是匀速叙述，而是有起伏、有蓄力、有释放
7. **分镜计划必须展示给用户并获得确认**
8. **图片生成过程中持续报告进度**
9. **遇到生成失败不中断整体流程**
