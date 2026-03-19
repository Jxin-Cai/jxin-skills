---
name: git-auto-commit-review
description: Automate pre-commit code review for a git repository — snapshot diffs, produce a timestamped CodeReview report, propose improvements, and generate a conventional commit message in the format `<type>(<scope>): <subject>`. Use this skill whenever the user wants to commit code, review changes before committing, do a code review, or mentions things like "提交代码", "commit", "review一下", "检查改动", "代码审查", "帮我看看代码", "准备提交", or any git commit workflow. Also trigger when the user asks to generate a commit message or review a diff.
---

# Git Auto Commit Review

## Why this workflow exists

Committing without review leads to subtle bugs and technical debt. This skill forces a structured pause: snapshot the diff, review against proven rules, get programmer sign-off, then commit with a clean message. The report file creates an audit trail that helps the team learn from past reviews.

## Reviewer persona

Act as a senior engineer skilled in code review, focusing on: maintainability, robustness, performance, concurrency/thread safety, API design, testability, and edge cases. The review must incorporate `references/review-rules.md` (read it during Step 1) and add: risk assessment, potential regression points, and actionable fix suggestions with rationale.

The review-rules.md is a large file (480+ lines) organized by category. Use its table of contents to jump to relevant sections based on the diff content — no need to apply every rule to every review.

## Workflow

### Step 0: Snapshot current changes

Run the bundled script to capture the current state:

```bash
python3 ".claude/skills/git-auto-commit-review/scripts/create_review_bundle.py"
```

This creates files under `code_review_reports/` with naming pattern `YYYYMMDDHHMMSS_<git_username>`:
- `.md` — report template (fill this in during review)
- `.diff.patch` / `.diff_staged.patch` — unstaged and staged diffs
- `.status.txt` / `.log.txt` / `.meta.json` — context snapshots

If both diffs are empty, tell the user there's nothing to review and stop.

Do not include `code_review_reports/` in commits (recommend adding to `.gitignore`).

### Step 1: Review the diff (no code edits)

1. Read the `.diff.patch` and `.diff_staged.patch` files
2. Read `references/review-rules.md` and apply relevant rules based on the diff content
3. **Edit the `.md` report file**（用文件编辑工具写入，不要只在对话中输出），填写以下章节:
   - **变更概览**: What changed (high level) and risk assessment
   - **Must-fix before commit**: 必须修复才能提交的问题
   - **Nice-to-have**: 建议改进但不阻塞提交
   - **建议明细**: Actionable suggestions with file paths and rationale (explain *why* each matters)

### Step 2: Programmer decision gate

Present findings to the user and wait for explicit acceptance. The programmer decides — never modify code without approval.

After the programmer responds, **edit the `.md` report file** 的 "Programmer Decision" 章节，记录：
- Accept all / accept some / accept none
- List accepted suggestions explicitly

### Step 3: Apply accepted suggestions

After explicit acceptance:

1. Implement the accepted changes
2. Update the existing bundle (don't create a new one):
   ```bash
   python3 ".claude/skills/git-auto-commit-review/scripts/create_review_bundle.py" --update-latest
   ```
   Or specify a report ID: `--base-name "<报告编号>"`
3. Update the same report markdown — fill "Applied Changes" and adjust conclusions
4. Verify the working tree state (staged vs unstaged)

### Step 4: Generate commit message

Format: `<type>(<scope>): <subject>` (scope optional)

Allowed types: `feat` | `fix` | `to` | `docs` | `style` | `refactor` | `perf` | `test` | `chore` | `revert` | `merge` | `sync`

- `fix` = this commit contains the actual bug fix
- `to` = tracking a bug for later; the fix comes in a subsequent `fix` commit

Subject: Chinese preferred, <=50 chars, no trailing punctuation.

Examples: `fix(DAO):用户查询缺少username属性` · `feat(Controller):用户查询接口开发`

### Step 5: Commit

1. Confirm what is staged (`git diff --staged`)
2. Commit with single-line subject (no body unless requested)
3. Never change git config. Never push unless explicitly asked.

## Maintaining review rules

Append new rules to `references/review-rules.md` using the format documented there (Rule + Why + Bad/Good examples). This keeps the rule set growing with the team's experience.
