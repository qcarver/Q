from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

from .copy_sites import copy_sites
from .discover import discover
from .git_metadata import read_git_metadata
from .render import render, write_index


def build(root: Path, target: str = "local") -> Path:
    if target not in {"local", "public"}:
        raise ValueError("target must be 'local' or 'public'")
    output = root / "build" / target
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    settings = tomllib.loads((root / "q.toml").read_text(encoding="utf-8"))
    projects = discover(root / "projects.toml", public=target == "public")
    # Local development routes point at the enrolled working trees so they do
    # not become stale between builds. Public artifacts remain isolated copies.
    copy_sites(projects, output, live_links=target == "local")
    write_index(
        output / "index.html",
        render(
            projects,
            settings,
            read_git_metadata(root),
            explicit_index=target == "local",
        ),
    )
    return output
