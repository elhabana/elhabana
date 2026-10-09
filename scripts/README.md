# Profile graphics

Python 3.12+, standard library only. From the repository root:

```sh
python scripts/banner.py
python -m unittest discover -s scripts -p 'test_*.py'
```

`visuals.py` owns the palette. `banner.py` generates the dark/light header and
UN-CREDIBLES cover. `avatar.py` embeds four supplied poses in SYSTEM.VIEW and
swaps the expressions in an 18-second SVG SMIL loop. The PNGs in `assets/avatar`
are 420px copies of the supplied images. Both banner SVGs are self-contained,
so the avatar also appears when the README is rendered through an image proxy.
Static renderers show the neutral pose; PNG exports do not preserve animation.

`system-view.html` is the interactive version. Open it in a browser and press
**Activar sonido** to hear short synthesized chirps when the avatar opens its
mouth. The sound needs a click because browsers block unsolicited audio. The
GitHub profile README remains silent: GitHub renders its banner as an image and
does not run the JavaScript needed for audio. To share sound publicly, host
`system-view.html` together with `assets/avatar/` on a static web host.

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
