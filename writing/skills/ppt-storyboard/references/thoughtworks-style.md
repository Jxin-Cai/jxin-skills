# ThoughtWorks PPT 样式

## 🎨 品牌视觉系统

### 核心配色

**主色**：

- 深青色（Teal）：`#003B4D` - 专业、稳重、品牌主色
- 粉红色（Pink）：`#FF6B9D` - 活力、创新、强调色

**辅助色**：

- 青色（Cyan）：`#65B4C4`
- 橙色（Orange）：`#D9A441`
- 绿色（Green）：`#6FA287`
- 紫色（Purple）：`#8B7BA8`

**背景色**：

- 白色：`#FFFFFF`
- 浅灰：`#F0F0F0` / `#F5F5F5`

**文字色**：

- 黑色：`#000000`（白底）
- 白色：`#FFFFFF`（深色底）

---

## 📐 设计规范

### 页面设置

- **尺寸**：16:9 比例（1920x1080px）
- **边距**：上下左右各 80-100px
- **网格**：12 列网格系统

### 字体规范（官方标准）

**字体家族**：

- **标题**：Bitter（衬线字体）
- **正文**：Inter（无衬线字体）

**使用规则**（严格执行）：

| 元素      | 字体   | 字重                   | 字号    | 说明                  |
| --------- | ------ | ---------------------- | ------- | --------------------- |
| 主标题    | Bitter | **Bold（粗体）**       | 48-72pt | ✅ **只能**使用粗体   |
| 副标题    | Inter  | **SemiBold（半粗体）** | 24-36pt | ✅ **只能**使用半粗体 |
| 正文      | Inter  | **Regular（常规体）**  | 14-18pt | ✅ **只能**使用常规体 |
| 强调内容  | Inter  | **Bold（粗体）**       | 14-18pt | ✅ 正文中的强调部分   |
| 标签/说明 | Inter  | Regular                | 12-14pt | 同正文字重            |

**字重限制（重要！）**：

**Bitter 字体**：

- ✅ **Bold（粗体）** - 唯一允许使用
- ❌ Thin（细体）- 禁止
- ❌ ExtraLight（超细体）- 禁止
- ❌ Light（轻量体）- 禁止
- ❌ Regular（常规体）- 禁止
- ❌ Medium（中等体）- 禁止
- ❌ SemiBold（半粗体）- 禁止
- ❌ ExtraBold（超粗体）- 禁止
- ❌ Black（黑体）- 禁止

**Inter 字体**：

- ✅ **Regular（常规体）** - 正文使用
- ✅ **SemiBold（半粗体）** - 副标题使用
- ✅ **Bold（粗体）** - 强调使用
- ❌ Thin（细体）- 禁止
- ❌ ExtraLight（超细体）- 禁止
- ❌ Light（轻量体）- 禁止
- ❌ Medium（中等体）- 禁止
- ❌ ExtraBold（超粗体）- 禁止
- ❌ Black（黑体）- 禁止

### 文本规范（ThoughtWorks 写作指南）

**公司名称写法**：

- ✅ **Thoughtworks**（首字母 T 大写，w 小写）
- ❌ ThoughtWorks / thoughtworks / THOUGHTWORKS

**大小写规范**：

- **句首大写格式（Sentence case）**：句子首字母大写，内部仅专有名词大写
- ✅ 标题示例："We have fantastic software products"
- ❌ 错误示例："We Have Fantastic Software Products"
- 适用：标题、副标题、正文、图片说明
- 标题末尾：无需句号

**日期格式**：

- 格式：月份 日期, 年份
- ✅ 示例："June 20, 2021"
- ✅ 示例："Sunday June 20, 2021"

**数字写法**（美联社规范）：

- 个位数（0-9）：英文拼写（two, five, nine）
- 两位数及以上：阿拉伯数字（10, 34, 100）
- ✅ "We have two teams"
- ✅ "There are 15 members"

**语言**：

- 官方语言为美式英语（American English）

### 图形规范

- **风格**：扁平化、几何化
- **形状**：菱形、圆形、六边形
- **阴影**：柔和投影（0 4px 12px rgba(0,0,0,0.1)）
- **圆角**：0-12px（根据元素类型）

---

## 📄 页面模板

### 封面页（Cover）

**布局**：

- 背景：深青色 #003B4D 全屏
- Logo：左下角，白色+粉色
- 主标题：白色，60-72pt，**Bitter Bold**，居中或左对齐，垂直居中
- 副标题：粉色 #FF6B9D，24-36pt，**Inter SemiBold**

**适用**：封面、结束页

---

### 章节页（Section）

**布局**：

- 背景：深青色 #003B4D 全屏
- 标题：白色，72pt，**Bitter Bold**，左对齐
- 副标题/编号：粉色 #FF6B9D，36pt，**Inter SemiBold**
- Logo：左下角

**文本规范**：

- 标题使用句首大写格式
- 数字：个位数拼写（two, five），两位数用数字（10, 15）

**适用**：章节过渡、大章节引导

---

### 内容页 - 图文混排（Content with Image）

**布局**：

- 背景：白色 #FFFFFF
- 标题：黑色，48pt，**Bitter Bold**，顶部左对齐
- 副标题：黑色，24pt，**Inter SemiBold**
- 正文：黑色，16-18pt，**Inter Regular**
- 强调文字：黑色，16-18pt，**Inter Bold**
- 主体：左侧文字（40%）+ 右侧图片/图表（60%）
- 底部色带（可选）：4 色条（橙/深青/浅青/粉），各 25%宽

**文本规范**：

- 所有文本使用句首大写格式
- 标题末尾无句号
- 列表项简洁，关键词式

**适用**：概念介绍、内容说明

---

### 内容页 - 纯文字（Content with Cards）

**布局**：

- 背景：白色 #FFFFFF
- 标题：黑色，48pt，**Bitter Bold**，顶部
- 正文：黑色，16-18pt，**Inter Regular**，段落文本，左对齐
- 卡片：浅灰背景 #F0F0F0，多列布局（2-3 列）
- 卡片标题：彩色背景（使用辅助色），白色文字，**Inter SemiBold**
- 卡片内容：白色/黑色文字，**Inter Regular**

**文本规范**：

- 标题：句首大写，无句号
- 正文：句首大写
- 列表项：句首大写

**适用**：要点列举、多项说明

---

### 图表页 - 流程图（Diagram - Flow）

**布局**：

- 背景：白色 #FFFFFF
- 标题：黑色，48pt，**Bitter Bold**，顶部，可选粉色下划线
- 左侧：文字说明（30-40%），**Inter Regular**，16-18pt
- 右侧：流程图（60-70%）
- 流程图风格：
  - 菱形/矩形组合
  - 使用品牌色填充
  - 箭头连接
  - 色块内文字：白色，**Inter SemiBold**，14-16pt
  - 色块外标签：黑色，**Inter Regular**，14-16pt

**文本规范**：

- 标题：句首大写
- 流程步骤：简短关键词
- 说明文字：句首大写

**适用**：流程展示、方法论

---

### 图表页 - 关系图（Diagram - Relationship）

**布局**：

- 背景：白色 #FFFFFF（或左白右浅灰 #F0F0F0）
- 标题：黑色，48pt，**Bitter Bold**，顶部
- 左侧：文字说明（30-40%），**Inter Regular**，16-18pt
- 右侧：关系图（60-70%）
- 关系图类型：
  - 圆形（演进、层级）
  - 六边形蜂窝（能力、网络）
  - 环形（组成、原则）
- 图形内文字：白色，**Inter SemiBold**，14-16pt
- 图形外标签：黑色，**Inter Regular**，12-14pt

**文本规范**：

- 图形内：简短关键词
- 图形外：句首大写的说明

**适用**：关系展示、能力地图

---

### 表格页（Table）

**布局**：

- 背景：白色 #FFFFFF
- 标题：黑色，48pt，**Bitter Bold**，顶部
- 左侧：说明文字（20-30%），**Inter Regular**，14-16pt
- 右侧：表格（70-80%）
- 表格样式：
  - 表头：彩色渐变（粉/橙/绿），白色文字，**Inter SemiBold**，14-16pt
  - 第一列：深青色 #003B4D 背景，白色文字，**Inter SemiBold**
  - 数据单元格：浅灰 #F0F0F0 背景，黑色文字，**Inter Regular**，14-16pt

**文本规范**：

- 表头：关键词式，简短
- 数据：简洁表达
- 数字：遵循 AP 规范（个位数拼写，两位数以上用数字）

**适用**：数据对比、指标展示

---

## 🎯 应用到 PPT 生成

### 样式配置模板

```markdown
# PPT 样式配置 - ThoughtWorks 风格

## 品牌识别

- **品牌**：ThoughtWorks
- **风格定位**：专业、现代、创新

## 核心配色

### 主色

- 深青色（Teal）：#003B4D - 品牌主色
- 粉红色（Pink）：#FF6B9D - 强调色

### 辅助色

- 青色：#65B4C4
- 橙色：#D9A441
- 绿色：#6FA287
- 紫色：#8B7BA8

### 背景和文字

- 白色背景：#FFFFFF
- 浅灰背景：#F0F0F0
- 黑色文字：#000000
- 白色文字：#FFFFFF

## 布局规范

- **比例**：16:9
- **边距**：80-100px
- **分栏**：左文右图（40/60）或左图右文
- **对齐**：左对齐为主，标题可居中

## 字体规范

- **字体**：无衬线（Sans-serif）
- **主标题**：48-72pt，粗体
- **副标题**：24-36pt
- **正文**：14-18pt
- **标签**：12-14pt

## 图形规范

- **风格**：扁平化、几何化
- **形状**：菱形、圆形、六边形
- **阴影**：柔和（0 4px 12px rgba(0,0,0,0.1)）
- **线条**：粗线条，简洁

## 页面元素

- **Logo**：左下角固定位置
- **页码**：右下角
- **装饰**：底部色带（可选）

## 设计原则

1. **简洁至上**：去除非必要元素
2. **对比鲜明**：深浅色对比、字号对比
3. **留白充分**：不拥挤，呼吸感
4. **图形化表达**：用图形代替文字
5. **品牌一致**：严格遵循色板和字体

---

## 📋 排版规范速查表

### 字体使用（严格执行）

| 元素   | 字体   | 字重     | ✅ 允许            | ❌ 禁止                                                       |
| ------ | ------ | -------- | ------------------ | ------------------------------------------------------------- |
| 主标题 | Bitter | Bold     | Bold（粗体）       | Thin/ExtraLight/Light/Regular/Medium/SemiBold/ExtraBold/Black |
| 副标题 | Inter  | SemiBold | SemiBold（半粗体） | Thin/ExtraLight/Light/Medium/ExtraBold/Black                  |
| 正文   | Inter  | Regular  | Regular（常规体）  | Thin/ExtraLight/Light/Medium/ExtraBold/Black                  |
| 强调   | Inter  | Bold     | Bold（粗体）       | Thin/ExtraLight/Light/Medium/SemiBold/ExtraBold/Black         |

### 文本规范（必须遵守）

| 规范项   | 规则                      | ✅ 正确                    | ❌ 错误                    |
| -------- | ------------------------- | -------------------------- | -------------------------- |
| 公司名称 | T 大写，w 小写            | Thoughtworks               | ThoughtWorks/thoughtworks  |
| 大小写   | 句首大写（Sentence case） | We have fantastic products | We Have Fantastic Products |
| 标题末尾 | 无句号                    | Our approach               | Our approach.              |
| 日期格式 | 月份 日期, 年份           | June 20, 2021              | 2021-06-20                 |
| 数字     | 个位拼写，两位数字        | two teams, 15 members      | 2 teams, fifteen members   |
| 语言     | 美式英语                  | -                          | -                          |

### 关键限制

**字体限制**：

- ⚠️ Bitter 字体**只能**使用 Bold（粗体）
- ⚠️ Inter 字体**只能**使用 Regular、SemiBold、Bold
- ⚠️ 禁止使用任何细体、轻量体、中等体、超粗体、黑体变体

**文本限制**：

- ⚠️ 所有文本**必须**使用句首大写格式
- ⚠️ 标题内部**仅**专有名词大写（Thoughtworks, Python, DevOps 等）
- ⚠️ 公司名称**必须**写作 Thoughtworks（不是 ThoughtWorks）

---

## 🎯 提示词模板要素

生成 ThoughtWorks 风格 PPT 时，提示词应包含：

### 必需要素

- ✅ 深青色 #003B4D 和粉红色 #FF6B9D 为核心配色
- ✅ 标题使用 **Bitter Bold**
- ✅ 副标题使用 **Inter SemiBold**
- ✅ 正文使用 **Inter Regular**
- ✅ 句首大写格式（Sentence case）
- ✅ 公司名：Thoughtworks（T 大写，w 小写）
- ✅ 扁平化图形，几何形状
- ✅ Logo 固定左下角
- ✅ 16:9 比例

### 布局要素

- ✅ 大标题+留白（封面/章节页）
- ✅ 左文右图（内容页 40/60）
- ✅ 卡片式布局（多项内容）
- ✅ 图表清晰简洁

### 色彩运用

- ✅ 深色页面使用深青色 #003B4D 背景
- ✅ 白色页面用黑色 #000000 文字
- ✅ 强调内容用粉红色 #FF6B9D
- ✅ 图表使用辅助色组合

### 文本规范

- ✅ 句首大写格式（标题、副标题、正文、图片说明）
- ✅ 标题末尾无句号
- ✅ 个位数数字拼写（two, five），两位数及以上用数字（10, 34）
- ✅ 日期格式：June 20, 2025

---

## 📝 提示词示例

### 封面页完整提示词
```

Create a Thoughtworks-branded PPT cover page

**Title**: AI-driven development in 2025

**Thoughtworks Brand Style**:

- Background: Teal #003B4D full screen
- Main title: White text, 72pt, **Bitter Bold**, center aligned, vertically centered
- Title text: "AI-driven development in 2025" (sentence case)
- Subtitle: Pink #FF6B9D, 36pt, **Inter SemiBold**, below title
- Logo: Bottom left corner, Thoughtworks logo (white + pink accent)
- Copyright: Bottom, "© 2025 Thoughtworks", white, 10pt, **Inter Regular**

**Typography Rules**:

- Use sentence case (first letter capitalized, rest lowercase except proper nouns)
- Title font: Bitter Bold ONLY (no other weights)
- Subtitle font: Inter SemiBold ONLY
- Company name: "Thoughtworks" (capital T, lowercase w)

**Layout**:

- 16:9 ratio (1920x1080px)
- Margins: 80-100px all sides
- Generous whitespace, minimalist design

**Language**: English (or Chinese with proper font support)
**Style**: Flat design, modern, professional

```

### 内容页完整提示词

```

Create a Thoughtworks-branded PPT content page

**Title**: Our approach
**Subtitle**: Collaborative and co-creative

**Content**:

- One team
- Open and transparent
- Design + technology + business
- Cultivate innovation

**Thoughtworks Brand Style**:

- Background: White #FFFFFF
- Title: Black, 48pt, **Bitter Bold**, top left aligned
- Title text: "Our approach" (sentence case, no period)
- Subtitle: Black, 24pt, **Inter SemiBold**
- Content text: Black, 16-18pt, **Inter Regular**
- Layout: Left text (40%) + Right image (60%)
- Bottom color band: Orange #D9A441 / Teal #003B4D / Cyan #65B4C4 / Pink #FF6B9D (25% each, 30px height)
- Logo: Bottom left corner
- Page number: Bottom right, "109" (or appropriate number)

**Typography Rules**:

- All text in sentence case
- No periods at end of titles
- Numbers: Spell out single digits (two, five), use numerals for 10+ (15, 34)
- List items: Brief, keyword-style

**Fonts**:

- Title: **Bitter Bold ONLY**
- Subtitle: **Inter SemiBold ONLY**
- Body text: **Inter Regular ONLY**
- Emphasis: **Inter Bold ONLY**

**Layout**:

- 16:9 ratio
- Clear visual hierarchy
- Generous spacing

**Style**: Flat design, modern, professional, brand-consistent

```

---

## ✅ 质量检查清单

生成完成后必须检查：

### 字体检查
- [ ] 标题使用 Bitter Bold（不是其他字重）
- [ ] 副标题使用 Inter SemiBold（不是其他字重）
- [ ] 正文使用 Inter Regular（不是其他字重）
- [ ] 强调使用 Inter Bold
- [ ] 无细体、轻量体、中等体、超粗体、黑体

### 文本检查
- [ ] 公司名称：Thoughtworks（T大写，w小写）
- [ ] 所有文本使用句首大写格式
- [ ] 标题末尾无句号
- [ ] 个位数拼写（two, five），两位数及以上用数字（10, 34）
- [ ] 日期格式正确（June 20, 2025）

### 配色检查
- [ ] 主色：深青 #003B4D 和粉红 #FF6B9D
- [ ] 辅助色：青/橙/绿/紫（仅这6种颜色）
- [ ] 背景：白色或深青色（无其他颜色）
- [ ] 文字：黑色（白底）或白色（深色底）

### 布局检查
- [ ] 16:9比例
- [ ] 边距80-100px
- [ ] Logo左下角
- [ ] 页码右下角（如适用）
- [ ] 深色封面 + 白色内容页

---

**版本**：v1.1
**更新**：2025-01-30
**基于**：ThoughtWorks官方PPT样式分析 + 官方排版规范
**样本数**：10页
**适用**：企业级、咨询类、技术类PPT
```
