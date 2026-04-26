---
description: 图片生成，可选择 GPT 或 Gemini 渠道
disable-model-invocation: true
argument-hint: "[图片提示词] [--gpt|--gemini]"
---

这是统一图片生成入口，请按用户指定或询问后选择图片生成渠道。

- 如果用户参数明确包含 `--gpt`、`gpt`、`GPT` 或“用 GPT”，请使用技能 `jxin-writing:gpt-image-gen` 处理本次请求。
- 如果用户参数明确包含 `--gemini`、`gemini`、`Gemini` 或“用 Gemini”，请使用技能 `jxin-writing:gemini-image-gen` 处理本次请求。
- 如果用户没有明确指定渠道，请用 AskUserQuestion 询问使用 GPT 还是 Gemini，然后调用对应技能。

用户参数：$ARGUMENTS
