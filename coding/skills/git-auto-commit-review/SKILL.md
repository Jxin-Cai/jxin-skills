---
name: git-auto-commit-review
description: Git 提交助手——支持快速提交和深度 CR 提交两种模式。当用户要提交代码时触发，包括"commit"、"提交代码"、"提交"、"准备提交"、"提交前审查"、"cr 提交"等。注意：纯粹的代码审查（不涉及提交意图）不应触发此技能。
---

# Git 提交助手

支持快速提交和深度 CR 提交两种模式。简单改动走快速流程，关键变更走 CR 流程。

## 流程

### 第 0 步：获取变更

```bash
git diff && git diff --staged && git status --porcelain
```

如果无任何变更，告知用户并停止。

### 第 1 步：暂存检查

检查是否有未暂存的改动：
- 如果所有改动已暂存（staged），直接进入第 2 步
- 如果有未暂存的改动，向用户确认：暂存全部（`git add -A`）还是只暂存部分文件

### 第 2 步：询问提交模式

向用户展示变更概要（改了哪些文件、大致改了什么），然后询问：

- **快速提交**：仅生成规范 commit message 并提交，适合小改动
- **CR 提交**：深度代码审查 + 生成审查报告 + 提交，适合重要变更

---

## 快速提交流程

### 生成 commit message

格式：`<type>(<scope>): <subject>`（scope 可选）

允许的 type：`feat` | `fix` | `to` | `docs` | `style` | `refactor` | `perf` | `test` | `chore` | `revert` | `merge` | `sync`

- `fix` = 本次提交包含实际修复
- `to` = 团队扩展类型，标记待修复的 bug，后续用 `fix` 提交（非 Conventional Commits 标准）

subject 要求：中文优先，<=50 字，不加结尾标点。

示例：`fix(DAO):用户查询缺少username属性` · `feat(Controller):用户查询接口开发`

### 确认并提交

1. 向用户展示 commit message，等待确认
2. 确认暂存区内容（`git diff --staged`）
3. 提交。绝不修改 git config，绝不 push 除非用户明确要求

---

## CR 提交流程

### 第 1 步：生成审查快照

运行本技能 `scripts/` 目录下的脚本捕获当前状态：

```bash
python3 "<本技能目录>/scripts/create_review_bundle.py"
```

> 注：`<本技能目录>` 指本技能的实际安装路径，即包含此 SKILL.md 的目录。

在 `code_review_reports/` 下生成带时间戳的文件集（.md 报告模板、.diff.patch、.status.txt 等）。

### 第 2 步：审查 diff

以资深工程师视角审查，关注：可维护性、健壮性、性能、并发安全、API 设计、可测试性、边界情况。

1. 读取 `.diff.patch` 和 `.diff_staged.patch`
2. 根据项目技术栈选择审查规则（通用规则必读，语言规则按需加载）：
   - **通用规则**（所有项目必读）：`references/review-rules.md`
   - **Java 后端**（Spring/Dubbo/MyBatis）：`references/review-rules-java.md`
   - **前端**（Vue/React/TypeScript）：`references/review-rules-frontend.md`
   - **Python**（Django/Flask/FastAPI）：`references/review-rules-python.md`
   - **Go**：`references/review-rules-go.md`
   - 只读取与变更相关的章节，不必逐条检查
3. **编辑 `.md` 报告文件**（用文件编辑工具写入），填写：
   - **变更概览**：改了什么、影响范围、风险等级
   - **必须修复**：阻塞提交的问题
   - **建议改进**：不阻塞提交但值得优化
   - **建议明细**：每条建议附文件路径和理由

### 第 3 步：等待用户决策

展示审查结论，等待用户明确回复。审查阶段只输出建议，不主动修改代码。

用户回复后，编辑报告的"开发者决策"章节，记录采纳情况。

### 第 4 步：执行采纳的建议

用户明确采纳后，进入修改阶段：

1. 实施用户同意的修改
2. 更新快照：
   ```bash
   python3 "<本技能目录>/scripts/create_review_bundle.py" --update-latest
   ```
3. 更新报告中的"已执行变更"章节

### 第 5 步：生成 commit message 并提交

同快速提交流程的 commit message 规范。提交前确认暂存区内容。
