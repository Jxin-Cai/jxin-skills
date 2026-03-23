# Jxin Skills

Jxin 的 Claude Code 技能集合，分为 **Coding（开发工具）** 和 **Writing（创作工具）** 两个插件。

## 安装

### 方式一：通过插件市场

1. 先将本仓库加载为插件市场：
   ```
   /plugin marketplace add https://github.com/Jxin-Cai/jxin-skills
   ```
2. 然后从市场中选择需要的插件安装：
   - **jxin-coding** — 开发工具集
   - **jxin-writing** — 创作工具集

### 方式二：通过 URL 直接安装

```
/install-skill https://github.com/Jxin-Cai/jxin-skills
```

安装后同样可以选择安装 coding、writing 或两者都装。

## Coding 技能一览

| 技能 | 触发命令 | 说明 |
|------|---------|------|
| git-auto-commit-review | `/git-auto-commit-review` | Git 提交助手。支持**快速提交**（生成规范 commit message）和**CR 提交**（深度代码审查 + 审查报告 + 提交）两种模式 |
| git-branch-guard | `/git-branch-guard` | Git 分支守卫。强制分支命名规范和 squash merge 策略 |
| worktree-manager | `/worktree-manager` | Git worktree 管理。并行开发多个功能分支 |
| claude-code-critic | `/claude-code-critic` | 严苛代码评审。以资深工程师视角审查项目或 Skill，输出分级评审报告（Critical / Major / Minor） |
| claude-notify-hook | `/claude-notify-hook` | macOS 系统通知。配置 Claude Code 任务完成后的桌面通知 |

## Writing 技能一览

| 技能 | 触发命令 | 说明 |
|------|---------|------|
| tech-article-writer | `/tech-article-writer` | 技术文章创作。黄金五段式结构，支持科普、问题解决、经验总结、趋势分析四种文章类型，自动生成封面提示词和摘要 |
| ppt-storyboard | `/ppt-storyboard` | PPT 叙事分镜。三幕式叙事弧线，根据受众（管理层/技术/投资方）适配内容密度，自动生成分镜图片并合成 PDF |
| gemini-image-gen | `/gemini-image-gen` | Gemini 图片生成。通过 Gemini Web API 生成图片，支持中文提示词，内置频率控制。也供其他技能内部调用 |
| smart-image-generator | `/smart-image-generator` | 智能图片生成（集成版） |
| markdown-publisher | `/markdown-publisher` | Markdown 转富文本 HTML。支持主题样式、Mermaid 图表渲染、本地图片 base64 内联，适合发布到微信公众号等平台 |
| resume-craft | `/resume-craft` | 简历优化与 PDF 生成。基于"面试官 7 秒初筛"原则重构简历结构，支持生成科技感 PDF，含密码保护和多主题 |

## 使用方式

所有技能通过 `/技能名` 触发，例如：

```
/git-auto-commit-review    # 提交代码
/tech-article-writer       # 写一篇技术文章
/ppt-storyboard            # 把文章做成 PPT
/resume-craft              # 优化简历
```

## 许可

MIT
