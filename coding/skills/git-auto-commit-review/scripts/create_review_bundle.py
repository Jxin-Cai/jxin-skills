#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class BundlePaths:
    base_name: str
    out_dir: Path
    report_md: Path
    status_txt: Path
    diff_patch: Path
    diff_staged_patch: Path
    log_txt: Path
    meta_json: Path


def _run_git(args: list[str]) -> str:
    p = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if p.returncode != 0 and p.stderr.strip():
        print(f"WARNING: git {' '.join(args)} stderr: {p.stderr.strip()}", flush=True)
    return p.stdout


def _slugify_filename(s: str) -> str:
    s = s.strip()
    if not s:
        return "unknown"
    # Replace whitespace with underscore, then drop unsafe chars
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9._-]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unknown"


def _git_username() -> str:
    name = _run_git(["config", "user.name"]).strip()
    if name:
        return _slugify_filename(name)
    email = _run_git(["config", "user.email"]).strip()
    if email:
        local = email.split("@", 1)[0]
        return _slugify_filename(local)
    return "unknown"


def _timestamp() -> str:
    # YYYYMMDDHHMMSS
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _detect_branch() -> str:
    out = _run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    return out or "unknown"


def _detect_repo_root() -> Optional[Path]:
    out = _run_git(["rev-parse", "--show-toplevel"]).strip()
    return Path(out) if out else None


def _bundle_paths(out_dir: Path, base_name: str) -> BundlePaths:
    return BundlePaths(
        base_name=base_name,
        out_dir=out_dir,
        report_md=out_dir / f"{base_name}.md",
        status_txt=out_dir / f"{base_name}.status.txt",
        diff_patch=out_dir / f"{base_name}.diff.patch",
        diff_staged_patch=out_dir / f"{base_name}.diff_staged.patch",
        log_txt=out_dir / f"{base_name}.log.txt",
        meta_json=out_dir / f"{base_name}.meta.json",
    )


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _render_report_template(meta: dict) -> str:
    base_name = meta["base_name"]
    return f"""# 代码审查报告

- 报告编号: `{base_name}`
- 时间: `{meta["created_at_local"]}`
- Git 用户: `{meta["git_username_raw"]}` → `{meta["git_username_sanitized"]}`
- 分支: `{meta["branch"]}`

## 变更概览（填写）

- 本次改动目的:
- 影响范围（模块/层级）:
- 风险等级: 低 / 中 / 高

## Diff 证据（自动生成）

- 未暂存: `{base_name}.diff.patch`
- 已暂存: `{base_name}.diff_staged.patch`
- 状态: `{base_name}.status.txt`

## 审查结论（填写）

### 必须修复

- [ ] （填写）

### 建议改进

- [ ] （填写）

## 建议明细（填写）

> 审查规则来源：本技能 references/ 目录下的 review-rules.md（及按技术栈选择的扩展规则文件）

## 开发者决策（必填）

- 采纳建议: 全部 / 部分 / 不采纳
- 采纳列表（逐条列出）:
- 不采纳原因（可选）:

## 已执行变更（可选，用于二次检查）

- 已采纳并完成的修改（逐条列出）:
- 重新跑的测试/验证（命令 + 结果）:
- 二次检查结论（是否可以提交）:

## 提交信息（必填，遵守规范）

候选 commit message:

`<type>(<scope>): <subject>`

允许的 type: feat / fix / to / docs / style / refactor / perf / test / chore / revert / merge / sync

subject 要求: 中文优先，<=50 字，不要结尾标点

最终确认 commit message:

`（填写）`

## 提交摘要（必填）

- 这次 commit 做了什么（1-3 句）:
- 变更文件数:
- 变更行数（可选）:
"""

def _parse_timestamp_from_base_name(base_name: str) -> Optional[str]:
    # Expect: YYYYMMDDHHMMSS_<user>
    m = re.match(r"^(?P<ts>\d{14})_", base_name)
    return m.group("ts") if m else None


def _find_latest_base_name(out_dir: Path, *, git_user_sanitized: str) -> Optional[str]:
    """
    Pick latest bundle for current git user by timestamp prefix.
    Looks for: code_review_reports/YYYYMMDDHHMMSS_<user>.meta.json
    """
    candidates: list[tuple[str, str]] = []
    pattern = f"*_{git_user_sanitized}.meta.json"
    for meta_path in out_dir.glob(pattern):
        base_name = meta_path.name[: -len(".meta.json")]
        ts = _parse_timestamp_from_base_name(base_name)
        if ts:
            candidates.append((ts, base_name))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]


def _load_existing_meta(meta_path: Path) -> Optional[dict]:
    try:
        if not meta_path.exists():
            return None
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        # Corrupted meta shouldn't block capture; we'll regenerate meta.
        return None


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="create_review_bundle.py",
        description=(
            "Create or update a CodeReview bundle under code_review_reports/.\n"
            "Default: create a new timestamped bundle.\n"
            "Update mode: overwrite diff/status/log/meta for an existing bundle, without creating new files."
        ),
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--base-name",
        help="Update the specified base_name (e.g. 20260108180243_Thanos). Overwrites snapshots in-place.",
    )
    g.add_argument(
        "--update-latest",
        action="store_true",
        help="Update the latest bundle for current git user (overwrites snapshots in-place).",
    )
    return p.parse_args()


def _check_gitignore(repo_root: Path, dir_name: str) -> None:
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        print(f"WARNING: .gitignore not found. Consider adding '{dir_name}/' to .gitignore.", flush=True)
        return
    content = gitignore.read_text(encoding="utf-8")
    if dir_name not in content:
        print(f"WARNING: '{dir_name}/' not found in .gitignore. Add it to avoid accidentally committing review reports.", flush=True)


def main() -> int:
    args = _parse_args()

    repo_root = _detect_repo_root()
    if repo_root is None:
        print("ERROR: Not a git repository (git rev-parse failed).")
        return 2

    out_dir = repo_root / "code_review_reports"
    _check_gitignore(repo_root, "code_review_reports")
    git_user_sanitized = _git_username()
    if args.base_name:
        base_name = args.base_name.strip()
    elif args.update_latest:
        latest = _find_latest_base_name(out_dir, git_user_sanitized=git_user_sanitized)
        if latest is None:
            print(f"ERROR: No existing bundle found for user {git_user_sanitized} in {out_dir}")
            return 2
        base_name = latest
    else:
        ts = _timestamp()
        base_name = f"{ts}_{git_user_sanitized}"

    # capture raw for transparency (may include spaces)
    git_user_raw = _run_git(["config", "user.name"]).strip() or _run_git(["config", "user.email"]).strip() or "unknown"

    paths = _bundle_paths(out_dir=out_dir, base_name=base_name)

    existing_meta = _load_existing_meta(paths.meta_json)
    created_at_local = (
        (existing_meta.get("created_at_local") if isinstance(existing_meta, dict) else None)
        or datetime.now().isoformat(timespec="seconds")
    )

    meta = {
        "base_name": base_name,
        "created_at_local": created_at_local,
        "updated_at_local": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(repo_root),
        "branch": _detect_branch(),
        "git_username_raw": git_user_raw,
        "git_username_sanitized": git_user_sanitized,
        "paths": {
        "report_md": str(paths.report_md),
        "status_txt": str(paths.status_txt),
        "diff_patch": str(paths.diff_patch),
        "diff_staged_patch": str(paths.diff_staged_patch),
        "log_txt": str(paths.log_txt),
        "meta_json": str(paths.meta_json),
        },
    }

    status = _run_git(["status", "--porcelain=v1", "-b"])
    diff = _run_git(["diff"])
    diff_staged = _run_git(["diff", "--staged"])
    log = _run_git(["log", "-n", "20", "--oneline", "--decorate"])

    _write_text(paths.status_txt, status)
    _write_text(paths.diff_patch, diff)
    _write_text(paths.diff_staged_patch, diff_staged)
    _write_text(paths.log_txt, log)
    _write_text(paths.meta_json, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

    if not paths.report_md.exists():
        _write_text(paths.report_md, _render_report_template(meta))

    print(str(paths.report_md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

