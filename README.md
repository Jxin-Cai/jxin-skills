<div align="center">

# Jxin Skills

**Claude Code 技能插件集 — 开发工具 + 创作工具，一键安装即用。**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-D97757.svg)](https://github.com/anthropics/claude-code)

[English](./README_en.md)&ensp;|&ensp;[License](./LICENSE)

</div>

<br/>

Jxin Skills 是一组为 [Claude Code](https://github.com/anthropics/claude-code) 打造的技能插件，按用途分为两个可独立安装的插件包：

- **jxin-coding** — 开发工具集：Git 提交审查、代码评审、代码行数统计
- **jxin-writing** — 创作工具集：技术文章写作、PPT 分镜、图片生成、简历优化、Markdown 发布

所有技能通过 `/slash-command` 调用，无需手动配置，开箱即用。

<br/>

## 目录

- [安装](#安装)
- [技能一览](#技能一览)
  - [Coding（开发工具）](#coding开发工具)
  - [Writing（创作工具）](#writing创作工具)
- [使用方式](#使用方式)
- [项目结构](#项目结构)
- [Contributing](#contributing)
- [License](#license)

<br/>

## 安装

### 方式一：通过插件市场

```bash
# 1. 添加插件市场
/plugin marketplace add https://github.com/Jxin-Cai/jxin-skills

# 2. 从市场中选择安装
#    - jxin-coding（开发工具集）
#    - jxin-writing（创作工具集）
```

### 方式二：通过 URL 直接安装

```bash
/install-skill https://github.com/Jxin-Cai/jxin-skills
```

安装后可选择安装 coding、writing 或两者都装。

<br/>

## 技能一览

### Coding（开发工具）

| 技能 | 命令 | 说明 |
|------|------|------|
| git-auto-commit-review | `/jxin-coding:commit` | Git 提交助手 — 支持快速提交（生成规范 commit message）和 CR 提交（深度代码审查 + 审查报告 + 提交） |
| claude-code-critic | `/jxin-coding:critic` | 严苛代码评审 — 以资深工程师视角审查项目或 Skill，输出分级评审报告（Critical / Major / Minor） |
| code-loc-counter | `/jxin-coding:loc` | 代码行数统计 — 扫描任意语言项目，排除测试和注释，输出按语言明细 |

### Writing（创作工具）

| 技能 | 命令 | 说明 |
|------|------|------|
| tech-article-writer | `/jxin-writing:article` | 技术文章创作 — 黄金五段式结构，支持科普、问题解决、经验总结、趋势分析四种类型 |
| ppt-storyboard | `/jxin-writing:ppt` | PPT 叙事分镜 — 三幕式叙事弧线，根据受众适配内容密度，可选 GPT/Gemini 生成分镜图 |
| gpt-image-gen | `/jxin-writing:image` | GPT 图片生成 — 通过 gpt-image-2 生成图片，支持 Images API 和 Responses API |
| gemini-image-gen | `/jxin-writing:image` | Gemini 图片生成 — 通过 Gemini Web API 生成图片，支持中文提示词 |
| markdown-publisher | `/jxin-writing:publish` | Markdown 转富文本 — 支持主题样式、Mermaid 渲染、图片 base64 内联，适合微信公众号等平台 |
| resume-craft | `/jxin-writing:resume` | 简历优化与 PDF 生成 — 基于"7 秒初筛"原则重构简历，支持科技感 PDF 和密码保护 |

<br/>

## 使用方式

技能有两种调用方式，效果相同：

**插件命令（短名）：**

```bash
/jxin-coding:commit           # 提交代码
/jxin-coding:critic           # 严苛评审
/jxin-coding:loc              # 统计代码行数

/jxin-writing:article         # 写技术文章
/jxin-writing:ppt             # PPT 分镜设计
/jxin-writing:image           # 生成图片（GPT 或 Gemini）
/jxin-writing:publish         # Markdown 转富文本
/jxin-writing:resume          # 优化简历
```

**直接技能命令（全名）：**

```bash
/jxin-coding:git-auto-commit-review
/jxin-coding:claude-code-critic
/jxin-coding:code-loc-counter

/jxin-writing:tech-article-writer
/jxin-writing:ppt-storyboard
/jxin-writing:gpt-image-gen
/jxin-writing:gemini-image-gen
/jxin-writing:markdown-publisher
/jxin-writing:resume-craft
```

<br/>

## 项目结构

```
jxin-skills/
├── .claude-plugin/
│   └── marketplace.json          # 插件市场入口
├── coding/                        # 开发工具插件
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/                  # slash command 快捷入口
│   └── skills/                    # 技能源码
│       ├── git-auto-commit-review/
│       ├── claude-code-critic/
│       └── code-loc-counter/
└── writing/                       # 创作工具插件
    ├── .claude-plugin/
    │   └── plugin.json
    ├── commands/                  # slash command 快捷入口
    └── skills/                    # 技能源码
        ├── tech-article-writer/
        ├── ppt-storyboard/
        ├── gpt-image-gen/
        ├── gemini-image-gen/
        ├── markdown-publisher/
        └── resume-craft/
```

<br/>

## Contributing

欢迎提交 Bug 报告、功能建议和 Pull Request。

如果计划贡献较大的改动，请先开 Issue 讨论方向和范围。

<br/>

## License

Licensed under the [Apache License 2.0](./LICENSE).

Copyright 2025 jxin
