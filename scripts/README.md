# Profile graphics

Python 3.12+, standard library only. From the repository root:

```sh
python scripts/banner.py
python -m unittest discover -s scripts -p 'test_*.py'
```

`visuals.py` owns the palette. `banner.py` generates the dark/light header and
UN-CREDIBLES cover. `avatar.py` reads the four supplied poses in `assets/avatar`
with a small standard-library PNG decoder and turns them into a particle bust
(about 5,000 dots, accent colour, brightness as halftone; inverted on the light
theme). Every pose shares the same particle positions, so only the eye and mouth
particles animate: the eyes blink on an 18-second SMIL loop and the mouth reads
along with the live terminal, flapping while its letters are typed. After the
boot screen the particles fly in as swarms and a few keep shimmering.

The header opens with `invaders.py`: an 8-bit Space Invaders round simulated in
Python (player, shots, hits, bombs, score) and baked into SMIL. The player is hit,
GAME OVER flashes and the screen switches off like an old CRT. Then `boot.py`
plays a short terminal boot sequence, glitches out and the panels power on from
a centre line (about 10.5 s in total). DEVELOPER.PROFILE is a live terminal that
types `whoami` and `cat now_building.txt` in a 10-second loop; each output first
appears as noise and decrypts letter by letter while the avatar reads it.

`heroes.py` builds the UN-CREDIBLES cover from the team's concept sketches:
standing, punch, hit reaction, backflip and superhero landing. Their particles
were extracted once (line art as bright dots, the body filled in as a plain
suit) and are stored in `assets/uncredibles/particles.json`; the drawings are not
kept in the repo. The in-between frames are particle morphs from the standing
pose to each drawing. Four identical heroes brawl in two duels on a 6-second
loop: wind-up and punch; the victim staggers, or takes the hit, backflips, lands
like a hero and walks back. Bursts of particles mark each impact and landing. Every overlay is hidden or settled by default, so static
renderers show the finished banner with the whole terminal session.
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

The README no longer shows the stack. The Resolve and CapCut icons are still in
`assets/icons` but unused:

- DaVinci Resolve: https://cdn.simpleicons.org/davinciresolve (Simple Icons,
  CC0 distribution; recolored and framed for readability).
- CapCut: https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/capcut-icon.svg
  (UXWing; retained original artwork). Brand marks belong to their owners.

External README services: Shields badges.
Core personal details are also readable text.
Social destinations were read directly from https://github.com/elhabana:
YouTube @elhabana, Instagram elhabana, Twitch elhabanaaa, Kick elhabanaa.

The overall two-panel composition was studied from
https://github.com/emmi-lili/emmi-lili. No personal content, portrait, branding
or generator code was copied.
