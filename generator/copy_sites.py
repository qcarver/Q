from __future__ import annotations

import html
import shutil
from pathlib import Path

from .models import Project


IGNORED_NAMES = {
    ".git", ".github", ".pytest_cache", "__pycache__", "build", "node_modules",
    "target", ".venv", "venv", ".env",
}


def _write_wrapper(project: Project, output: Path) -> None:
    title = html.escape(project.name)
    output.joinpath("index.html").write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · Überproject-Q</title>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ width: 100%; height: 100%; margin: 0; overflow: hidden; }}
    body {{ display: flex; flex-direction: column; background: #17211c; }}
    .q-bar {{
      z-index: 10; display: flex; flex: 0 0 48px; align-items: center;
      padding: 6px 10px; border-bottom: 1px solid #ffffff3d;
      background: #17211cf2; box-shadow: 0 2px 10px #0007;
    }}
    .q-back {{
      display: grid; width: 58px; height: 34px; place-items: center;
      padding-left: 8px; color: #102019; background: #a8e2c2;
      clip-path: polygon(0 50%, 15px 0, 100% 0, 100% 100%, 15px 100%);
      font: 900 19px/1 ui-rounded, "Avenir Next", system-ui, sans-serif;
      text-decoration: none; filter: drop-shadow(0 2px 2px #0008);
    }}
    .q-back:hover, .q-back:focus-visible {{ background: #d7f6e4; outline: none; }}
    iframe {{ display: block; flex: 1 1 auto; width: 100%; min-height: 0; border: 0; background: white; }}
  </style>
</head>
<body>
  <nav class="q-bar" aria-label="Überproject-Q navigation">
    <a class="q-back" href="../index.html" target="_top" aria-label="Back to Überproject-Q" title="Back to Überproject-Q">Q</a>
  </nav>
  <iframe src="site/index.html" title="{title}"></iframe>
</body>
</html>
''', encoding="utf-8")


def copy_sites(projects: list[Project], destination: Path, *, live_links: bool = False) -> None:
    for project in projects:
        route = Path(project.route)
        if route.is_absolute() or ".." in route.parts:
            raise ValueError(f"{project.id}: unsafe route {project.route!r}")
        output = destination / route
        output.mkdir(parents=True)
        site = output / "site"
        if live_links:
            site.symlink_to(project.web_root, target_is_directory=True)
        else:
            shutil.copytree(
                project.web_root,
                site,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(*IGNORED_NAMES, "*.pyc"),
            )
        _write_wrapper(project, output)
