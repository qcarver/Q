from pathlib import Path

from generator.build import build


def test_omitted_project_sentinel_never_enters_public_build(tmp_path: Path):
    root = tmp_path / "q"
    root.mkdir()
    (root / "q.toml").write_text('title = "Q"\n', encoding="utf-8")
    public_site = tmp_path / "public-site"
    public_site.mkdir()
    (public_site / "index.html").write_text("PUBLIC", encoding="utf-8")
    omitted_site = tmp_path / "omitted-site"
    omitted_site.mkdir()
    sentinel = "FICTIONAL_OMITTED_SENTINEL_7B1C"
    (omitted_site / "index.html").write_text(sentinel, encoding="utf-8")
    (root / "projects.toml").write_text(f'''
[projects.public_fixture]
source = "{public_site}"
route = "public-fixture"
include_publicly = true

[projects.omitted_fixture]
source = "{omitted_site}"
route = "omitted-fixture"
summary = "{sentinel}"
include_publicly = false
''', encoding="utf-8")

    output = build(root, "public")
    artifact = b"".join(path.read_bytes() for path in output.rglob("*") if path.is_file())
    assert sentinel.encode() not in artifact
    assert not (output / "omitted-fixture").exists()
