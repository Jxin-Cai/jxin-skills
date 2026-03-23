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
│   └── skills/
│       ├── git-auto-commit-review/
│       ├── git-branch-guard/
│       ├── worktree-manager/
│       ├── claude-code-critic/
│       └── claude-notify-hook/
└── writing/                       # 创作工具插件
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/
        ├── tech-article-writer/
        ├── ppt-storyboard/
        ├── gemini-image-gen/
        ├── smart-image-generator/
        ├── markdown-publisher/
        └── resume-craft/
```

## 技能分类

### Coding（开发工具）

| 技能 | 用途 |
|------|------|
| `git-auto-commit-review` | Git 提交助手，支持快速提交和深度 CR 提交 |
| `git-branch-guard` | Git 分支管理钩子，强制分支命名和 squash merge |
| `worktree-manager` | Git worktree 管理，并行开发多功能 |
| `claude-code-critic` | 项目/Skill 严苛评审 |
| `claude-notify-hook` | macOS 系统通知配置 |

### Writing（创作工具）

| 技能 | 用途 |
|------|------|
| `tech-article-writer` | 技术文章创作，黄金五段式 |
| `ppt-storyboard` | PPT 叙事分镜设计，三幕式结构 |
| `gemini-image-gen` | Gemini 图片生成底层能力 |
| `smart-image-generator` | 智能图片/PPT 生成（集成版） |
| `markdown-publisher` | Markdown 转富文本 HTML（微信公众号等） |
| `resume-craft` | 简历优化与 PDF 生成 |

## 约束

- 技能源码直接放在对应插件的 `skills/` 目录下，不使用符号链接
- 新增技能放到对应分类插件的 `skills/` 目录中
- 技能仅通过用户显式 `/slash-command` 触发
