from __future__ import annotations

import tomllib
from datetime import datetime
from pathlib import Path

from .git_metadata import read_git_metadata
from .models import Project


def discover(config_path: Path, *, public: bool = False) -> list[Project]:
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    projects: list[Project] = []
    for project_id, item in data.get("projects", {}).items():
        include_publicly = bool(item.get("include_publicly", False))
        if public and not include_publicly:
            continue

        source = (config_path.parent / item["source"]).resolve()
        web_root = (source / item.get("web_root", ".")).resolve()
        if not web_root.is_relative_to(source):
            raise ValueError(f"{project_id}: web_root escapes the source directory")
        index = web_root / "index.html"
        if not index.is_file():
            raise ValueError(f"{project_id}: no index.html in {web_root}")

        git = read_git_metadata(source)
        committed_at = git.get("committed_at")
        filesystem_date = not isinstance(committed_at, datetime)
        if filesystem_date:
            committed_at = datetime.fromtimestamp(index.stat().st_mtime).astimezone()

        projects.append(Project(
            id=project_id,
            name=item.get("name", project_id),
            source=source,
            web_root=web_root,
            route=item.get("route", project_id),
            summary=item.get("summary", ""),
            include_publicly=include_publicly,
            category=item.get("category", "public" if include_publicly else "local"),
            commit=git.get("commit"),
            committed_at=committed_at,
            message=git.get("message"),
            upstream=git.get("upstream"),
            date_is_filesystem=filesystem_date,
            include_files=tuple(item["include_files"]) if "include_files" in item else None,
        ))
    return sorted(projects, key=lambda project: project.committed_at, reverse=True)
