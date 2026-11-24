from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    source: Path
    web_root: Path
    route: str
    summary: str
    include_publicly: bool
    category: str
    commit: str | None
    committed_at: datetime
    message: str | None
    upstream: str | None
    date_is_filesystem: bool = False
    include_files: tuple[str, ...] | None = None
