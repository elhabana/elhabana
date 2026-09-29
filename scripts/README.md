# Profile graphics

Python 3.12+, standard library only. From the repository root:

```sh
python scripts/banner.py
python scripts/radar.py
python scripts/cards.py
python -m unittest discover -s scripts -p 'test_*.py'
```

`visuals.py` owns the palette. `banner.py` generates the banner and project cover.
`radar.py` reads `assets/data/game-skills.json` and `creative-skills.json`.
Their 0–100 values are illustrative editorial emphasis, not proficiency ratings.
Game emphasis follows the brief; creative axes start equal. Edit them freely.

`cards.py` paginates GitHub's public owned repositories, excludes forks and
private repos, and includes archived work. It sums stars and forks received,
then GitHub-reported language bytes across that same set. Every language counts;
more than six are grouped into a true `Other` sum. Repository language history
does not represent the current stack. No commits or contributions are inferred.
Unavailable metrics are omitted. Actual zeros stay zero. Empty language data
shows an explicit empty state. API failures abort before overwriting good data.

The dated snapshot is `assets/data/github.json`. Re-render without network or
changing the original date using `python scripts/cards.py --offline`.
`GITHUB_TOKEN` is optional locally and supplied by Actions. Never store tokens
in source, JSON or command arguments. No private data is requested.

## Refresh workflow

`.github/workflows/update-profile.yml` runs Mondays at 07:23 UTC, on manual
dispatch, and changes to generators or radar data. It uses read-only contents
permission and uploads a `profile-assets` artifact for review. It does **not**
commit or push. Once the workflow is published, download the artifact and copy
its contents into `assets/` to review and publish a refresh. The profile displays
the last published snapshot, not the latest workflow artifact. No PAT is needed.

## Presentation

Major graphics are local SVGs with dark/light `<picture>` selection. External
services are typing (readme-typing-svg), badges (Shields), icons (skillicons) and
views (Komarev). Views count third-party image requests, not verified unique
visitors. Personal details remain in text or alt descriptions if services fail.
Add social links only after verifying them. Project covers are graphic concepts,
not gameplay screenshots. No feature is claimed to be finished.

The radar table intentionally stays 50/50 like the reference. Text scales down
on narrow screens; alt descriptions retain all axes. The About section repeats
essential banner information at normal reading size.

## Reference study

https://github.com/emmi-lili/emmi-lili uses a 1180×610 two-panel banner,
typing, socials, stack, JSON-driven radars and generated statistics. Its banner
uses portrait/logo particle morphs; cards use REST and optional GraphQL; workflows
commit regenerated graphics and use another service for languages. This original
implementation uses simple editor geometry and the Python standard library.
No portrait, personal content, scoring data or source code was copied.

GitHub API semantics:
https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user
https://docs.github.com/en/rest/repos/repos#list-repository-languages
