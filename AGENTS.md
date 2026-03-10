# AGENTS.md

## Purpose
`stewart-filmscreen-homeassistant` is the Home Assistant integration for Stewart Filmscreen controllers.

## Workflow
- Use `uv` for local commands.
- Run repo-local lint and targeted tests before pushing.
- Keep service registration and unload behavior deterministic across startup and reload.

## Lifecycle Contract
- Stewart is effectively always on; normal operation should not invent a shutdown lifecycle.
- Main cover entities stay available while the controller is reachable.
- Use `unavailable` only when the controller is truly unreachable or powered off.
- Domain services must register reliably on startup and reload.

## Commits
- Use conventional commits for releasable changes: `fix: ...` or `feat: ...`.

## Releases
1. Merge normal conventional commits to `master`.
2. Let `release-please` open or update the release PR.
3. Do not manually edit version files or changelogs outside the Release Please PR.
4. Do not manually create tags or GitHub releases.
5. Merge the Release Please PR to publish.
