#!/bin/bash
# list_worktrees.sh - 列出所有 Git worktree

set -e

echo "📋 Git Worktree 列表"
echo "===================="
echo ""

# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    exit 1
fi

# 获取 worktree 列表
worktrees=$(git worktree list --porcelain)

if [ -z "$worktrees" ]; then
    echo "📭 没有找到 worktree"
    exit 0
fi

# 解析并显示 worktree 信息
current_worktree=""
current_head=""
current_branch=""

while IFS= read -r line; do
    if [[ $line == worktree* ]]; then
        # 新的 worktree 开始
        if [ -n "$current_worktree" ]; then
            # 显示上一个 worktree 的信息
            echo "📂 路径: $current_worktree"
            echo "   分支: $current_branch"
            echo "   HEAD: ${current_head:0:8}"
            echo ""
        fi
        current_worktree="${line#worktree }"
        current_head=""
        current_branch=""
    elif [[ $line == HEAD* ]]; then
        current_head="${line#HEAD }"
    elif [[ $line == branch* ]]; then
        current_branch="${line#branch }"
        current_branch="${current_branch#refs/heads/}"
    fi
done <<< "$worktrees"

# 显示最后一个 worktree
if [ -n "$current_worktree" ]; then
    echo "📂 路径: $current_worktree"
    echo "   分支: $current_branch"
    echo "   HEAD: ${current_head:0:8}"
    echo ""
fi

# 显示总数
count=$(echo "$worktrees" | grep -c "^worktree")
echo "总计: $count 个 worktree"
