#!/bin/bash
# create_worktree.sh - 创建新的 Git worktree

set -e

# 使用说明
usage() {
    echo "用法: $0 <功能名称> [基础分支]"
    echo ""
    echo "参数:"
    echo "  功能名称    新功能的名称(用于命名worktree和分支)"
    echo "  基础分支    可选,基于哪个分支创建(默认: main)"
    echo ""
    echo "示例:"
    echo "  $0 user-auth"
    echo "  $0 payment-feature develop"
    exit 1
}

# 检查参数
if [ $# -lt 1 ]; then
    usage
fi

FEATURE_NAME=$1
BASE_BRANCH=${2:-main}
BRANCH_NAME="feature/${FEATURE_NAME}"
WORKTREE_PATH="../${FEATURE_NAME}-worktree"

echo "🚀 创建 worktree 用于功能: ${FEATURE_NAME}"
echo "   基础分支: ${BASE_BRANCH}"
echo "   Worktree 路径: ${WORKTREE_PATH}"
echo ""

# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    exit 1
fi

# 检查基础分支是否存在
if ! git rev-parse --verify "${BASE_BRANCH}" > /dev/null 2>&1; then
    echo "❌ 错误: 基础分支 '${BASE_BRANCH}' 不存在"
    exit 1
fi

# 检查 worktree 路径是否已存在
if [ -d "${WORKTREE_PATH}" ]; then
    echo "❌ 错误: Worktree 路径 '${WORKTREE_PATH}' 已存在"
    exit 1
fi

# 创建 worktree
echo "📂 创建 worktree..."
git worktree add "${WORKTREE_PATH}" -b "${BRANCH_NAME}" "${BASE_BRANCH}"

echo ""
echo "✅ Worktree 创建成功!"
echo ""
echo "下一步:"
echo "  1. 切换到 worktree: cd ${WORKTREE_PATH}"
echo "  2. 开始开发你的功能"
echo "  3. 提交变更: git add . && git commit -m '你的提交信息'"
echo "  4. 合并回主库: bash scripts/merge_worktree.sh ${WORKTREE_PATH} main"
