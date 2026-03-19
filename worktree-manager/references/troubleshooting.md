# Git Worktree 故障排查指南

本文档列出使用 Git worktree 时的常见问题及其解决方案。

## 创建问题

### 错误: "fatal: invalid reference"

**症状:**
```bash
$ git worktree add ../new-feature -b feature/new
fatal: invalid reference: feature/new
```

**原因:** 分支名包含非法字符或格式

**解决方案:**
```bash
# 检查分支名是否符合 Git 规范
# 避免: 空格、~、^、:、?、*、[、\

# 正确的命名
git worktree add ../new-feature -b feature/new-auth
git worktree add ../new-feature -b feature_new_auth
```

### 错误: "'path' already exists"

**症状:**
```bash
$ git worktree add ../feature-auth -b feature/auth
fatal: '../feature-auth' already exists
```

**原因:** 目标路径已存在

**解决方案:**
```bash
# 方案1: 使用不同路径
git worktree add ../feature-auth-v2 -b feature/auth

# 方案2: 删除现有目录(确保没有重要数据)
rm -rf ../feature-auth
git worktree add ../feature-auth -b feature/auth

# 方案3: 使用 --force(谨慎使用)
git worktree add --force ../feature-auth -b feature/auth
```

### 错误: "branch 'xxx' is already checked out"

**症状:**
```bash
$ git worktree add ../another-worktree feature/existing
fatal: 'feature/existing' is already checked out at '../existing-worktree'
```

**原因:** 同一分支不能同时在多个 worktree 中检出

**解决方案:**
```bash
# 方案1: 创建新分支
git worktree add ../new-worktree -b feature/existing-copy feature/existing

# 方案2: 使用现有 worktree
cd ../existing-worktree

# 方案3: 删除旧 worktree 后重新创建
git worktree remove ../existing-worktree
git worktree add ../another-worktree feature/existing

# 方案4: 使用分离 HEAD(临时查看)
git worktree add --detach ../temp feature/existing
```

## 删除问题

### 错误: "contains modified or untracked files"

**症状:**
```bash
$ git worktree remove ../feature-worktree
fatal: '../feature-worktree' contains modified or untracked files, use --force to delete it
```

**原因:** Worktree 中有未提交的变更

**解决方案:**
```bash
# 方案1: 提交变更
cd ../feature-worktree
git add .
git commit -m "保存进度"
cd -
git worktree remove ../feature-worktree

# 方案2: 暂存变更
cd ../feature-worktree
git stash
cd -
git worktree remove ../feature-worktree

# 方案3: 强制删除(数据会丢失!)
git worktree remove --force ../feature-worktree

# 方案4: 移动 worktree 到其他位置备份
mv ../feature-worktree ../feature-worktree-backup
git worktree prune
```

### 错误: "not a working tree"

**症状:**
```bash
$ git worktree remove ../some-path
fatal: '../some-path' is not a working tree
```

**原因:** 路径不是有效的 worktree

**解决方案:**
```bash
# 检查有效的 worktree
git worktree list

# 使用正确的路径
git worktree remove <正确的路径>

# 如果是孤立记录,清理
git worktree prune
```

### Worktree 已手动删除,无法使用 remove

**症状:** 手动删除目录后,Git 仍认为 worktree 存在

**解决方案:**
```bash
# 清理孤立的 worktree 记录
git worktree prune

# 或手动删除记录
rm -rf .git/worktrees/<worktree-name>
git worktree prune
```

## 操作问题

### 错误: "worktree HEAD points to a non-existent ref"

**症状:** Worktree 损坏,无法正常使用

**原因:** worktree 的引用被破坏

**解决方案:**
```bash
# 修复 worktree
git worktree repair

# 或在 worktree 内修复
cd ../problem-worktree
git worktree repair

# 如果无法修复,重新创建
cd main-repo
git worktree remove --force ../problem-worktree
git worktree add ../problem-worktree existing-branch
```

### 移动 worktree 后 Git 无法识别

**症状:** 移动 worktree 目录后,Git 找不到它

**解决方案:**
```bash
# 使用 Git 命令移动
git worktree move old-path new-path

# 如果已经手动移动,修复引用
git worktree repair new-path

# 如果修复失败,重新创建
git worktree prune
git worktree add new-path existing-branch
```

### 在 worktree 中无法切换分支

**症状:**
```bash
$ cd ../feature-worktree
$ git checkout main
fatal: 'main' is already checked out at '/path/to/main-repo'
```

**原因:** 主仓库已检出该分支

**解决方案:**
```bash
# 方案1: 切换到其他分支
git checkout -b temp-branch

# 方案2: 使用分离 HEAD
git checkout --detach main

# 方案3: 在主仓库中切换分支
cd main-repo
git checkout other-branch
cd ../feature-worktree
git checkout main
```

## 合并和冲突

### 合并时出现"Already up to date"

**症状:** 合并 worktree 分支时显示已是最新

**原因:** 可能在错误的分支或分支已合并

**解决方案:**
```bash
# 检查当前分支
git branch

# 确认要合并的分支有新提交
git log main..worktree-branch

# 如果有提交但显示最新,可能需要强制合并
git merge --no-ff worktree-branch
```

### 合并冲突解决

**症状:** 合并 worktree 时出现冲突

**解决方案:**
```bash
# 查看冲突文件
git status

# 方案1: 手动解决
# 编辑冲突文件,保留需要的内容
git add <解决的文件>
git commit

# 方案2: 使用合并工具
git mergetool

# 方案3: 取消合并重新开始
git merge --abort

# 方案4: 使用 cherry-pick 选择性合并
git cherry-pick <commit-hash>
```

## 性能问题

### Worktree 创建缓慢

**症状:** 创建 worktree 花费很长时间

**原因:** 大型仓库或网络问题

**解决方案:**
```bash
# 使用本地分支(不从远程拉取)
git worktree add ../new-wt -b new-branch existing-local-branch

# 使用浅克隆(如果是新仓库)
git clone --depth 1 <repo-url>

# 使用 sparse-checkout 减少文件
git sparse-checkout init --cone
git sparse-checkout set <path>
```

### 磁盘空间不足

**症状:** 多个 worktree 占用大量磁盘空间

**解决方案:**
```bash
# 清理未使用的 worktree
git worktree list
git worktree remove <unused-worktree>

# 使用 sparse-checkout
cd worktree
git sparse-checkout init --cone
git sparse-checkout set src/

# 清理 Git 对象(所有 worktree 共享)
git gc --aggressive

# 考虑使用符号链接共享只读文件
ln -s ../main-repo/large-readonly-dir large-readonly-dir
```

## IDE 和工具集成

### VS Code 无法识别 worktree 为 Git 仓库

**症状:** VS Code 不显示 Git 状态

**解决方案:**
```bash
# 在 worktree 中打开 VS Code
cd worktree
code .

# 检查 .vscode/settings.json
{
  "git.repositoryPath": ".",
  "git.enabled": true
}
```

### IDE 索引问题

**症状:** IDE 显示错误或无法找到文件

**解决方案:**
1. 重新启动 IDE
2. 使缓存/索引无效并重启
3. 在每个 worktree 中单独打开项目
4. 配置 IDE 忽略其他 worktree 的路径

### Git 钩子不执行

**症状:** 在 worktree 中提交时钩子未运行

**原因:** 钩子在主仓库的 .git/hooks,worktree 可能找不到

**解决方案:**
```bash
# 方案1: 使用 core.hooksPath 配置
git config core.hooksPath /path/to/main-repo/.git/hooks

# 方案2: 在 worktree 中创建符号链接
cd worktree/.git
ln -s ../../main-repo/.git/hooks hooks

# 方案3: 使用 Husky 等工具(自动处理)
```

## 环境和依赖

### Node.js: node_modules 冲突

**症状:** 不同 worktree 的依赖版本冲突

**解决方案:**
```bash
# 每个 worktree 独立安装
cd worktree
rm -rf node_modules
npm install  # 或 pnpm install

# 使用 pnpm workspace(推荐)
# 在根目录 pnpm-workspace.yaml:
packages:
  - 'worktrees/*'

# 或使用 nvm 切换 Node 版本
nvm use 16  # 在 worktree-1
nvm use 18  # 在 worktree-2
```

### Python: 虚拟环境路径问题

**症状:** 虚拟环境激活后路径不正确

**解决方案:**
```bash
# 每个 worktree 创建独立虚拟环境
cd worktree
python -m venv venv
source venv/bin/activate

# 或使用 pyenv 管理版本
pyenv local 3.9.0  # 在 worktree-1
pyenv local 3.10.0 # 在 worktree-2
```

### 数据库迁移冲突

**症状:** 不同 worktree 的数据库迁移冲突

**解决方案:**
```bash
# 使用独立的数据库实例
# .env in worktree-1
DATABASE_URL=postgresql://localhost/db_feature1

# .env in worktree-2
DATABASE_URL=postgresql://localhost/db_feature2

# 或使用 Docker 容器
docker run -d --name db-worktree1 -p 5432:5432 postgres
docker run -d --name db-worktree2 -p 5433:5432 postgres
```

## 诊断工具

### 检查 worktree 状态

```bash
# 详细列表
git worktree list --verbose

# 检查特定 worktree
git worktree list | grep worktree-name

# 检查 worktree Git 目录
ls -la .git/worktrees/
```

### 验证 worktree 完整性

```bash
# 修复所有 worktree
git worktree repair

# 清理孤立记录
git worktree prune --verbose

# 检查文件系统
for wt in .git/worktrees/*; do
  echo "Checking $wt"
  cat "$wt/gitdir"
done
```

### 调试脚本

```bash
#!/bin/bash
# debug-worktree.sh - 诊断 worktree 问题

echo "=== Git Worktree 诊断 ==="
echo ""

echo "1. Worktree 列表:"
git worktree list
echo ""

echo "2. Worktree 元数据:"
ls -la .git/worktrees/
echo ""

echo "3. 分支状态:"
git branch -vv
echo ""

echo "4. 修复 worktree:"
git worktree repair
echo ""

echo "5. 清理孤立记录:"
git worktree prune --dry-run
echo ""

echo "诊断完成"
```

## 预防措施

### 最佳实践清单

- [ ] 使用有意义的 worktree 名称
- [ ] 定期运行 `git worktree prune`
- [ ] 完成后立即删除 worktree
- [ ] 保持 worktree 数量在合理范围(建议 < 5 个)
- [ ] 为每个 worktree 配置独立环境
- [ ] 文档化团队的 worktree 使用约定
- [ ] 定期备份重要的未推送分支
- [ ] 在 .gitignore 中排除 worktree 目录

### 监控脚本

```bash
#!/bin/bash
# monitor-worktrees.sh - 监控 worktree 健康状况

MAX_WORKTREES=5
WORKTREE_COUNT=$(git worktree list | wc -l)

if [ $WORKTREE_COUNT -gt $MAX_WORKTREES ]; then
    echo "⚠️  警告: 有 $WORKTREE_COUNT 个worktree (建议 < $MAX_WORKTREES)"
    echo "考虑清理未使用的 worktree"
fi

# 检查孤立记录
if git worktree prune --dry-run | grep -q "Removing"; then
    echo "⚠️  发现孤立的 worktree 记录"
    echo "运行: git worktree prune"
fi

echo "✅ Worktree 健康检查完成"
```
