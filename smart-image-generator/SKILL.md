---
name: smart-image-generator
description: 智能图片和PPT生成工具，自动识别场景，协作设计提示词，使用Gemini生成专业图片。支持ThoughtWorks等企业级样式，完美支持中文。
---

# 智能图片生成器

一个基于Gemini的智能图片生成系统，支持单图生成和完整PPT制作。

## 🎯 何时使用

**单图生成**：
- "生成图片" / "生成封面" / "生成海报"
- "流程图" / "思维导图" / "可视化"

**PPT生成**：
- "生成PPT" / "做个PPT" / "制作演示文稿"

**账号管理**：
- "换号" / "重新登录" / "切换账号"

---

## 📋 AI执行流程

### 流程A：单图生成

#### Step 1: 理解需求

**获取信息**：
- 内容来源：文件路径 / URL / 直接文本
- 场景类型：自动检测或用户指定
- 视觉风格：默认obsidian，或用户指定

**自动检测场景**：
- 包含"流程"/"步骤" → flowchart
- 包含"思维"/"结构" → mindmap
- 包含"活动"/"宣传" → poster
- 包含"笔记"/"插图" → note
- 默认 → cover

#### Step 2: 生成提示词

**执行命令**：

```bash
cd skills/custom-skills/smart-image-generator

bun scripts/generate-prompt.ts \
  --scene ${场景类型} \
  --style ${视觉风格} \
  --file ${输入文件路径} \
  --content "${内容文本}"
```

**脚本自动处理**：
- ✅ 检测语言（中文/英文）
- ✅ 提取标题、关键词
- ✅ 生成专业提示词
- ✅ 保存到合适位置

**输出位置优先级**：
1. 用户指定 `--output` → 使用指定路径
2. 提供 `--file` → 输入文件同目录
3. 无文件 → 项目根目录

#### Step 3: 确认提示词

**展示给用户**：

```
✅ 已生成提示词！

📝 提示词预览：
---
Create a obsidian-style cover (16:9):
Title: AI时代的研发新范式
Visual: 专业现代的构图
...
---

📁 保存位置: docs/smart-image-generator-output/prompts/cover-obsidian-2025-01-30.md

这个提示词是否满意？
- 满意：我将立即生成图片
- 需要调整：请告诉我如何修改
```

#### Step 4: 生成图片

**用户确认后执行**：

```bash
bun scripts/generate-image.ts \
  --prompt ${提示词文件路径}
```

**首次使用自动登录**：
1. 打开Chrome浏览器（只1个窗口）
2. 跳转到gemini.google.com
3. 等待用户登录（最多5分钟）
4. 登录成功，浏览器关闭
5. 保存登录状态，后续自动使用

**后续使用**：直接生成，无需登录

#### Step 5: 返回结果

```
✅ 图片生成成功！

📁 提示词: docs/smart-image-generator-output/prompts/cover-obsidian-2025-01-30.md
📁 图片:   docs/smart-image-generator-output/images/cover-obsidian-2025-01-30.png

您可以：
- 查看生成的图片
- 修改提示词后重新生成
```

---

### 流程B：PPT生成

#### Step 1: 理解内容

**获取信息**：
- 内容文件（Markdown格式）
- PPT名称（自动提取或用户指定）
- 语言设置（中文/英文）
- 样式风格（默认thoughtworks）

#### Step 2: 制定计划

**分析内容结构**：

```
用户内容：
# 主标题
## 章节1
### 要点1.1
### 要点1.2
## 章节2
...

分页计划：
- 第1页：封面（主标题）
- 第2页：章节引导（章节1）
- 第3页：内容页（要点1.1）
- 第4页：内容页（要点1.2）
- ...
- 共N页
```

**展示计划给用户**：

```
📋 PPT分页计划

标题：AI时代的研发新范式
样式：ThoughtWorks企业风格
共计：10页

页面列表：
1. 封面 - AI时代的研发新范式
2. 章节 - 背景介绍
3. 内容 - 技术变革
4. 内容 - 行业趋势
...

是否开始生成？
```

#### Step 3: 生成PPT

**用户确认后执行**：

```bash
bun scripts/generate-ppt.ts \
  --content ${内容文件} \
  --name "${PPT名称}" \
  --chinese \
  --style thoughtworks
```

**自动流程**：
1. 创建目录：`ppt/{ppt-name}/`
2. 生成样式配置：`prompts/style-config.md`
3. 为每页生成提示词：`prompts/page-01.md` ...
4. 组合样式+内容
5. 逐页调用Gemini生成图片
6. 保存到：`images/page-01.png` ...

**进度提示**：

```
🎨 正在生成PPT...

✓ 第1页已生成（封面）
✓ 第2页已生成（章节引导）
⏳ 正在生成第3页...
```

#### Step 4: 返回结果

```
✅ PPT生成完成！

📁 PPT目录: ppt/AI时代的研发新范式/
📂 提示词:   ppt/AI时代的研发新范式/prompts/ (10个文件)
🖼️  图片:     ppt/AI时代的研发新范式/images/ (10张)
📄 分页计划: ppt/AI时代的研发新范式/plan.json

共生成 10 页，用时约 8 分钟
```

---

### 流程C：账号管理

#### 换号/重新登录

**触发关键词**：
- "换号" / "重新登录" / "切换账号"
- "登出" / "logout"

**AI执行步骤**：

1. **识别意图**

```
用户: 我想换个账号

AI: 检测到您想要换号重新登录。
```

2. **智能搜索技能位置**

```
正在搜索 smart-image-generator 技能...

✓ 找到技能位置: ~/.cursor/skills/smart-image-generator
```

3. **执行登出**

```bash
cd ${技能目录}
bun scripts/logout.ts
```

4. **确认结果**

```
✅ 登录状态已清除

💡 下次生成图片时会自动弹出浏览器，请登录新账号。
```

---

## 🎨 样式系统

### 单图样式

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| `obsidian` | 手绘知识风格（默认） | 笔记、知识管理 |
| `notion` | 现代SaaS风格 | 产品介绍、专业文档 |
| `minimal` | 极简主义 | 简洁设计 |
| `chalkboard` | 黑板风格 | 教学、演示 |

### PPT样式

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| `thoughtworks` | 企业咨询风格（默认） | 企业级PPT、技术方案 |
| `professional` | 专业商务 | 商务汇报、项目提案 |
| `modern` | 现代简约 | 产品发布、创意展示 |
| `minimal` | 极简主义 | 学术演讲、数据报告 |

### ThoughtWorks风格特点

**配色**：
- 深青色 #003B4D（主色）
- 粉红色 #FF6B9D（强调色）
- 辅助色：青#65B4C4 / 橙#D9A441 / 绿#6FA287 / 紫#8B7BA8

**布局**：
- 深色封面 + 白色内容页
- 左文右图（40/60）
- Logo固定左下角

**图形**：
- 扁平化几何图形
- 菱形、圆形、六边形

---

## 📂 目录结构

### 单图输出

```
输入文件目录/smart-image-generator-output/
├── prompts/
│   └── cover-obsidian-2025-01-30.md
└── images/
    └── cover-obsidian-2025-01-30.png
```

### PPT输出

```
ppt/
  {ppt-name}/
    prompts/
      style-config.md      # 共用样式配置
      page-01.md           # 各页提示词
      page-02.md
      ...
    images/
      page-01.png          # 各页图片
      page-02.png
      ...
    plan.json             # 分页计划
```

---

## 🔧 技术要点

### 中文支持

**完美支持中文**：
- ✅ 使用UTF-8编码传输
- ✅ 自动检测内容语言
- ✅ 中文内容自动添加中文标记
- ✅ PPT支持中文文字生成

### 自动登录

**无需手动配置**：
- ✅ 首次自动打开浏览器
- ✅ 登录状态自动保存
- ✅ 过期自动重新登录
- ✅ 5分钟超时，支持2FA

**登录数据存储**：
- Cookies：`~/.local/share/smart-image-generator/cookies.txt`
- Profile：`~/.local/share/smart-image-generator/chrome-profile/`

---

## 📝 命令参考

### 单图生成

```bash
# 从文件生成
bun scripts/generate-prompt.ts --scene cover --file article.md
bun scripts/generate-image.ts --prompt 提示词路径

# 从内容生成
bun scripts/generate-prompt.ts --scene flowchart --content "流程说明"
bun scripts/generate-image.ts --prompt 提示词路径
```

### PPT生成

```bash
# 基础用法（ThoughtWorks默认样式）
bun scripts/generate-ppt.ts -c content.md

# 完整参数
bun scripts/generate-ppt.ts \
  -c content.md \
  -n "PPT名称" \
  --chinese \
  --style thoughtworks
```

### 账号管理

```bash
# 清除登录
bun scripts/logout.ts

# 检查登录状态
bun scripts/logout.ts --check
```

---

## ⚠️ AI执行注意事项

1. **征求用户确认**：生成图片前必须展示提示词并获得同意
2. **明确输出位置**：告知用户文件保存在哪里
3. **自动处理登录**：不要让用户手动配置，系统会自动处理
4. **支持迭代优化**：用户可以修改提示词后重新生成
5. **PPT耗时提醒**：告知用户10页PPT约需5-10分钟

---

## 📚 场景类型

| 场景 | 描述 | 触发词 |
|------|------|--------|
| `cover` | 文章封面图 | 封面、头图 |
| `flowchart` | 流程图 | 流程、步骤、工作流 |
| `poster` | 宣传海报 | 海报、活动、宣传 |
| `mindmap` | 思维导图 | 思维导图、知识图 |
| `note` | 笔记插图 | 笔记、插图、说明 |

---

## 🎯 使用示例

### 示例1：为文章生成封面

```
用户: 帮我为 docs/article.md 生成封面

AI: 好的，正在分析文章内容...
    
    检测到文章标题："AI时代的研发新范式"
    场景类型：封面图
    内容语言：中文
    
    正在生成提示词...
    
    ✅ 提示词已生成！
    
    [展示提示词预览]
    
    是否开始生成图片？

用户: 开始吧

AI: [执行生成...]
    
    ✅ 图片生成成功！
    📁 图片: docs/smart-image-generator-output/images/cover-obsidian-2025-01-30.png
```

### 示例2：生成PPT

```
用户: 帮我生成一个PPT，内容在 presentation.md

AI: 好的，正在分析内容...
    
    📋 分页计划：
    - 第1页：封面
    - 第2页：背景介绍
    - 第3页：核心理念
    ...
    - 共8页
    
    使用ThoughtWorks企业风格
    
    是否开始生成？

用户: 开始

AI: [执行生成...]
    
    ✓ 第1页已生成
    ✓ 第2页已生成
    ...
    
    ✅ PPT生成完成！
    📁 目录: ppt/AI时代的研发新范式/
```

### 示例3：换号重新登录

```
用户: 我想换个账号

AI: 检测到您想要换号重新登录。
    
    🔍 正在搜索技能位置...
    ✓ 找到: ~/.cursor/skills/smart-image-generator
    
    🔐 正在清除登录状态...
    
    ✅ 登录状态已清除
    💡 下次生成图片时会自动弹出浏览器，请登录新账号。
```

---

## 🔍 参考资源

### 场景定义
- `references/scene-types/*.md` - 各场景详细说明

### 样式定义
- `references/styles/*.md` - 各样式详细规范

---

**版本**: v2.4.0  
**更新**: 2025-01-30
