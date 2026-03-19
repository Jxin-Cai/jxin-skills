# Git Worktree 使用最佳实践

本文档总结了使用 Git worktree 的最佳实践、模式和技巧。

## 命名约定

### Worktree 路径命名

**推荐模式:**
```bash
# 使用描述性名称 + worktree 后缀
git worktree add ../user-authentication-worktree -b feature/user-auth

# 或简短但清晰的名称
git worktree add ../auth-wt -b feature/user-auth

# 包含 issue/ticket 编号
git worktree add ../JIRA-123-payment -b feature/JIRA-123-payment
```

**避免:**
```bash
# 过于简短,难以识别
git worktree add ../wt1 -b feature/auth

# 没有描述性
git worktree add ../temp -b feature/important-feature
```

### 分支命名

遵循项目的分支命名规范:

```bash
# 功能分支
git worktree add ../new-feature -b feature/descriptive-name

# 修复分支
git worktree add ../bug-fix -b fix/issue-123-description

# 实验分支
git worktree add ../experiment -b experiment/new-approach

# 发布分支
git worktree add ../release -b release/v2.0.0
```

## 目录组织

### 推荐结构

将所有 worktree 放在统一位置:

```
projects/
├── main-repo/              # 主仓库
├── main-repo-worktrees/    # 所有 worktree 的容器
│   ├── feature-auth/
│   ├── feature-payment/
│   └── hotfix-critical/
```

**创建脚本:**
```bash
#!/bin/bash
# 在统一位置创建 worktree
WORKTREE_DIR="../$(basename $(pwd))-worktrees"
mkdir -p "$WORKTREE_DIR"
git worktree add "$WORKTREE_DIR/$1" -b "$2"
```

### 替代方案:按类型组织

```
projects/
├── main-repo/
├── features/
│   ├── auth-worktree/
│   └── payment-worktree/
├── hotfixes/
│   └── critical-bug-worktree/
└── experiments/
    └── new-approach-worktree/
```

## 工作流程模式

### 模式 1: 功能隔离开发

适用于:并行开发多个独立功能

```bash
# 主仓库保持 main 分支
cd main-repo

# 为每个功能创建 worktree
git worktree add ../feature-1 -b feature/user-profile
git worktree add ../feature-2 -b feature/notifications
git worktree add ../feature-3 -b feature/settings

# 在不同终端/IDE 实例中开发
# 完成后依次合并
```

**优点:**
- 功能彼此隔离
- 可以快速切换上下文
- 避免频繁的 stash/unstash

### 模式 2: 长期分支维护

适用于:维护多个版本或长期分支

```bash
# 为每个版本创建 worktree
git worktree add ../v1-maintenance -b maintain/v1.x
git worktree add ../v2-maintenance -b maintain/v2.x
git worktree add ../v3-development -b develop

# 在需要时分别处理各版本
```

**优点:**
- 避免频繁切换分支
- 保持构建环境独立
- 减少依赖冲突

### 模式 3: 审查和比较

适用于:代码审查或比较不同方案

```bash
# 创建审查专用 worktree
git worktree add --detach ../pr-review origin/pr-branch

# 比较不同实现
git worktree add ../approach-a -b experiment/approach-a
git worktree add ../approach-b -b experiment/approach-b

# 并排比较,选择最佳方案
```

### 模式 4: 紧急修复

适用于:在开发过程中处理紧急问题

```bash
# 正在功能开发中
cd feature-worktree

# 紧急问题出现
cd main-repo
git worktree add ../hotfix -b hotfix/critical main

# 修复并部署
cd ../hotfix
# 修复代码
git push

# 返回功能开发
cd ../feature-worktree
```

## 依赖管理

### Node.js 项目

每个 worktree 独立安装依赖:

```bash
# 创建 worktree
git worktree add ../feature-new-api -b feature/new-api

cd ../feature-new-api

# 安装依赖(使用快速包管理器)
pnpm install  # 或 npm install / bun install

# 如果使用 pnpm,可以链接到主仓库节省空间
# pnpm install --prefer-offline
```

### Python 项目

为每个 worktree 创建虚拟环境:

```bash
# 创建 worktree
git worktree add ../feature-ml-model -b feature/ml-model

cd ../feature-ml-model

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 共享依赖策略

对于大型依赖,考虑符号链接:

```bash
# 仅适用于只读依赖
cd worktree
ln -s ../main-repo/node_modules node_modules

# ⚠️ 注意:修改可能影响主仓库
```

## 性能优化

### 减少磁盘使用

```bash
# Git 对象是共享的,只有工作目录占用空间
# 使用 sparse-checkout 减少检出文件
cd worktree
git sparse-checkout init --cone
git sparse-checkout set src/specific-module
```

### 加速 worktree 创建

```bash
# 使用本地分支(避免网络请求)
git worktree add ../new-feature -b feature/new main

# 而不是
git worktree add ../new-feature -b feature/new origin/main
```

### 批量操作

```bash
# 批量创建 worktree
features="auth payment notifications settings"
for f in $features; do
    git worktree add "../feature-$f" -b "feature/$f"
done
```

## 清理和维护

### 定期清理

建立清理习惯:

```bash
#!/bin/bash
# cleanup-worktrees.sh

# 列出所有 worktree
echo "当前 worktree:"
git worktree list

# 清理孤立记录
git worktree prune

# 删除已合并的分支
git branch --merged | grep -v "\*" | grep -v "main" | xargs -n 1 git branch -d
```

### 自动化清理

使用 Git 钩子自动清理:

```bash
# .git/hooks/post-merge
#!/bin/bash
# 合并后清理 worktree

BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
WORKTREE_PATH="../${BRANCH_NAME}-worktree"

if [ -d "$WORKTREE_PATH" ]; then
    read -p "删除 worktree $WORKTREE_PATH? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git worktree remove "$WORKTREE_PATH"
    fi
fi
```

## IDE 集成

### Visual Studio Code

每个 worktree 可以有独立的 VS Code workspace:

```bash
# 为 worktree 创建 workspace
cd worktree
code . --new-window
```

**workspace 设置:**
```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "git.repositoryPath": ".",
    "git.detectSubmodules": false
  }
}
```

### JetBrains IDEs

在 worktree 中打开项目时:

1. 选择 "Open" 而不是 "Attach"
2. 允许 IDE 重新索引
3. 配置独立的运行配置

## 团队协作

### 共享约定

团队应约定:

1. **Worktree 位置约定** - 所有人使用相同的目录结构
2. **分支命名规范** - 一致的命名模式
3. **清理策略** - 何时删除 worktree 和分支
4. **文档** - 在 README 中说明 worktree 使用

### .gitignore 配置

添加 worktree 目录到 .gitignore:

```gitignore
# Worktree 目录
*-worktree/
*-wt/
worktrees/
```

## 安全考虑

### 敏感信息

确保每个 worktree 有独立的环境配置:

```bash
# 创建 worktree 后
cd new-worktree

# 复制环境文件(不要符号链接)
cp ../main-repo/.env.example .env
# 编辑 .env 填入值
```

### 备份

Worktree 只是工作目录,Git 对象仍在主仓库:

```bash
# 备份策略:
# 1. 定期推送分支到远程
# 2. 备份主仓库的 .git 目录
# 3. 不需要单独备份 worktree(可重建)
```

## 常见陷阱

### 1. 在多个 worktree 修改同一文件

**问题:** 容易产生冲突

**解决:**
- 明确每个 worktree 的职责范围
- 使用不同的模块/目录
- 频繁同步主分支

### 2. 忘记删除 worktree

**问题:** 占用磁盘空间

**解决:**
```bash
# 定期运行清理脚本
git worktree list | grep -v "$(pwd)" | awk '{print $1}' | \
  while read path; do
    if [ ! -d "$path" ]; then
      git worktree prune
    fi
  done
```

### 3. 依赖版本冲突

**问题:** 不同 worktree 需要不同依赖版本

**解决:**
- 为每个 worktree 独立安装依赖
- 使用容器化开发环境(Docker)
- 使用虚拟环境(Python venv, Node nvm)

### 4. 环境配置混乱

**问题:** 共享配置导致冲突

**解决:**
- 每个 worktree 独立的 .env 文件
- 使用环境变量隔离
- 文档化配置需求
