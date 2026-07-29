<div align="center">

# Jxin Skills

**Skill plugins for Claude Code — dev tools + creative tools, install and use instantly.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-D97757.svg)](https://github.com/anthropics/claude-code)

[中文文档](./README.md)&ensp;|&ensp;[License](./LICENSE)

</div>

<br/>

Jxin Skills is a collection of skill plugins built for [Claude Code](https://github.com/anthropics/claude-code), split into two independently installable packages:

- **jxin-coding** — Dev toolkit: Git commit review, code review, LOC counter
- **jxin-writing** — Creative toolkit: tech article writing, PPT storyboard, image generation, resume optimization, Markdown publishing

All skills are invoked via `/slash-command` — no manual configuration needed.

<br/>

## Table of Contents

- [Installation](#installation)
- [Skills](#skills)
  - [Coding (Dev Tools)](#coding-dev-tools)
  - [Writing (Creative Tools)](#writing-creative-tools)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

<br/>

## Installation

### Option 1: Via Plugin Marketplace

```bash
# 1. Add the plugin marketplace
/plugin marketplace add https://github.com/Jxin-Cai/jxin-skills

# 2. Install from the marketplace
#    - jxin-coding (dev toolkit)
#    - jxin-writing (creative toolkit)
```

### Option 2: Direct URL Install

```bash
/install-skill https://github.com/Jxin-Cai/jxin-skills
```

After installation, choose to install coding, writing, or both.

<br/>

## Skills

### Coding (Dev Tools)

| Skill | Command | Description |
|-------|---------|-------------|
| git-auto-commit-review | `/jxin-coding:commit` | Git commit assistant — quick commit (generate conventional message) or CR commit (deep code review + report + commit) |
| claude-code-critic | `/jxin-coding:critic` | Strict code review — senior engineer perspective, outputs graded report (Critical / Major / Minor) |
| code-loc-counter | `/jxin-coding:loc` | LOC counter — scan any language project, exclude tests and comments, output per-language breakdown |

### Writing (Creative Tools)

| Skill | Command | Description |
|-------|---------|-------------|
| tech-article-writer | `/jxin-writing:article` | Tech article writing — golden five-paragraph structure, supports tutorial, problem-solving, experience summary, and trend analysis |
| ppt-storyboard | `/jxin-writing:ppt` | PPT storyboard — three-act narrative arc, audience-adapted density, optional GPT/Gemini storyboard images |
| gpt-image-gen | `/jxin-writing:image` | GPT image generation — via gpt-image-2, supports Images API and Responses API |
| gemini-image-gen | `/jxin-writing:image` | Gemini image generation — via Gemini Web API, supports Chinese prompts |
| markdown-publisher | `/jxin-writing:publish` | Markdown to rich HTML — theme styling, Mermaid rendering, base64 image inlining for WeChat and similar platforms |
| resume-craft | `/jxin-writing:resume` | Resume optimization & PDF — restructure based on "7-second screening" principle, tech-style PDF with password protection |

<br/>

## Usage

Skills can be invoked in two equivalent ways:

**Plugin commands (short name):**

```bash
/jxin-coding:commit           # Commit code
/jxin-coding:critic           # Code review
/jxin-coding:loc              # Count lines of code

/jxin-writing:article         # Write a tech article
/jxin-writing:ppt             # PPT storyboard design
/jxin-writing:image           # Generate image (GPT or Gemini)
/jxin-writing:publish         # Markdown to rich text
/jxin-writing:resume          # Optimize resume
```

**Direct skill commands (full name):**

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

## Project Structure

```
jxin-skills/
├── .claude-plugin/
│   └── marketplace.json          # Plugin marketplace entry
├── coding/                        # Dev tools plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/                  # Slash command shortcuts
│   └── skills/                    # Skill source code
│       ├── git-auto-commit-review/
│       ├── claude-code-critic/
│       └── code-loc-counter/
└── writing/                       # Creative tools plugin
    ├── .claude-plugin/
    │   └── plugin.json
    ├── commands/                  # Slash command shortcuts
    └── skills/                    # Skill source code
        ├── tech-article-writer/
        ├── ppt-storyboard/
        ├── gpt-image-gen/
        ├── gemini-image-gen/
        ├── markdown-publisher/
        └── resume-craft/
```

<br/>

## Contributing

Bug reports, feature requests, and pull requests are welcome.

For significant changes, please open an issue first to discuss direction and scope.

<br/>

## License

Licensed under the [Apache License 2.0](./LICENSE).

Copyright 2025 jxin
