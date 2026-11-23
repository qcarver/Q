from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from generator.build import build
from generator.discover import discover
from generator.models import Project
from generator.render import _age_fraction


ROOT = Path(__file__).parents[1]


def test_public_projects_are_enrolled_and_newest_first():
    projects = discover(ROOT / "projects.toml", public=True)
    assert {project.id for project in projects} == {
        "Thesis", "Wumpus", "NatesClock",
    }
    assert projects == sorted(projects, key=lambda project: project.committed_at, reverse=True)


def test_routes_are_distinct_and_safe():
    projects = discover(ROOT / "projects.toml", public=True)
    routes = [project.route for project in projects]
    assert len(routes) == len(set(routes))
    assert all(".." not in Path(route).parts for route in routes)


def test_local_routes_are_live_links(tmp_path: Path):
    root = tmp_path / "q"
    root.mkdir()
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("first", encoding="utf-8")
    (root / "q.toml").write_text('title = "Q"\n', encoding="utf-8")
    (root / "projects.toml").write_text(f'''
[projects.live]
source = "{site}"
route = "live"
''', encoding="utf-8")

    output = build(root, "local")
    route = output / "live"
    site_link = route / "site"
    assert site_link.is_symlink()
    launchpad = (output / "index.html").read_text(encoding="utf-8")
    assert 'href="live/index.html"' in launchpad
    assert '<span class="age filesystem"' in launchpad
    assert 'background-color:#111' in launchpad
    assert '#55c878 0 var(--green)' in launchpad
    wrapper = (route / "index.html").read_text(encoding="utf-8")
    assert 'href="../index.html"' in wrapper
    assert 'aria-label="Back to Überproject-Q"' in wrapper
    assert 'src="site/index.html"' in wrapper
    assert (site_link / "index.html").read_text(encoding="utf-8") == "first"

    (site / "index.html").write_text("second", encoding="utf-8")
    assert (site_link / "index.html").read_text(encoding="utf-8") == "second"


def test_age_wheel_uses_four_hour_grace_fourteen_year_scale_and_floor(tmp_path: Path):
    def project_at(age: timedelta) -> Project:
        return Project(
            id="fixture", name="Fixture", source=tmp_path, web_root=tmp_path,
            route="fixture", summary="", include_publicly=False, category="local",
            commit="abcdef0", committed_at=datetime.now(timezone.utc) - age,
            message="Fixture", upstream=None,
        )

    assert _age_fraction(project_at(timedelta(hours=3)), 14, .14, 4) == 1.0
    four_years = _age_fraction(project_at(timedelta(days=4 * 365.2425)), 14, .14, 4)
    assert four_years == pytest.approx(1 - 4 / 14, abs=.001)
    assert _age_fraction(project_at(timedelta(days=20 * 365.2425)), 14, .14, 4) == .14
