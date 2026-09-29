# Profile graphics

Python 3.12+, standard library only. From the repository root:

```sh
python scripts/banner.py
python -m unittest discover -s scripts -p 'test_*.py'
```

`visuals.py` owns the palette and the SVG primitives. `banner.py` generates the
hero (`assets/banner-*.svg`), the UN-CREDIBLES cover (`assets/uncredibles-*.svg`)
and the open Selected Work slot (`assets/projects/reserved-*.svg`).

`motion.py` generates `assets/memes/dev-memes-*.svg`: an 18-second SMIL loop with
five original scenes about ordinary programming pain (it works on my machine,
compiling then "just a small change", one bug fixed and three created, a
NullReferenceException, Stack Overflow). Scenes are plain monospace text, small
windows and geometric faces — no JavaScript, no external references, no
copyrighted characters, no raster payload. Adding or editing a scene means
editing a `_scene_*` function in `motion.py` and the `SCENES` tuple.

## How the animation works

- Scene switching uses one `<animate attributeName="opacity">` per scene.
  `motion.fade_track()` builds the keyframes so neighbouring fades overlap and
  sum to 1: the banner never blinks through black, and the first and last values
  of every track match, so the loop is seamless.
- Everything runs through SMIL only. GitHub renders README images inside an
  `<img>`, where scripts never run, external files (fonts, images) are not
  fetched, and links inside the SVG are not clickable. So: system font stacks
  only, no `<image>`/base64, no `foreignObject`, and social links live in the
  README rather than inside the SVGs.
- The base `opacity` on each scene group is a fallback, not a value used in
  browsers: a renderer without SMIL shows scene 0 and hides the rest. PNG
  snapshots and static previews therefore look like a single frame, not a
  collage.
- `textLength` pins the width of the `$ git push origin main` line so the
  blinking cursor lands in the same place whatever monospace font is available.

## Assets

- Local banners use a `<picture>` element with dark and light variants and
  `width="100%"`, so they scale from phone to desktop.
- Stack icons: skillicons for Unity, C#, Blender, Photoshop and VS Code;
  DaVinci Resolve and CapCut use the local icons in `assets/icons/`
  (Simple Icons, CC0 distribution, recolored; CapCut artwork from UXWing,
  retained as-is). Brand marks belong to their owners.
- The hero, the covers and the banners are generated files. Edit the scripts,
  never the SVG output.

## GitHub stats

The stats section embeds three read-only widgets and nothing else: the activity
graph from `github-readme-activity-graph.vercel.app` and the languages and
overview cards from `github-readme-stats.vercel.app`. Both projects now ship
from Vercel after the old Heroku and Cyclic deployments were retired, and both
are community-hosted, so they can be rate limited. If a card ever stops loading,
the fix is to self-host (or generate the SVGs with an Action) rather than to add
another badge.

Colors are passed per theme: transparent background (`bg_color=00000000`),
`hide_border=true`, cold grey-blue titles and no rank circle, so the cards read
as activity instead of decoration.
