---
name: worktree-manager
description: Git worktree 管理技能,用于在单个仓库中并行开发多个功能。当需要:(1)像创建功能分支一样创建独立的 worktree (2)在 worktree 中开发新功能 (3)将 worktree 的变更合并回主库的功能分支 (4)管理、查看或清理现有 worktree 时使用此技能。
---

# Worktree 管理器

## 概述

Git worktree 允许在同一仓库中同时检出多个分支到不同目录。这个技能帮助你像使用功能分支一样管理 worktree,实现并行开发多个功能而互不干扰。

**核心优势:**
- 在独立的工作目录中并行开发多个功能
- 每个 worktree 有自己的文件和变更,互不影响
- 可以在不同 worktree 之间快速切换
- 开发完成后轻松合并回主分支

## 核心工作流

### 创建 Worktree 开发新功能

典型流程:

1. **创建 worktree** - 为新功能创建独立的工作目录
   ```bash
   # 使用提供的脚本
   bash scripts/create_worktree.sh <功能名称> [基础分支]
   
   # 或使用原生 Git 命令
   git worktree add path/to/worktree -b feature-branch-name
   ```

2. **在 worktree 中开发** - 切换到 worktree 目录进行开发
   ```bash
   cd path/to/worktree
   # 正常开发、提交代码
   git add .
   git commit -m "实现功能"
   ```

3. **合并到主库功能分支** - 开发完成后合并变更
   ```bash
   # 使用提供的脚本
   bash scripts/merge_worktree.sh <worktree路径> <目标分支>
   
   # 或手动操作
   cd main-repo
   git checkout target-branch
   git merge feature-branch-name
   ```

### 管理现有 Worktree

**查看所有 worktree:**
```bash
bash scripts/list_worktrees.sh
# 或
git worktree list
```

**切换回 worktree 继续开发:**
```bash
cd path/to/worktree
# 继续开发...
git add .
git commit -m "继续开发"
```

**清理不需要的 worktree:**
```bash
bash scripts/cleanup_worktree.sh <worktree路径>
# 或
git worktree remove path/to/worktree
```

## 常用操作

### 创建 Worktree

**基本创建:**
```bash
git worktree add ../feature-login -b feature/login
```

**基于特定分支创建:**
```bash
git worktree add ../hotfix-bug main
```

**创建并自动命名:**
```bash
git worktree add ../feature-payment -b feature/payment origin/develop
```

### 查看和管理

**列出所有 worktree:**
```bash
git worktree list
# 输出格式: 路径  分支  状态
```

**查看详细信息:**
```bash
git worktree list --porcelain
```

**删除 worktree:**
```bash
# 先移除 worktree
git worktree remove path/to/worktree

# 如果有未提交的更改,强制删除
git worktree remove --force path/to/worktree

# 清理孤立的 worktree 记录
git worktree prune
```

### 合并变更

从 worktree 合并变更到主库:

```bash
# 方法1: 在主库中合并 worktree 的分支
cd main-repo
git checkout target-branch
git merge worktree-branch-name

# 方法2: 使用 cherry-pick 选择性合并提交
git cherry-pick <commit-hash>
```

## 最佳实践

1. **命名规范** - 使用描述性的 worktree 和分支名称
   ```bash
   git worktree add ../feature-user-auth -b feature/user-auth
   ```

2. **保持同步** - 定期从主分支拉取更新
   ```bash
   cd worktree-path
   git fetch origin
   git merge origin/main
   ```

3. **及时清理** - 功能完成后删除不需要的 worktree
   ```bash
   git worktree remove path/to/worktree
   git branch -d feature-branch-name  # 删除已合并的分支
   ```

4. **避免冲突** - 不要在多个 worktree 中修改同一文件

5. **独立环境** - 每个 worktree 可能需要独立安装依赖
   - Node.js 项目: `npm install` 或 `pnpm install`
   - Python 项目: `python -m venv venv && pip install -r requirements.txt`

## 资源

### 脚本工具

- `scripts/create_worktree.sh` - 便捷创建 worktree
- `scripts/list_worktrees.sh` - 查看所有 worktree 状态
- `scripts/merge_worktree.sh` - 合并 worktree 到目标分支
- `scripts/cleanup_worktree.sh` - 安全清理 worktree

### 参考文档

- `references/worktree_commands.md` - Git worktree 完整命令参考
- `references/best_practices.md` - Worktree 使用最佳实践
- `references/troubleshooting.md` - 常见问题解决方案

## 注意事项

- Worktree 共享 Git 对象和配置,但有独立的工作目录
- 删除 worktree 不会自动删除关联的分支
- 某些 IDE 可能需要重新索引 worktree
- Worktree 路径必须在主仓库之外
