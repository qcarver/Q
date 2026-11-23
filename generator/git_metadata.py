from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


def _git(path: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def read_git_metadata(path: Path) -> dict[str, object]:
    head = _git(path, "rev-parse", "HEAD")
    if not head:
        return {}
    committed = _git(path, "log", "-1", "--format=%cI")
    return {
        "commit": head,
        "committed_at": datetime.fromisoformat(committed) if committed else None,
        "message": _git(path, "log", "-1", "--format=%s"),
        "upstream": _git(path, "remote", "get-url", "origin"),
    }
