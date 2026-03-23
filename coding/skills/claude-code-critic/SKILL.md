---
name: claude-code-critic
description: 严苛评审——站在 Claude Code 最佳实践角度评审项目或 Skill。当用户说"评审"、"审查"、"review"、"看看有什么问题"、"code audit"、"质量检查"时触发。任务型技能，仅在用户明确要求时触发。
disable-model-invocation: true
---

# Claude Code Critic

严苛评审项目或 Skill。追问本质，不放水，每条批评有理有据。

## 流程

### Step 1: 确定目标

从对话上下文提取评审目标路径和类型（项目 or Skill）。只有在路径完全无法推断时才询问用户。默认全面评审。

### Step 2: 扫描

先理解，再评判。完整扫描后再形成判断。

**项目**：结构 → CLAUDE.md / .claude/ 配置 → 核心代码 → 测试 → 安全 → 依赖

**Skill**：SKILL.md 全文 → 目录结构 → references/ → scripts/

大型项目（>100 文件）用 Agent 子代理并行扫描不同模块。

### Step 3: 评审

读取 `references/review-rules.md`，按目标类型选择适用规则。

重点找真正影响质量的问题，3 条 Critical 胜过 30 条 Minor。多个发现指向同一根因时合并为一条。

### Step 4: 出报告

```
# 评审报告：[名称]

**总评**：1-2 句。

## Critical
### C1: [标题]
`文件:行号` — 问题 / 原因 / 建议

## Major
### M1: [标题]
同上格式

## Minor
### m1: [标题]
同上格式

## 亮点
- ...
```

报告要简洁。每条发现：位置 + 一句话问题 + 一句话原因 + 具体建议。不要废话。

### Step 5: 交付

输出报告后询问用户：展开讨论、直接修复、还是有异议。
