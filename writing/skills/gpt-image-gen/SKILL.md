---
name: gpt-image-gen
description: 基于 GPT Responses 协议的图片生成技能。传入图片提示词和样式要求，通过项目级 host/key 调用 gpt-image-2 生成图片。当用户需要使用 GPT 生成插图、封面、海报、PPT 分镜图片时使用此技能；也适用于其他技能（如 ppt-storyboard）内部调用。
---

# GPT 图片生成器

通过 Responses API 调用 `gpt-image-2` 生成图片。设计为既可被用户直接调用，也可被其他技能（如 PPT 叙事分镜技能）程序化调用。

## 核心能力

- 接收提示词 + 样式要求，调用 GPT 图片模型生成 PNG
- 首次使用时保存项目级 host/key 配置
- 后续同一项目自动复用配置
- 支持指定输出路径，默认写入当前会话根目录的 `image_output/`
- 不向日志输出完整 key

## 执行流程

### Step 1: 检查项目配置

配置保存于**调用该技能的项目/会话根目录**下：

```text
.gpt-image-gen/
├── config.json        # host、模型、默认尺寸等非敏感配置
├── credentials.json   # API key
└── .gitignore         # 忽略本目录内所有内容
```

先检查配置：

```bash
cd <gpt-image-gen 技能目录>
bun scripts/config.ts --check --workspace <项目根目录绝对路径>
```

如果配置存在且可读取，继续生成图片。

如果配置不存在，必须引导用户提供：

1. **host**：Responses API 服务地址，例如 `https://example.com` 或 `https://example.com/v1`
2. **key**：API key

拿到 host/key 后，先验证再保存：

```bash
bun scripts/config.ts \
  --set \
  --workspace <项目根目录绝对路径> \
  --host <host> \
  --key <key> \
  --image-model gpt-image-2
```

验证失败时不要保存配置，向用户报告脱敏后的错误原因。

### Step 2: 明确生成意图

需要两个关键输入：

1. **图片提示词**（必需）：描述要生成什么图片的详细文本
2. **样式要求**（可选）：视觉风格、配色、布局等要求

如果用户没给提示词而是给了一段内容或文件，先把内容转化为适合图片生成的提示词。转化时：

- 提取核心主题和关键视觉元素
- 用英文描述视觉构图，中文只出现在标题/具体内容引用中
- 指定比例（默认 16:9）
- 结合用户指定的样式要求

如果用户只给了很短的模糊需求，先用 AskUserQuestion 补齐最影响结果的选项：

- **用途**：封面 / 插图 / 海报 / PPT 配图
- **画幅**：16:9 / 1:1 / 3:4 / 自定义
- **风格**：现代简约 / 商务科技 / 手绘插画 / 自定义

如果用户已经给出清晰提示词，不要为了形式强行追问。

如果用户既没有显式指定提示词文件保存目录，也没有显式指定图片输出目录，则默认使用**调用该技能的会话当前根目录**下的 `image_output/` 作为工作目录，并在其中创建：

- `prompts/`：保存生成或整理后的提示词文件
- `images/`：保存最终生成的图片

不要把提示词、图片或配置写到 `gpt-image-gen` 技能自身目录里；技能目录只用于读取脚本。

### Step 3: 构建完整提示词

将用户的图片描述和样式要求组合成一份完整提示词。如果是从其他技能调用（如 ppt-storyboard），提示词已经准备好，直接使用。

提示词保存为 `.md` 文件，路径由调用方指定；如果调用方未指定，则默认保存到当前会话根目录下 `image_output/prompts/`。图片默认保存到当前会话根目录下 `image_output/images/`。

直接用户调用时，提示词应组织成便于预览的结构：

```markdown
Generate an image based on the following description:

## Subject
...

## Composition
...

## Style
...

## Constraints
- Aspect ratio: 16:9
- No unwanted text unless explicitly requested
```

### Step 4: 展示预览并确认

**直接用户调用时**：生成前用简洁卡片展示本次生图计划，而不是只贴完整提示词。

展示格式：

```text
生图计划

渠道：GPT / gpt-image-2
用途：PPT 配图
画幅：16:9
风格：现代简约，暖橙主色
输出：image_output/images/<name>.png

提示词摘要：
- 主体：...
- 构图：...
- 风格：...
```

然后用 AskUserQuestion 提供操作：

1. **直接生成**：按当前提示词生成
2. **调整提示词**：用户补充修改要求后再生成
3. **只保存提示词**：保存 prompt，不调用接口

**被其他技能调用时（批量模式）**：跳过逐个确认，由调用方技能统一管理确认流程。

### Step 5: 生成图片

调用 GPT 生成图片：

```bash
cd <gpt-image-gen 技能目录>
bun scripts/generate-image.ts \
  --workspace <项目根目录绝对路径> \
  --prompt-file <提示词文件路径> \
  --output <输出图片路径>
```

**参数说明**：

- `--workspace`：项目/会话根目录，用于读取 `.gpt-image-gen` 配置
- `--prompt-file` / `-p`：提示词文件路径（必需）
- `--output` / `-o`：输出图片路径（可选，默认根据提示词文件位置推断）
- `--size`：图片尺寸（可选，默认 `1536x1024`，适合 16:9 PPT）
- `--quality`：图片质量（可选，默认 `auto`）
- `--format`：输出格式（可选，默认 `png`）

### Step 6: 频率控制

连续调用外部生图服务可能遇到限流。执行频率控制策略：

- **单次生成**：直接调用，无需等待
- **批量生成**（2张以上）：每张图片之间等待 5 秒 + 1-5 秒随机秒数
- **大批量生成**（5张以上）：每 5 张额外等待 30 秒
- 如果遇到 429、5xx 或网络错误，等待 60 秒后重试，最多重试 2 次

### Step 7: 返回结果

生成完成后用清晰的结果卡片返回，不只给路径：

```text
图片生成完成

文件：image_output/images/<name>.png
提示词：image_output/prompts/<name>.md
渠道：GPT / gpt-image-2
尺寸：1536x1024

你可以继续：
- 调整提示词重新生成
- 换成 Gemini 渠道再试一版
- 直接使用这张图
```

如果生成失败，返回：

- 失败阶段：配置检查 / 接口请求 / 结果解析 / 文件写入
- 脱敏后的错误摘要
- 建议下一步：重新配置 host/key、换尺寸/提示词、稍后重试

不要输出完整 key、完整响应体或大段 base64。

## 账号管理

重新配置 host/key：

```bash
cd <gpt-image-gen 技能目录>
bun scripts/config.ts --clear --workspace <项目根目录绝对路径>
bun scripts/config.ts --set --workspace <项目根目录绝对路径> --host <host> --key <key>
```

检查配置：

```bash
bun scripts/config.ts --check --workspace <项目根目录绝对路径>
```

## 技术细节

- 运行环境：需要 Bun 运行时
- 协议：Responses API
- 默认模型：`gpt-image-2`
- 输出格式：PNG
- 配置范围：项目级 `.gpt-image-gen/`
