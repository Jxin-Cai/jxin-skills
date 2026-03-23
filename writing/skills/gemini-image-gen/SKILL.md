---
name: gemini-image-gen
description: 基于 Gemini 的图片生成技能。传入图片提示词和样式要求，调用 Gemini 生成图片。当用户需要 AI 生成图片、插图、封面、海报、流程图、思维导图时使用此技能。也适用于其他技能（如 ppt-storyboard）内部调用来批量生成图片。
---

# Gemini 图片生成器

通过 Gemini Web API 生成高质量图片的专用技能。设计为既可被用户直接调用，也可被其他技能（如叙事分镜技能）程序化调用。

## 核心能力

- 接收提示词 + 样式要求，调用 Gemini 生成图片
- 内置频率控制，防止 API 被风控
- 自动处理 Google 账号登录（首次使用弹浏览器，后续自动复用）
- 完美支持中文提示词

## 执行流程

### Step 1: 确认输入

需要两个关键输入：

1. **图片提示词**（必需）：描述要生成什么图片的详细文本
2. **样式要求**（可选）：视觉风格、配色、布局等要求

如果用户没给提示词而是给了一段内容或文件，先帮用户把内容转化为适合图片生成的提示词。转化时：
- 提取核心主题和关键视觉元素
- 用英文描述视觉构图（Visual 部分），中文只出现在标题/具体内容引用中
- 指定比例（默认 16:9）
- 结合用户指定的样式要求

### Step 2: 构建完整提示词

将用户的图片描述和样式要求组合成一份完整提示词。如果是从其他技能调用（如 ppt-storyboard），提示词已经准备好，直接使用。

提示词保存为 `.md` 文件，路径由调用方指定或默认保存到输出目录的 `prompts/` 子目录。

### Step 3: 展示提示词并确认

**直接用户调用时**：展示提示词预览，等用户确认或修改后再生成。

**被其他技能调用时（批量模式）**：跳过逐个确认，由调用方技能统一管理确认流程。

### Step 4: 生成图片

调用 Gemini 生成图片：

```bash
cd <gemini-image-gen 技能目录>
bun scripts/generate-image.ts \
  --prompt-file <提示词文件路径> \
  --output <输出图片路径>
```

**参数说明**：
- `--prompt-file` / `-p`：提示词文件路径（必需）
- `--output` / `-o`：输出图片路径（可选，默认根据提示词文件位置自动推断）

### Step 5: 频率控制（重要）

Gemini API 有频率限制，连续调用会被风控。执行频率控制策略：

- **单次生成**：直接调用，无需等待
- **批量生成**（2张以上）：每张图片之间**等待 15-20 秒**
- **大批量生成**（5张以上）：每 5 张额外等待 30 秒
- 如果遇到 429 或生成失败，**等待 60 秒**后重试，最多重试 2 次

频率控制的具体执行方式：在调用 `generate-image.ts` 之间插入等待。示例：

```bash
# 第1张
bun scripts/generate-image.ts -p prompts/page-01.md -o images/01.png

# 等待 15 秒
sleep 15

# 第2张
bun scripts/generate-image.ts -p prompts/page-02.md -o images/02.png
```

### Step 6: 返回结果

生成完成后返回：
- 图片文件路径
- 生成状态（成功/失败/重试次数）

## 首次使用：自动登录

首次使用时脚本会自动：
1. 打开 Chrome 浏览器（只1个窗口）
2. 跳转到 gemini.google.com
3. 等待用户登录 Google 账号（最多5分钟）
4. 登录成功后自动保存状态，浏览器关闭
5. 后续使用自动复用登录状态

登录数据存储：
- Cookies：`~/.local/share/smart-image-generator/cookies.txt`
- Profile：`~/.local/share/smart-image-generator/chrome-profile/`

## 账号管理

换号/重新登录：

```bash
cd <gemini-image-gen 技能目录>
bun scripts/logout.ts
```

检查登录状态：

```bash
bun scripts/logout.ts --check
```

## 样式参考

生成提示词时可参考以下预设样式（详见 `references/` 目录）：

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| `obsidian` | 手绘知识风格 | 笔记、知识管理 |
| `notion` | 现代SaaS风格 | 产品介绍、专业文档 |
| `minimal` | 极简主义 | 简洁设计 |
| `chalkboard` | 黑板风格 | 教学、演示 |
| `thoughtworks` | 企业咨询风格 | 企业级PPT、技术方案 |

## 技术细节

- 运行环境：需要 Bun 运行时
- 依赖：node-fetch, cheerio
- 图片来源：Gemini Web API（通过浏览器 Cookie 认证）
- 输出格式：PNG
- 支持中文：完整 UTF-8 编码支持
