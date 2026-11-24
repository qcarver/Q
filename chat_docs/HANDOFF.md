# Überproject-Q Handoff

Continue from `/home/qcarver/Dev/Q` using medium reasoning unless the user requests otherwise.

## Objective

Build Überproject-Q as a static **web-project launchpad and multiplexer**. It should discover eligible project directories with a root `index.html`, generate a visually unified launch page, and fan out to their static sites through paths beneath one host. It will eventually produce two artifacts: a rigorously sanitized public GitHub Pages edition and a broader Granville LAN edition.

The authoritative requirements and preliminary architecture are in [`chat_docs/PDR.md`](PDR.md). Defer to that document for the gnat-ass details: classification precedence, colors, privacy boundary, metadata, age glyph, sorting, backgrounds, directory layout, build stages, and validation rules.

## Current state

- Q is an existing local Git repository with one old commit and no remote.
- The worktree already contained unrelated deletions and untracked backup/readme files before this work. Preserve them; do not clean, restore, or commit them without direction.
- `chat_docs/PDR.md` contains the agreed design.
- Root `index.html` is a hand-built visual sketch, not a generator output or final design.
- `HANDOFF.md` at the repository root is intended to be a symlink to this file.
- No generator, tests, manifests, submodules, deployment workflow, or server configuration has been implemented yet.

## Non-negotiable privacy rule

An omitted repository's identity must not occur anywhere in the public artifact, including HTML, JavaScript, CSS, JSON, comments, documentation, URLs, source maps, submodule declarations, image metadata, or hidden elements. Client-side hiding is not privacy. Filter before rendering or copying.

Do not put real private/local omitted-project names into tracked examples or tests. Use obviously fictional fixtures. Keep target-specific private metadata outside anything copied or published publicly.

## Recommended next implementation slice

Start with a small, test-driven local prototype:

1. Add the Python package skeleton and configuration schema proposed by the PDR.
2. Discover fixture directories containing root `index.html` files.
3. Extract local Git metadata without contacting or mutating remotes.
4. Classify only fictional test fixtures.
5. Generate a local launch page from normalized records.
6. Prove that an omitted fixture's unique sentinel never appears anywhere in a public build.
7. Keep publication and real submodule enrollment out of this first slice.

Before changing existing repository state, inspect `git status` and preserve all user-owned changes. Use `apply_patch` for file edits. Do not publish, add remotes, add real submodules, or modify `qcarver.github.io` without an explicit request.

## Visual sketch

Open [`visual-sketch.html`](visual-sketch.html) in a browser for the preserved disposable example of the intended hierarchy: header, freshness glyphs, rounded project cards, category treatments, and newest-first presentation. It deliberately uses fictional entries and contains no inventory of real omitted repositories. The repository-root [`index.html`](../index.html) now forwards local browser sessions to the generated launchpad in `build/local/`.

## Browser coordination

Wumpus_as_Web owns its existing Firefox session and remote-debugging port. Do not attach to, navigate, refresh, relaunch, or otherwise manipulate that session from Q work.

When Q needs interactive Firefox testing, launch a genuinely separate instance with a Q-specific profile, `--no-remote`, and a distinct debugger port. This keeps tabs, session restoration, and remote-control traffic isolated while testing in the same browser family. Wait for Wumpus_as_Web when the task specifically concerns its active browser state rather than competing for that session.

## Local route freshness

Each generated `build/local/<route>/index.html` is a lightweight Q-owned frame with a persistent back-to-Q arrow. Its `site/` entry is a live directory link to the enrolled project's configured web root. Local development therefore reflects the current working tree immediately, including changes newer than Git HEAD, without regenerating Q or modifying the project page. The public build deliberately copies each site beneath the same wrapper into an isolated snapshot and must be rebuilt and inspected before publication.

## Granville deployment

`python -m generator --target lan` creates a materialized `build/lan/` artifact containing every locally enrolled project. A project may declare `include_files` to restrict LAN copying to an explicit safe allowlist; Depot Manager uses this boundary so its inventory, local configuration, and repository sources do not enter Apache's document root. Deploy the completed artifact to `/var/www/html/`, never the live repository trees or the symlink-based development build.

Granville uses `scripts/deploy_granville.sh` to validate and synchronize the LAN artifact into Apache's document root. The tracked `deploy/granville/uberproject-q-granville.{service,timer}` user units refresh it every five minutes while qcarver's user manager is running. Enabling user lingering is an optional privileged follow-up if refreshes must continue with no qcarver login session; Apache continues serving the most recent artifact regardless.
