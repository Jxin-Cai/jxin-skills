#!/bin/bash
# cleanup_worktree.sh - 安全清理 Git worktree

set -e

# 使用说明
usage() {
    echo "用法: $0 <worktree路径> [选项]"
    echo ""
    echo "参数:"
    echo "  worktree路径  要删除的 worktree 路径"
    echo ""
    echo "选项:"
    echo "  -f, --force   强制删除(即使有未提交的变更)"
    echo "  -b, --branch  同时删除关联的分支"
    echo ""
    echo "示例:"
    echo "  $0 ../user-auth-worktree"
    echo "  $0 ../payment-feature-worktree --force --branch"
    exit 1
}

# 检查参数
if [ $# -lt 1 ]; then
    usage
fi

WORKTREE_PATH=$1
FORCE=false
DELETE_BRANCH=false

# 解析选项
shift
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            FORCE=true
            ;;
        -b|--branch)
            DELETE_BRANCH=true
            ;;
        *)
            echo "❌ 未知选项: $1"
            usage
            ;;
    esac
    shift
done

echo "🗑️  清理 worktree"
echo "   路径: ${WORKTREE_PATH}"
echo ""

# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    exit 1
fi

# 检查 worktree 是否存在
if ! git worktree list | grep -q "${WORKTREE_PATH}"; then
    echo "❌ 错误: Worktree '${WORKTREE_PATH}' 不存在"
    echo ""
    echo "可用的 worktree:"
    git worktree list
    exit 1
fi

# 获取 worktree 的分支名
BRANCH_NAME=""
if [ -d "${WORKTREE_PATH}/.git" ] || [ -f "${WORKTREE_PATH}/.git" ]; then
    cd "${WORKTREE_PATH}"
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
    cd - > /dev/null
fi

# 检查是否有未提交的变更
if [ "$FORCE" = false ] && [ -d "${WORKTREE_PATH}" ]; then
    cd "${WORKTREE_PATH}"
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "⚠️  警告: Worktree 中有未提交的变更"
        echo ""
        git status --short
        echo ""
        echo "选项:"
        echo "  1. 先提交变更: git add . && git commit -m '...'"
        echo "  2. 使用 --force 强制删除"
        cd - > /dev/null
        exit 1
    fi
    cd - > /dev/null
fi

# 删除 worktree
echo "🗑️  删除 worktree..."
if [ "$FORCE" = true ]; then
    git worktree remove --force "${WORKTREE_PATH}"
else
    git worktree remove "${WORKTREE_PATH}"
fi

echo "✅ Worktree 已删除"

# 删除关联分支(如果指定)
if [ "$DELETE_BRANCH" = true ] && [ -n "$BRANCH_NAME" ]; then
    echo ""
    echo "🌿 删除关联分支: ${BRANCH_NAME}"
    
    # 检查分支是否已合并
    if git branch --merged | grep -q "${BRANCH_NAME}"; then
        git branch -d "${BRANCH_NAME}"
        echo "✅ 分支已删除"
    else
        echo "⚠️  警告: 分支未合并"
        echo "   使用 'git branch -D ${BRANCH_NAME}' 强制删除"
    fi
fi

# 清理孤立的 worktree 记录
echo ""
echo "🧹 清理孤立记录..."
git worktree prune

echo ""
echo "✅ 清理完成!"
