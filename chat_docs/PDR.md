# Überproject-Q: Preliminary Design Requirements

## 1. Purpose

Überproject-Q is a static web-project launchpad that:

- Discovers eligible project websites.
- Generates a common, visually informative home page.
- Publishes those websites beneath one GitHub Pages domain.
- Produces essentially the same site for Granville to serve on the home network.
- Maintains awareness of each project's Git and upstream status.

It is initially a **web-project launchpad and multiplexer**, not a catalog of every repository. If every project eventually acquires a website, it naturally becomes a universal entry point for those projects.

## 2. Eligible projects

A directory is eligible when it contains an `index.html` at its root.

For the first version:

- A Git repository without a root `index.html` is omitted.
- A non-Git directory with a root `index.html` is included locally.
- Public Git-backed sites may be included in the GitHub build.
- Private and local-only projects must never be named or copied into the public artifact.
- A project may be explicitly excluded regardless of automatic discovery.
- Only static browser-compatible sites are supported initially.

The generator must inspect the actual directory, not merely trust a manually maintained list.

## 3. Deployment targets

### Public edition

Published at:

```text
https://qcarver.github.io/
```

Project sites receive clean directory routes:

```text
https://qcarver.github.io/<project-name>/
```

Only public-safe projects and assets enter this artifact.

### Granville edition

Served approximately as:

```text
http://granville/
http://granville/index.html
http://<granville-ip>/
```

It can eventually contain:

- Public GitHub projects.
- Private GitHub projects.
- Collaborative projects visible to authorized users.
- Local Git projects.
- Non-Git web directories.

LAN name resolution is a deployment concern separate from Q's generator.

## 4. Public/private security rule

The generator creates separate artifacts:

```text
build/public/
build/local/
```

Privacy filtering occurs **before files are copied or HTML is generated**.

The public artifact must contain no:

- Private project names.
- Private repository URLs.
- Private descriptions.
- Private submodule declarations.
- Private images.
- Hidden HTML elements containing private metadata.
- JavaScript data structures containing private metadata.

Browser-side rendering may construct the visible page, but it operates only on metadata already authorized for that build.

Authenticated, per-collaborator GitHub access is deferred. GitHub Pages does not automatically give the page access to repositories the visitor can see on github.com.

## 5. Project classifications

Each project has one primary presentation category:

| Category | Meaning | Presentation |
|---|---|---|
| `untracked` | Directory has `index.html` but is not inside a Git repository | Piss-yellow fill, red line |
| `local` | Git repository has no GitHub upstream | Black and white |
| `private` | Private GitHub repository | Flesh tones, chestnut/hair-colored lines |
| `collaborative` | Explicitly recognized collaborative repository | Robin's-egg blue, royal-blue lines |
| `public` | Public repository owned by Quinn | Mint/spearmint fill, forest-green and bark-brown lines |
| `fork` | Fork originating in another owner's project | Pale khaki, darkest-brown lines |

Proposed classification precedence:

```text
explicit override
    → untracked
    → fork
    → collaborative
    → GitHub private
    → GitHub public
    → local Git
```

This prevents a public fork from being styled merely as public and allows exceptional collaboration status to be supplied by private, target-specific configuration.

## 6. Project metadata

Each discovered project produces a normalized record resembling:

```yaml
id: depotMgr
name: Depot Manager
directory: submodules/depotMgr
route: depotMgr/
has_index: true

git:
  is_repository: true
  head: 1a2b3c4
  committed_at: 2026-11-20T14:22:00-05:00
  message: Improve bin recognition
  upstream: https://github.com/qcarver/depotMgr.git

github:
  owner: qcarver
  visibility: public
  fork: false

presentation:
  category: public
  summary: Uses ArUco fiducials to identify the locations of depot bins.
  include_publicly: true
  background_images: []
```

Most fields will be discovered. A small manifest supplies overrides, summaries, privacy decisions, and collaboration classifications.

## 7. Home-page presentation

The header contains:

- `Überproject-Q`.
- "A Web-Project Launchpad and Multiplexer".
- Q's most recent commit message, capped to a configured length.
- Q's seven-character commit hash.

Below it, projects appear in descending freshness order.

Each project entry contains:

- Commit-age glyph.
- Rounded rectangular launch button.
- Friendly project name.
- Summary capped at 40 words.
- Latest commit date.
- Capped latest commit message.
- Seven-character commit hash.
- Visual category treatment.

Selecting a project navigates to:

```text
/<project-route>/
```

It does not need an iframe. The project becomes the loaded page.

## 8. Commit-age glyph

The glyph is a compact pie:

- Begins at twelve o'clock.
- Fills counterclockwise.
- Green represents freshness.
- Black represents age.
- A commit no more than four hours old: 100% green.
- After four hours, freshness decreases linearly on a fourteen-year scale.
- Green never falls below 14%.

Initial linear calculation:

```text
scaled_age = max(0, age_in_seconds - four_hours)
green_fraction = max(0.14, 1.00 - scaled_age / fourteen_years)
```

An SVG is preferable to a CSS pie because SVG gives precise control over counterclockwise direction and accessible labeling.

For non-Git directories:

- The glyph uses the `index.html` modification time provisionally.
- It is visually marked as filesystem-derived rather than commit-derived.
- No synthetic commit hash or message is invented.

## 9. Random tiled background

On every home-page load:

1. JavaScript selects one entry from an approved background-image manifest.
2. The image becomes a tiled page background.
3. A readability overlay keeps text and controls legible.

Security and size constraints:

- The public manifest contains public images only.
- The local manifest may contain locally authorized images.
- Q should not indiscriminately copy every image from every repository.
- Discovery can propose candidates, but a manifest should approve the usable set.
- Each image records its source project for attribution and maintenance.

A deterministic query option would help debugging:

```text
/?background=depotMgr-02
```

## 10. Submodules and website copying

Q tracks approved Git projects as submodules where practical:

```text
projects/
├── depotMgr/
├── pentacubes_c3/
└── ...
```

The build does not publish `.git`, `.gitmodules`, or Git internals.

For each eligible submodule, it copies the static website into:

```text
build/public/<route>/
```

A root `index.html` commonly depends on CSS, JavaScript, images, and subdirectories. Consequently, Q must copy the required website tree, not just `index.html`.

Initial safe rule for public repositories:

- Copy the repository working tree.
- Exclude `.git`, development caches, build artifacts, secrets, and configured exclusions.
- Permit a project-specific `web_root` override later.

Because public repository source is already public, copying it is not a new confidentiality exposure, but accidental secrets and oversized files still require checks.

For local/private builds, inclusion must be explicit because copying an entire working tree could expose unrelated material to the LAN.

## 11. Preliminary repository design

```text
Q/
├── README.md
├── pyproject.toml
├── q.toml
├── projects.toml
├── generator/
│   ├── __init__.py
│   ├── discover.py
│   ├── git_metadata.py
│   ├── github_metadata.py
│   ├── classify.py
│   ├── privacy.py
│   ├── copy_sites.py
│   ├── render.py
│   └── validate.py
├── templates/
│   └── index.html.j2
├── static/
│   ├── q.css
│   ├── q.js
│   └── icons/
├── projects/
│   └── <Git submodules>
├── local-sites.toml
├── tests/
│   ├── test_classification.py
│   ├── test_privacy.py
│   ├── test_sorting.py
│   └── test_routes.py
├── build/
│   ├── public/
│   └── local/
└── .github/
    └── workflows/
        └── build.yml
```

Python is a sensible generator language here because this is metadata inspection and file generation, while the resulting site remains plain HTML, CSS, and JavaScript.

### Configuration split

`q.toml` contains general behavior:

```toml
title = "Überproject-Q"
tagline = "A Web-Project Launchpad and Multiplexer"
commit_message_limit = 80
project_summary_words = 40
stale_years = 14
fresh_hours = 4
minimum_green = 0.14
```

`projects.toml` contains public-safe metadata and explicit overrides:

```toml
[projects.FitCsMastersThesis]
route = "FitCsMastersThesis"
summary = "Demonstrates context-free visualization of streaming object data."
```

Omitted-project names, paths, URLs, collaborators, and GitHub handles must not appear in public configuration, generated metadata, documentation shipped with the public artifact, comments, or client-side code. Target-specific private configuration may classify them only after their identities and permissions have been verified.

Local-only paths should live in a file excluded from the public repository, such as `local-sites.toml`. Generated public output must not depend on that file.

## 12. Build pipeline

```text
Discover directories and submodules
        ↓
Read Git remotes and commit metadata
        ↓
Query or inspect GitHub visibility where necessary
        ↓
Apply explicit project overrides
        ↓
Classify projects
        ↓
Reject directories lacking root index.html
        ↓
Apply target-specific privacy filter
        ↓
Copy static website trees
        ↓
Generate target-specific metadata
        ↓
Render launchpad
        ↓
Run leak and route validation
        ↓
Produce public/ or local/ artifact
```

### Required public-build validation

The public build fails if:

- A selected project is not explicitly public-safe.
- A private/local project name occurs in generated output.
- A project route escapes its output directory.
- A copied file resembles a credential or private key.
- A project lacks `index.html`.
- Two projects claim the same route.
- A submodule was not initialized.
- Any generated link points at a missing local page.

## 13. Publishing design

The recommended roles are:

- **Q:** Private-capable generator, manifests, and submodule coordinator.
- **qcarver.github.io:** Generated public artifact and existing public domain.
- **Granville document root:** Generated local artifact.

Publishing the public artifact into `qcarver.github.io` will require either:

- A credential allowing Q's workflow to update that repository; or
- A workflow inside `qcarver.github.io` that fetches and builds Q's public-safe source.

For the first implementation, local generation followed by an inspected, deliberate publication is safer. Cross-repository deployment can be automated after the artifact and privacy checks are trustworthy.

## 14. Proposed implementation stages

1. **Foundation**
   - Cleanly initialize Q.
   - Add requirements and configuration schema.
   - Preserve the old Q material without treating it as the new application.
2. **Local prototype**
   - Discover repositories and standalone web directories.
   - Detect root `index.html`.
   - Read commit and upstream metadata.
   - Generate a working launchpad locally.
3. **Presentation**
   - Implement classifications, colors, project cards, sorting, glyphs, and random tiled backgrounds.
4. **Public privacy boundary**
   - Generate distinct public and local artifacts.
   - Add leak checks and explicit publication approval.
5. **GitHub publication**
   - Preserve the thesis site under `/FitCsMastersThesis/`.
   - Make Q the `qcarver.github.io` root.
   - Publish approved project routes.
6. **Granville**
   - Install the local artifact.
   - Configure the web server.
   - Establish reliable `granville` LAN resolution.
7. **Later authenticated collaboration**
   - Investigate genuine GitHub login and permission-aware delivery for authorized collaborators.
   - Do not expose omitted repositories through ordinary public Pages meanwhile.

This is sufficiently defined to begin the foundation and discovery prototype without prematurely locking down the final visual design.
