#!/usr/bin/env python3
"""管理文章快照、差异、回滚与增量编辑影响分析。"""

import argparse
import difflib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from shared import extract_h2_headings, extract_title, read_article


MAX_VERSIONS = 10


class VersionManager:
    def __init__(self, article_file: Path, store_root: Optional[Path] = None):
        self.article_file = article_file.resolve()
        root = store_root or self.article_file.parent / ".tech-article-writer" / "versions"
        safe_name = re.sub(r"[^0-9A-Za-z一-鿿._-]+", "-", self.article_file.stem).strip("-") or "article"
        self.version_dir = root / safe_name
        self.metadata_file = self.version_dir / "meta.json"

    def _load_metadata(self) -> Dict[str, object]:
        if not self.metadata_file.exists():
            return {"article_file": str(self.article_file), "versions": []}
        return json.loads(self.metadata_file.read_text(encoding="utf-8"))

    def _save_metadata(self, metadata: Dict[str, object]) -> None:
        self.version_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def snapshot(self, note: str = "", kind: str = "edit") -> int:
        if not self.article_file.exists():
            raise FileNotFoundError(self.article_file)
        metadata = self._load_metadata()
        versions = metadata["versions"]
        latest = max((int(item["version"]) for item in versions), default=0)
        version = latest + 1
        content = read_article(self.article_file)
        snapshot_file = self.version_dir / f"v{version}.md"
        self.version_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file.write_text(content, encoding="utf-8")
        versions.append({
            "version": version,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "title": extract_title(content),
            "kind": kind,
            "note": note,
            "size": len(content.encode("utf-8")),
        })
        while len(versions) > MAX_VERSIONS:
            removed = versions.pop(0)
            (self.version_dir / f"v{removed['version']}.md").unlink(missing_ok=True)
        self._save_metadata(metadata)
        return version

    def list_versions(self) -> List[Dict[str, object]]:
        return list(self._load_metadata()["versions"])

    def _resolve_version(self, version: int) -> Path:
        path = self.version_dir / f"v{version}.md"
        if not path.exists():
            raise ValueError(f"版本不存在: v{version}")
        return path

    def diff(self, version: int) -> Tuple[str, Dict[str, int]]:
        old = self._resolve_version(version).read_text(encoding="utf-8").splitlines()
        current = read_article(self.article_file).splitlines()
        diff_lines = list(difflib.unified_diff(old, current, fromfile=f"v{version}", tofile="current", lineterm=""))
        added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
        return "\n".join(diff_lines), {"added_lines": added, "removed_lines": removed}

    def rollback(self, version: int) -> int:
        target = self._resolve_version(version)
        backup = self.snapshot(note=f"回滚到 v{version} 前的自动备份", kind="rollback-backup")
        shutil.copyfile(target, self.article_file)
        return backup

    def analyze_edit_impact(self, description: str) -> Dict[str, List[str]]:
        content = read_article(self.article_file)
        headings = extract_h2_headings(content)
        tokens = set(re.findall(r"[A-Za-z][A-Za-z0-9_.+-]*|[一-鿿]{2,8}", description.lower()))
        direct = [
            heading for heading in headings
            if any(token in heading.lower() or heading.lower() in token for token in tokens)
        ]
        if not direct and headings:
            direct = [headings[0]]

        consistency: List[str] = []
        for heading in direct:
            index = headings.index(heading)
            for neighbor in headings[max(0, index - 1):index + 2]:
                if neighbor not in direct and neighbor not in consistency:
                    consistency.append(neighbor)
        skip = [heading for heading in headings if heading not in direct and heading not in consistency]
        return {"regenerate": direct, "consistency_check": consistency, "skip": skip}


def print_versions(versions: List[Dict[str, object]]) -> None:
    if not versions:
        print("ℹ️ 暂无版本")
        return
    for item in versions:
        note = f" — {item['note']}" if item.get("note") else ""
        print(f"v{item['version']}  {item['created_at']}  {item['kind']}{note}")


def main() -> int:
    parser = argparse.ArgumentParser(description="文章版本与增量编辑管理")
    parser.add_argument("--action", required=True, choices=("snapshot", "list", "diff", "rollback", "smart-edit"))
    parser.add_argument("--article-file", required=True, help="Markdown 文章路径")
    parser.add_argument("--version", type=int, help="目标版本号")
    parser.add_argument("--note", default="", help="快照说明")
    parser.add_argument("--edit-description", help="计划修改的自然语言描述")
    parser.add_argument("--store-root", help="自定义版本存储根目录")
    args = parser.parse_args()

    manager = VersionManager(Path(args.article_file), Path(args.store_root) if args.store_root else None)
    try:
        if args.action == "snapshot":
            version = manager.snapshot(args.note)
            print(f"✅ 已创建版本快照: v{version}")
        elif args.action == "list":
            print_versions(manager.list_versions())
        elif args.action == "diff":
            if args.version is None:
                parser.error("diff 需要 --version")
            diff_text, summary = manager.diff(args.version)
            print(f"📊 变更摘要: +{summary['added_lines']} / -{summary['removed_lines']} 行")
            print(diff_text or "✅ 当前文章与目标版本无差异")
        elif args.action == "rollback":
            if args.version is None:
                parser.error("rollback 需要 --version")
            backup = manager.rollback(args.version)
            print(f"✅ 已回滚到 v{args.version}（回滚前内容备份为 v{backup}）")
        elif args.action == "smart-edit":
            if not args.edit_description:
                parser.error("smart-edit 需要 --edit-description")
            impact = manager.analyze_edit_impact(args.edit_description)
            print(json.dumps(impact, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"❌ 版本操作失败: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
