# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Jxin 的 Claude Code 技能集合，按用途分为两个可安装插件：

- **jxin-coding**（`coding/`）：开发工具集 — Git 提交审查、分支守卫、worktree 管理、代码评审、通知 hook
- **jxin-writing**（`writing/`）：创作工具集 — 技术文章写作、PPT 叙事分镜、图片生成、简历优化、Markdown 发布

## 插件加载

Claude Code 通过 `.claude-plugin/marketplace.json` 发现两个可安装插件（coding / writing），通过各自 `.claude-plugin/plugin.json` 加载。技能源码直接放在对应插件的 `skills/` 目录下。

## 目录结构

```
jxin-skills/
├── .claude-plugin/
│   └── marketplace.json          # 插件市场入口，注册 coding 和 writing 两个插件
├── coding/                        # 开发工具插件
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/                  # slash command 快捷入口
│   │   ├── commit.md              # /jxin-coding:commit → git-auto-commit-review
│   │   └── critic.md              # /jxin-coding:critic → claude-code-critic
│   └── skills/
│       ├── git-auto-commit-review/
│       └── claude-code-critic/
└── writing/                       # 创作工具插件
    ├── .claude-plugin/
    │   └── plugin.json
    ├── commands/                  # slash command 快捷入口
    │   ├── article.md             # /jxin-writing:article → tech-article-writer
    │   ├── ppt.md                 # /jxin-writing:ppt → ppt-storyboard
    │   ├── image.md               # /jxin-writing:image → gemini-image-gen
    │   ├── publish.md             # /jxin-writing:publish → markdown-publisher
    │   └── resume.md              # /jxin-writing:resume → resume-craft
    └── skills/
        ├── tech-article-writer/
        ├── ppt-storyboard/
        ├── gemini-image-gen/
        ├── markdown-publisher/
        └── resume-craft/
```

## 技能分类

### Coding（开发工具）

| 技能 | 用途 | 命令快捷方式 |
|------|------|-------------|
| `git-auto-commit-review` | Git 提交助手，支持快速提交和深度 CR 提交 | `/jxin-coding:commit` |
| `claude-code-critic` | 项目/Skill 严苛评审 | `/jxin-coding:critic` |

### Writing（创作工具）

| 技能 | 用途 | 命令快捷方式 |
|------|------|-------------|
| `tech-article-writer` | 技术文章创作，黄金五段式 | `/jxin-writing:article` |
| `ppt-storyboard` | PPT 叙事分镜设计，三幕式结构 | `/jxin-writing:ppt` |
| `gemini-image-gen` | Gemini 图片生成底层能力 | `/jxin-writing:image` |
| `markdown-publisher` | Markdown 转富文本 HTML（微信公众号等） | `/jxin-writing:publish` |
| `resume-craft` | 简历优化与 PDF 生成 | `/jxin-writing:resume` |

## 约束

- 技能源码直接放在对应插件的 `skills/` 目录下，不使用符号链接
- 新增技能放到对应分类插件的 `skills/` 目录中
- 技能仅通过用户显式 `/slash-command` 触发
