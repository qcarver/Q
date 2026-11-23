from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path

from .models import Project


def _age_fraction(
    project: Project,
    stale_years: float,
    minimum: float,
    fresh_hours: float,
) -> float:
    now = datetime.now(timezone.utc)
    committed = project.committed_at
    if committed.tzinfo is None:
        committed = committed.replace(tzinfo=timezone.utc)
    seconds = max(0.0, (now - committed.astimezone(timezone.utc)).total_seconds())
    seconds = max(0.0, seconds - fresh_hours * 60 * 60)
    fourteen_years = stale_years * 365.2425 * 24 * 60 * 60
    return max(minimum, 1.0 - seconds / fourteen_years)


def _glyph(project: Project, stale_years: float, minimum: float, fresh_hours: float) -> str:
    fraction = _age_fraction(project, stale_years, minimum, fresh_hours)
    green = fraction * 100
    label = f"{fraction:.0%} freshness"
    if project.date_is_filesystem:
        label += ", based on file modification time"
    return (
        f'<span class="age{" filesystem" if project.date_is_filesystem else ""}" '
        f'style="--green:{green:.2f}%" role="img" '
        f'aria-label="{html.escape(label)}"></span>'
    )


def render(
    projects: list[Project],
    settings: dict[str, object],
    q_git: dict[str, object],
    *,
    explicit_index: bool = False,
) -> str:
    limit = int(settings.get("commit_message_limit", 80))
    cards = []
    for project in projects:
        commit = project.commit[:7] if project.commit else "filesystem"
        message = (project.message or "No Git commit metadata")[:limit]
        date = project.committed_at.strftime("%Y-%m-%d")
        destination = f"{project.route}/index.html" if explicit_index else f"{project.route}/"
        cards.append(f'''<article class="project">
          {_glyph(project, float(settings.get("stale_years", 14)), float(settings.get("minimum_green", .14)), float(settings.get("fresh_hours", 4)))}
          <a class="card {html.escape(project.category)}" href="{html.escape(destination)}">
            <span class="name">{html.escape(project.name)}</span>
            <span class="summary">{html.escape(project.summary)}</span>
            <span class="commit">{date} · {html.escape(commit)} · {html.escape(message)}</span>
          </a>
        </article>''')
    q_commit = str(q_git.get("commit") or "uncommitted")[:7]
    q_message = str(q_git.get("message") or "Working tree prototype")[:limit]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(str(settings.get("title", "Überproject-Q")))}</title>
<style>
:root {{ font-family: ui-rounded,"Avenir Next",Avenir,system-ui,sans-serif; --ink:#17211c; --paper:rgba(250,249,240,.92); }}
* {{ box-sizing:border-box }} body {{ min-height:100vh;margin:0;color:var(--ink);background:repeating-linear-gradient(135deg,#416c58 0 18px,#365848 18px 36px); }}
main {{ width:min(920px,calc(100% - 2rem));margin:auto;padding:3rem 0 5rem }} header {{ margin-bottom:1.4rem;padding:1.8rem 2rem;border:2px solid #ffffffa6;border-radius:28px;background:var(--paper);box-shadow:0 18px 50px #0005;text-align:center }}
h1 {{ margin:0;font-size:clamp(2.2rem,8vw,4.8rem);line-height:.95;letter-spacing:-.055em }} .tagline {{ margin:.75rem 0;color:#4d6258;font-size:clamp(1rem,3vw,1.35rem) }} .q-commit,.commit {{ font-family:ui-monospace,monospace }} .q-commit {{ margin:0;color:#66746d;font-size:.78rem }}
.projects {{ display:grid;gap:.85rem }} .project {{ display:grid;grid-template-columns:48px 1fr;gap:.85rem;align-items:center }} .age {{ width:42px;aspect-ratio:1;border:2px solid #0d1712;border-radius:50%;background-color:#111;background-image:conic-gradient(from 0deg,#55c878 0 var(--green),#111 var(--green) 100%);box-shadow:0 3px 9px #0006;transform:scaleX(-1) }} .age.filesystem {{ outline:2px dashed #eee;outline-offset:2px }}
.card {{ display:block;padding:1rem 1.2rem;border:3px solid;border-radius:22px;color:var(--ink);box-shadow:0 8px 20px #0004;text-decoration:none;transition:.13s }} .card:hover,.card:focus-visible {{ transform:translateY(-2px);box-shadow:0 12px 26px #0005 }}
.public {{ border-color:#275b3b;background:#a8e2c2 }} .local {{ border-color:#222;background:#eee }} .name {{ display:block;margin-bottom:.28rem;font-size:1.18rem;font-weight:800 }} .summary {{ display:block;line-height:1.35 }} .commit {{ display:block;margin-top:.55rem;opacity:.68;font-size:.74rem }}
@media(max-width:560px) {{ main {{ width:min(100% - 1rem,920px);padding-top:.5rem }} header {{ border-radius:0 0 24px 24px }} .project {{ grid-template-columns:36px 1fr;gap:.5rem }} .age {{ width:34px }} }}
</style></head><body><main><header><h1>{html.escape(str(settings.get("title", "Überproject-Q")))}</h1><p class="tagline">{html.escape(str(settings.get("tagline", "")))}</p><p class="q-commit">{html.escape(q_message)} · {html.escape(q_commit)}</p></header>
<section class="projects" aria-label="Project websites">{''.join(cards)}</section></main></body></html>'''


def write_index(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
