#!/bin/bash
# merge_worktree.sh - 合并 worktree 的变更到主库的目标分支

set -e

# 使用说明
usage() {
    echo "用法: $0 <worktree路径> <目标分支>"
    echo ""
    echo "参数:"
    echo "  worktree路径  要合并的 worktree 路径"
    echo "  目标分支      合并到的目标分支(通常是 main 或 develop)"
    echo ""
    echo "示例:"
    echo "  $0 ../user-auth-worktree main"
    echo "  $0 ../payment-feature-worktree develop"
    exit 1
}

# 检查参数
if [ $# -lt 2 ]; then
    usage
fi

WORKTREE_PATH=$1
TARGET_BRANCH=$2

echo "🔀 合并 worktree 到目标分支"
echo "   Worktree: ${WORKTREE_PATH}"
echo "   目标分支: ${TARGET_BRANCH}"
echo ""

# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    exit 1
fi

# 检查 worktree 路径是否存在
if [ ! -d "${WORKTREE_PATH}" ]; then
    echo "❌ 错误: Worktree 路径 '${WORKTREE_PATH}' 不存在"
    exit 1
fi

# 检查目标分支是否存在
if ! git rev-parse --verify "${TARGET_BRANCH}" > /dev/null 2>&1; then
    echo "❌ 错误: 目标分支 '${TARGET_BRANCH}' 不存在"
    exit 1
fi

# 获取 worktree 的分支名
cd "${WORKTREE_PATH}"
WORKTREE_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "   Worktree 分支: ${WORKTREE_BRANCH}"
echo ""

# 检查是否有未提交的变更
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  警告: Worktree 中有未提交的变更"
    echo "   请先提交或暂存这些变更"
    git status --short
    exit 1
fi

# 返回主仓库
cd - > /dev/null

# 切换到目标分支
echo "📌 切换到目标分支: ${TARGET_BRANCH}"
git checkout "${TARGET_BRANCH}"

# 拉取最新变更
echo "⬇️  拉取最新变更..."
git pull origin "${TARGET_BRANCH}" || echo "无法拉取,继续合并本地分支"

# 合并 worktree 分支
echo ""
echo "🔀 合并分支: ${WORKTREE_BRANCH} -> ${TARGET_BRANCH}"
if git merge "${WORKTREE_BRANCH}" --no-ff -m "Merge ${WORKTREE_BRANCH} into ${TARGET_BRANCH}"; then
    echo ""
    echo "✅ 合并成功!"
    echo ""
    echo "下一步:"
    echo "  1. 检查合并结果: git log --oneline -5"
    echo "  2. 推送到远程: git push origin ${TARGET_BRANCH}"
    echo "  3. 清理 worktree: bash scripts/cleanup_worktree.sh ${WORKTREE_PATH}"
else
    echo ""
    echo "❌ 合并失败,请解决冲突后继续"
    echo ""
    echo "解决冲突步骤:"
    echo "  1. 查看冲突文件: git status"
    echo "  2. 手动编辑冲突文件"
    echo "  3. 标记已解决: git add <文件>"
    echo "  4. 完成合并: git commit"
    exit 1
fi
