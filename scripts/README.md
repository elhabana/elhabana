# Profile graphics

Python 3.12+, standard library only. From the repository root:

```sh
python scripts/banner.py
python -m unittest discover -s scripts -p 'test_*.py'
```

`visuals.py` owns the palette and `dots_d`, which draws particles as round-capped
zero-length strokes inside one `<path>` per size and brightness, with relative
moves: a fraction of the bytes of one `<circle>` per particle. `banner.py`
generates everything: the dark/light header, the UN-CREDIBLES cover and the
project cards.

`avatar.py` reads the four supplied poses in `assets/avatar`
with a small standard-library PNG decoder and turns them into a particle bust
(about 5,000 dots, accent colour, brightness as halftone; inverted on the light
theme). Every pose shares the same particle positions, so only the eyes and the
mouth change. They are drawn twice, as an open and a closed layer, and one SMIL
animation per layer swaps them: the eyes blink on an 18-second loop and the
mouth reads along with the live terminal, flapping while its letters are typed.
After the boot screen the particles fly in as swarms and a few keep shimmering.

The header opens with `invaders.py`: an 8-bit Space Invaders round simulated in
Python (player, shots, hits, bombs, score) and baked into SMIL. The player is hit,
GAME OVER flashes and the screen switches off like an old CRT. Then `boot.py`
plays a short terminal boot sequence, glitches out and the panels power on from
a centre line (about 10.5 s in total). DEVELOPER.PROFILE is a live terminal that
types `whoami` and `cat now_building.txt` in a 10-second loop; each output first
appears as noise and decrypts letter by letter while the avatar reads it.

`heroes.py` builds the UN-CREDIBLES cover from the team's concept sketches:
standing, punch, hit reaction, backflip, superhero landing and a selfie. Their particles
were extracted once (line art as bright dots, the body filled in as a plain
suit) and are stored in `assets/uncredibles/particles.json`; the drawings are not
kept in the repo. The in-between frames are particle morphs from the standing
pose to each drawing. Four identical heroes brawl in two duels on a 6-second
loop: wind-up and punch; the victim staggers, or takes the hit, backflips, lands
like a hero and walks back, while the puncher turns its back and takes a selfie
with it flying behind (a flash at the top of the flip). Bursts of particles mark
each impact and landing. The heroes are drawn at about half size, so their
particles use whole-unit coordinates (at most 0.25 px off on screen).

Every overlay is hidden or settled by default, so static renderers show the
finished banner with the whole terminal session and the heroes in their neutral
pose; PNG exports do not preserve animation.

`cards.py` draws the project cards with the cover's size and layout (1180x300,
title top left, a tag top right); the README stacks them under the cover and
links each one to its project on The Rookies. `skater.py` (Roller Hunter): the
hero of the trailer's opening comic skates in, hits a demon with a slingshot
stone (it bursts into particles), kickflips over the second one hitting it from the air, lands in a puff of dust
and skates off; the demons respawn. `duel.py` (FPS Online): two soldiers behind
cover trade hitscan shots with recoil, muzzle flash, tracers, casings and camera
shake; a kill dissolves the victim into particles that converge again to respawn
it, and a score sits in the header. Their particles were extracted once from
frames of the videos (the comic's line art, with the body filled in as a plain
suit; the soldier, too dark to segment, traced by hand over a frame) into
`assets/rollerhunter/` and `assets/fpsonline/`; the videos are not kept in the repo.

`system-view.html` is the interactive version. Open it in a browser and press
**Activar sonido** to hear short synthesized chirps when the avatar opens its
mouth. The sound needs a click because browsers block unsolicited audio. The
GitHub profile README remains silent: GitHub renders its banner as an image and
does not run the JavaScript needed for audio. To share sound publicly, host
`system-view.html` together with `assets/avatar/` on a static web host.

Regeneration is local only: no API, token or workflow is involved. The only
external service the README uses is Shields, for the badges.

The overall two-panel composition was studied from
https://github.com/emmi-lili/emmi-lili. No personal content, portrait, branding
or generator code was copied.
