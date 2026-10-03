# Profile graphics

Python 3.12+, standard library only. From the repository root:

```sh
python scripts/banner.py
python -m unittest discover -s scripts -p 'test_*.py'
```

`visuals.py` owns the palette. `banner.py` generates the dark/light header and
UN-CREDIBLES cover. `motion.py` samples original line-art contours from
`assets/memes/contours.json` into 1,200 particles and animates an 18-second SVG
SMIL loop: Surprised Pikachu, Trollface and This is fine. The contour drawings
are original interpretations, not extracted images. Edit those paths and captions
to change the memes. The loop needs no JavaScript or external service. Static
renderers show its first frame; PNG exports do not preserve the animation.

Signals, telemetry, their data and generators, and the Actions workflow were
removed at the user's request. Banner regeneration is now local only. No API,
token, commit or push is involved.

The stack uses VS Code. Resolve and CapCut have local app icons:

- DaVinci Resolve: https://cdn.simpleicons.org/davinciresolve (Simple Icons,
  CC0 distribution; recolored and framed for readability).
- CapCut: https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/capcut-icon.svg
  (UXWing; retained original artwork). Brand marks belong to their owners.

External README services: readme-typing-svg, Shields badges and skillicons.
Core personal details are also readable text.
Social destinations were read directly from https://github.com/elhabana:
YouTube @elhabana, Instagram elhabana, Twitch elhabanaaa, Kick elhabanaa.

The overall two-panel composition was studied from
https://github.com/emmi-lili/emmi-lili. No personal content, portrait, branding
or generator code was copied.
