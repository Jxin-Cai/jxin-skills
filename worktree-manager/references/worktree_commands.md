# Git Worktree 命令完整参考

本文档提供 Git worktree 所有命令的详细说明和示例。

## 核心命令

### git worktree add

创建新的 worktree 并检出分支

**语法:**
```bash
git worktree add [-f] [--detach] [--checkout] [--lock] [-b <new-branch>] <path> [<commit-ish>]
```

**常用示例:**

```bash
# 创建并检出新分支
git worktree add ../feature-login -b feature/login

# 基于现有分支创建
git worktree add ../hotfix main

# 基于远程分支创建
git worktree add ../feature-payment -b feature/payment origin/develop

# 创建临时 worktree(不创建分支)
git worktree add --detach ../temp HEAD~1
```

**选项说明:**
- `-b <new-branch>`: 创建新分支
- `-B <new-branch>`: 创建新分支,如果已存在则重置
- `--detach`: 创建分离 HEAD 的 worktree
- `-f, --force`: 强制创建,即使路径已存在
- `--lock`: 创建后立即锁定 worktree

### git worktree list

列出所有 worktree 及其详细信息

**语法:**
```bash
git worktree list [--porcelain] [-v | --verbose]
```

**示例:**

```bash
# 基本列表
git worktree list

# 机器可读格式
git worktree list --porcelain

# 详细信息(包含锁定原因等)
git worktree list --verbose
```

**输出格式:**
```
/path/to/main-repo    abc123f [main]
/path/to/worktree-1   def456g [feature/login]
/path/to/worktree-2   ghi789h (detached HEAD)
```

### git worktree remove

删除 worktree

**语法:**
```bash
git worktree remove [-f] <worktree>
```

**示例:**

```bash
# 删除 worktree
git worktree remove ../feature-login-worktree

# 强制删除(即使有未提交变更)
git worktree remove --force ../feature-login-worktree
```

**注意事项:**
- 删除 worktree 不会删除关联的分支
- 如果有未提交的变更,需要使用 `--force`
- 删除后需要运行 `git worktree prune` 清理记录

### git worktree move

移动 worktree 到新路径

**语法:**
```bash
git worktree move <worktree> <new-path>
```

**示例:**

```bash
# 移动 worktree
git worktree move ../old-location ../new-location
```

### git worktree prune

清理 worktree 的元数据

**语法:**
```bash
git worktree prune [-n] [-v] [--expire <expire>]
```

**示例:**

```bash
# 清理所有孤立的 worktree 记录
git worktree prune

# 预览将删除的记录
git worktree prune --dry-run

# 清理超过指定时间的记录
git worktree prune --expire 30.days.ago
```

**使用场景:**
- 手动删除 worktree 目录后清理 Git 记录
- 定期清理已删除 worktree 的元数据

### git worktree lock/unlock

锁定或解锁 worktree

**语法:**
```bash
git worktree lock [--reason <string>] <worktree>
git worktree unlock <worktree>
```

**示例:**

```bash
# 锁定 worktree(防止被自动清理)
git worktree lock --reason "长期功能开发" ../feature-worktree

# 解锁 worktree
git worktree unlock ../feature-worktree
```

**使用场景:**
- 在可移动介质(USB 驱动器)上的 worktree
- 防止自动化脚本删除重要 worktree

### git worktree repair

修复 worktree 的管理文件

**语法:**
```bash
git worktree repair [<path>...]
```

**示例:**

```bash
# 修复所有 worktree
git worktree repair

# 修复特定 worktree
git worktree repair ../feature-worktree
```

**使用场景:**
- worktree 被移动后修复引用
- 手动编辑后修复损坏的配置

## 高级用法

### 与远程仓库协作

```bash
# 创建 worktree 并跟踪远程分支
git worktree add -b feature/new-api ../api-worktree origin/develop

# 在 worktree 中推送到远程
cd ../api-worktree
git push -u origin feature/new-api

# 拉取远程更新
git pull origin feature/new-api
```

### 多人协作

```bash
# 团队成员 A 创建 worktree
git worktree add -b feature/shared ../shared-feature

# 团队成员 A 推送分支
cd ../shared-feature
git push -u origin feature/shared

# 团队成员 B 创建相同分支的 worktree
git worktree add ../shared-feature origin/feature/shared
```

### 临时实验

```bash
# 创建临时 worktree 测试想法
git worktree add --detach ../experiment

# 实验完成后删除
git worktree remove ../experiment
```

## 常见工作流

### 并行开发多个功能

```bash
# 主仓库保持在 main 分支
cd main-repo

# 创建功能 1 的 worktree
git worktree add ../feature-1 -b feature/user-auth

# 创建功能 2 的 worktree  
git worktree add ../feature-2 -b feature/payment

# 在不同终端窗口同时开发
cd ../feature-1  # 终端 1
cd ../feature-2  # 终端 2
```

### 紧急修复

```bash
# 正在 feature 分支开发
cd feature-worktree

# 紧急修复需要基于 main
git worktree add ../hotfix -b hotfix/critical-bug main

# 在 hotfix worktree 中修复
cd ../hotfix
# 修复并提交

# 合并回 main
cd main-repo
git checkout main
git merge hotfix/critical-bug

# 清理
git worktree remove ../hotfix
git branch -d hotfix/critical-bug
```

### 代码审查

```bash
# 创建审查专用 worktree
git worktree add ../review origin/feature-to-review

# 审查代码
cd ../review
# 查看、测试代码

# 审查完成后删除
cd -
git worktree remove ../review
```

## 注意事项和限制

1. **不能同时检出同一分支** - 同一分支只能在一个 worktree 中检出
2. **共享配置** - 所有 worktree 共享 .git/config 和钩子
3. **路径必须唯一** - worktree 路径不能重复
4. **磁盘空间** - 每个 worktree 占用额外磁盘空间
5. **IDE 支持** - 某些 IDE 可能需要重新索引每个 worktree

## 故障排查

### Worktree 记录损坏

```bash
# 修复所有 worktree
git worktree repair

# 如果无法修复,手动清理
rm -rf .git/worktrees/<worktree-name>
git worktree prune
```

### 无法删除 worktree

```bash
# 检查是否有未提交变更
git -C path/to/worktree status

# 强制删除
git worktree remove --force path/to/worktree
```

### Worktree 路径冲突

```bash
# 列出所有 worktree
git worktree list

# 移动到新路径
git worktree move old-path new-path
```
