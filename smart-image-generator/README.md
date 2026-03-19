# 智能图片生成器

基于 Gemini 的智能图片生成系统，支持单图生成和完整 PPT 制作。

## ✨ 核心功能

- 🎯 **单图生成**：封面、流程图、海报、思维导图等
- 📊 **PPT 生成**：一键生成完整演示文稿，支持 ThoughtWorks 等企业级样式
- 🌍 **完美中文**：自动检测语言，完美支持中文显示
- 🎨 **多种样式**：obsidian、notion、thoughtworks 等
- 🔐 **自动登录**：浏览器登录，无需手动配置 API

---

## 🚀 快速开始

### 1. 环境准备

**必需**：

- [Bun](https://bun.sh) 运行时（1.0.0+）
- [Google Chrome](https://google.com/chrome) 浏览器
- Google 账号

**验证环境**：

```bash
bun --version  # 检查Bun
./check-env.sh  # 或使用环境检查脚本
```

### 2. 安装依赖

```bash
cd skills/custom-skills/smart-image-generator
bun install
```

### 3. 生成第一张图片

```bash
# 快速测试
bun scripts/generate-prompt.ts \
  --scene cover \
  --content "AI时代研发提效"

bun scripts/generate-image.ts \
  --prompt smart-image-generator-output/prompts/cover-obsidian-*.md
```

**首次使用**：

- 🌐 自动打开 Chrome 浏览器
- 👤 在浏览器中登录 Google 账号
- ✅ 登录成功，浏览器自动关闭
- 🎨 开始生成图片

**后续使用**：直接生成，无需登录

---

## 📖 使用指南

### 单图生成

#### 基础流程

```bash
# 1. 生成提示词
bun scripts/generate-prompt.ts \
  --scene cover \
  --style obsidian \
  --content "你的内容"

# 2. 生成图片
bun scripts/generate-image.ts \
  --prompt 提示词文件路径
```

#### 从文件生成

```bash
# 为文章生成封面
bun scripts/generate-prompt.ts \
  --scene cover \
  --file docs/article.md

# 输出位置：docs/smart-image-generator-output/
```

#### 场景类型

| 场景        | 用途     | 示例               |
| ----------- | -------- | ------------------ |
| `cover`     | 文章封面 | 博客头图、文档封面 |
| `flowchart` | 流程图   | 工作流程、步骤说明 |
| `poster`    | 宣传海报 | 活动海报、产品宣传 |
| `mindmap`   | 思维导图 | 知识结构、概念关系 |
| `note`      | 笔记插图 | 学习笔记、说明图   |

#### 视觉风格

| 风格         | 特点                 | 适用               |
| ------------ | -------------------- | ------------------ |
| `obsidian`   | 手绘知识风格（默认） | 笔记、知识管理     |
| `notion`     | 现代 SaaS 风格       | 产品介绍、专业文档 |
| `minimal`    | 极简主义             | 简洁设计           |
| `chalkboard` | 黑板风格             | 教学、演示         |

---

### PPT 生成

#### 基础流程

**1. 准备内容文件（Markdown）**：

```markdown
# AI 时代的研发新范式

## 背景介绍

- AI 技术快速发展
- 开发范式转变

## 核心理念

- 人机协作
- 持续学习

## 实践案例

- 代码生成
- 代码审查
```

**2. 生成 PPT**：

```bash
# 使用默认ThoughtWorks样式
bun scripts/generate-ppt.ts -c content.md

# 或指定名称和样式
bun scripts/generate-ppt.ts \
  -c content.md \
  -n "产品发布会" \
  --style thoughtworks
```

**3. 查看结果**：

```bash
ls ppt/AI时代的研发新范式/
# prompts/  images/  plan.json

open ppt/AI时代的研发新范式/images/
```

#### PPT 样式

| 样式           | 特点                      | 适用场景           |
| -------------- | ------------------------- | ------------------ |
| `thoughtworks` | 深青+粉红企业风格（默认） | 企业咨询、技术方案 |
| `professional` | 蓝灰商务风格              | 商务汇报、项目提案 |
| `modern`       | 多彩现代风格              | 产品发布、创意展示 |
| `minimal`      | 黑白极简风格              | 学术演讲、数据报告 |

#### ThoughtWorks 样式详解

**配色系统**：

- 主色：深青 #003B4D
- 强调：粉红 #FF6B9D
- 辅助：青#65B4C4 / 橙#D9A441 / 绿#6FA287

**字体规范**（ThoughtWorks 官方标准）：

- 标题：**Bitter Bold**（只能用粗体）
- 副标题：**Inter SemiBold**（只能用半粗体）
- 正文：**Inter Regular**（只能用常规体）
- 强调：**Inter Bold**
- ⚠️ 禁止使用细体、轻量体、中等体、超粗体、黑体

**文本规范**（ThoughtWorks 写作指南）：

- 句首大写格式（Sentence case）
- 公司名：Thoughtworks（T 大写，w 小写）
- 标题末尾无句号
- 数字：个位拼写（two），两位数用数字（10, 34）
- 日期：June 20, 2025

**页面类型**：

- 封面：深色背景，大标题
- 章节：深色背景，章节名
- 内容：白色背景，左文右图
- 图表：白色背景，几何图形

**设计特点**：

- 扁平化、无渐变
- 几何图形（菱形、圆形、六边形）
- 左下角固定 Logo
- 专业、现代、品牌感强

#### 命令行参数

```bash
选项:
  -c, --content <file>    内容文件路径（必需）
  -n, --name <name>       PPT名称（默认：自动提取）
  --chinese               中文PPT（默认）
  --english               英文PPT
  -s, --style <preset>    样式预设（默认：thoughtworks）
  -o, --output <dir>      输出目录（默认：ppt/）
```

---

## 🔐 账号管理

### 首次登录

首次使用时会自动处理：

1. 打开 Chrome 浏览器（只 1 个窗口）
2. 跳转到 gemini.google.com
3. 等待你登录（最多 5 分钟）
4. 登录成功，浏览器自动关闭
5. 开始生成图片

### 换号/重新登录

**通过 AI 命令**（推荐）：

直接告诉 AI：

```
"我想换个账号"
"重新登录"
"切换账号"
```

AI 会自动清除登录状态，下次使用时重新登录。

**手动执行**：

```bash
# 清除登录
bun scripts/logout.ts

# 检查状态
bun scripts/logout.ts --check
```

### 登录优化

- ✅ 只弹出 1 个浏览器窗口
- ✅ 5 分钟超时，支持 2FA 验证
- ✅ 登录状态自动保存
- ✅ 过期自动重新登录

---

## 📂 目录结构

### 脚本目录

```
scripts/
├── generate-prompt.ts     # 生成提示词
├── generate-image.ts      # 生成图片
├── generate-ppt.ts        # 生成PPT
├── logout.ts              # 登出/换号
├── detect-scene.ts        # 场景检测
├── detect-input.ts        # 输入类型检测
└── lib/
    └── gemini-client.ts   # Gemini客户端
```

### 参考资源

```
references/
├── scene-types/           # 场景定义
│   ├── cover.md
│   ├── flowchart.md
│   ├── poster.md
│   ├── mindmap.md
│   └── note.md
└── styles/                # 样式定义
    ├── obsidian.md
    ├── notion.md
    ├── minimal.md
    ├── chalkboard.md
    └── thoughtworks.md
```

### 示例文件

```
examples/
└── ppt-content-example.md   # PPT内容示例
```

---

## 💡 使用技巧

### 技巧 1：组织内容

**单图**：

- 提取核心信息
- 简短标题和关键词
- 适合视觉化的内容

**PPT**：

```markdown
# 使用一级标题作为 PPT 主标题

## 二级标题会成为章节引导页

### 三级标题和内容会成为内容页

- 每页 3-5 个要点最佳
- 保持简洁清晰
```

### 技巧 2：选择样式

**单图场景**：

- 笔记、知识管理 → obsidian
- 产品文档、专业内容 → notion
- 简洁设计 → minimal

**PPT 场景**：

- 企业级、咨询类 → thoughtworks（默认）
- 商务汇报 → professional
- 产品发布 → modern
- 学术演讲 → minimal

### 技巧 3：中文支持

**自动检测**：

- 系统自动检测内容语言
- 中文内容自动添加中文标记
- 无需手动设置

**PPT 中文**：

```bash
# 默认就是中文
bun scripts/generate-ppt.ts -c content.md

# 或明确指定
bun scripts/generate-ppt.ts -c content.md --chinese
```

### 技巧 4：修改重生成

**单图**：

```bash
# 1. 编辑提示词
vim smart-image-generator-output/prompts/cover-*.md

# 2. 重新生成
bun scripts/generate-image.ts --prompt 提示词路径
```

**PPT 单页**：

```bash
# 1. 编辑某页提示词
vim ppt/my-ppt/prompts/page-05.md

# 2. 重新生成该页
bun scripts/generate-image.ts \
  -p ppt/my-ppt/prompts/page-05.md \
  -o ppt/my-ppt/images/page-05.png
```

---

## ❓ 常见问题

### Q: 首次使用需要做什么？

**A**: 什么都不需要！

- ✅ 第一次生成时会自动打开浏览器
- ✅ 在浏览器中登录 Google 账号即可
- ✅ 登录后所有数据自动保存

### Q: 支持哪些语言？

**A**: 完美支持中文和英文

- ✅ 自动检测内容语言
- ✅ 中文内容生成中文图片
- ✅ 英文内容生成英文图片
- ✅ PPT 支持 `--chinese` / `--english` 指定

### Q: PPT 生成需要多久？

**A**: 取决于页数

- 10 页 PPT 约 5-10 分钟
- 每页约 30-60 秒
- 首次需要登录时间

### Q: 如何换账号？

**A**: 两种方式

1. **通过 AI**：直接说"我想换个账号"
2. **手动**：`bun scripts/logout.ts`

### Q: 生成的图片在哪里？

**A**: 根据输入方式不同

- **从文件生成**：输入文件同目录的`smart-image-generator-output/images/`
- **直接内容**：项目根目录的`smart-image-generator-output/images/`
- **PPT**：`ppt/{ppt-name}/images/`

### Q: 可以修改提示词吗？

**A**: 可以！

1. 找到生成的提示词文件（`.md`）
2. 编辑内容
3. 重新运行 `generate-image.ts`

### Q: ThoughtWorks 样式是什么样的？

**A**: 企业级专业样式

- 配色：深青#003B4D + 粉红#FF6B9D
- 布局：深色封面 + 白色内容页
- 图形：扁平化几何图形
- 特点：专业、现代、品牌感强

详细说明见 `references/styles/thoughtworks.md`

---

## 📚 详细文档

### 核心文档

- `SKILL.md` - AI 执行流程和技能定义
- `README.md` - 本文档（用户手册）

### 参考资源

- `references/scene-types/*.md` - 场景类型定义
- `references/styles/*.md` - 样式风格定义
- `examples/*.md` - 使用示例

---

## 🔧 命令速查

### 单图生成

```bash
# 生成提示词
bun scripts/generate-prompt.ts \
  --scene <类型> \
  --style <风格> \
  --content "内容"

# 生成图片
bun scripts/generate-image.ts \
  --prompt 提示词路径
```

### PPT 生成

```bash
# 基础用法
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

# 检查状态
bun scripts/logout.ts --check
```

---

## 🎯 使用示例

### 示例 1：为文章生成封面

```bash
# 假设文章在 docs/my-article.md

# 生成提示词
bun scripts/generate-prompt.ts \
  --scene cover \
  --file docs/my-article.md

# 生成图片
bun scripts/generate-image.ts \
  --prompt docs/smart-image-generator-output/prompts/cover-*.md

# 结果：docs/smart-image-generator-output/images/cover-*.png
```

### 示例 2：生成流程图

```bash
# 生成提示词
bun scripts/generate-prompt.ts \
  --scene flowchart \
  --content "用户输入 → 场景识别 → 生成提示词 → 生成图片"

# 生成图片
bun scripts/generate-image.ts \
  --prompt smart-image-generator-output/prompts/flowchart-*.md
```

### 示例 3：生成 PPT

```bash
# 准备内容（见 examples/ppt-content-example.md）
cat > presentation.md << 'EOF'
# 产品发布会

## 产品简介
- 创新设计
- 强大功能

## 核心功能
- 功能1
- 功能2
EOF

# 生成PPT
bun scripts/generate-ppt.ts -c presentation.md

# 查看结果
ls ppt/产品发布会/images/
```

---

## 🎨 ThoughtWorks 样式指南

### 配色方案

**品牌主色**：

```
深青色 #003B4D ████  专业、稳重
粉红色 #FF6B9D ████  活力、创新
```

**辅助色**：

```
青色   #65B4C4 ████  清新、科技
橙色   #D9A441 ████  温暖、创新
绿色   #6FA287 ████  平衡、成长
紫色   #8B7BA8 ████  高级、创意
```

### 页面模板

**封面页**（深色）：

- 背景：深青色全屏
- 标题：白色大字，居中
- 副标题：粉色
- Logo：左下角

**章节页**（深色）：

- 背景：深青色全屏
- 标题：白色超大字，左对齐
- 编号：粉色

**内容页**（白色）：

- 背景：白色
- 标题：黑色，顶部
- 布局：左文（40%）右图（60%）
- 底部色带：4 色装饰

**图表页**（白色）：

- 背景：白色
- 布局：左文（30%）右图（70%）
- 图形：菱形、圆形、六边形
- 配色：品牌色组合

---

## 🔧 高级用法

### 批量生成

```bash
# 为多个文章批量生成封面
for file in docs/*.md; do
  bun scripts/generate-prompt.ts --scene cover --file "$file"
  # 然后批量生成图片
done
```

### 自定义输出位置

```bash
# 指定输出目录
bun scripts/generate-prompt.ts \
  --scene cover \
  --content "内容" \
  --output /custom/path/prompt.md
```

### 修改 PPT 单页

```bash
# 1. 编辑提示词
vim ppt/my-ppt/prompts/page-03.md

# 2. 重新生成该页
bun scripts/generate-image.ts \
  -p ppt/my-ppt/prompts/page-03.md \
  -o ppt/my-ppt/images/page-03.png
```

---

## 🐛 故障排除

### 登录问题

**浏览器未打开**：

- 检查 Chrome 是否已安装
- 路径：`/Applications/Google Chrome.app` (macOS)

**登录超时**：

- 5 分钟内完成登录（支持 2FA）
- 如超时，重新运行命令即可

**多个浏览器窗口**：

- 已修复，只会弹出 1 个窗口
- 如仍出现，请更新到最新版本

### 生成问题

**中文乱码**：

- 已修复，使用 UTF-8 编码
- 确保内容文件是 UTF-8 编码
- PPT 使用 `--chinese` 参数

**图片不清晰**：

- Gemini 生成的图片是高分辨率
- 如需更高质量，可以修改提示词添加"高清、细节丰富"等描述

**PPT 页面过多**：

- 建议控制在 10-20 页
- 超过 30 页考虑拆分为多个 PPT

### 环境问题

**Bun 未找到**：

```bash
# 安装Bun
curl -fsSL https://bun.sh/install | bash

# 验证
bun --version
```

**依赖安装失败**：

```bash
# 清除并重新安装
rm -rf node_modules bun.lock
bun install
```

---

## 🤝 与其他技能集成

### tech-article-writer 集成

本技能可与`tech-article-writer`技能配合使用：

- tech-article-writer 生成文章
- smart-image-generator 生成文章封面
- 自动插入图片引用到文章

AI 会自动处理集成，无需手动操作。

---

## 📝 技术说明

### 技术栈

- **运行时**：Bun
- **语言**：TypeScript
- **浏览器自动化**：Chrome DevTools Protocol
- **图片生成**：Gemini Web API

### 工作原理

```
用户输入 → 内容分析 → 场景识别 → 提示词生成 → Gemini API → 图片下载 → 保存
```

### 中文支持实现

- ✅ UTF-8 编码传输
- ✅ 自动语言检测
- ✅ 中文标记添加
- ✅ 专业图片模型支持

---

## 📄 许可证

MIT License

---

**版本**: v2.4.0  
**更新**: 2025-01-30  
**状态**: ✅ 稳定可用
