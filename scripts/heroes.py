"""UN-CREDIBLES cover: four identical particle heroes brawling in two duels.

The hero comes from two of the team's concept sketches, a side view and a
punch. Their particles were extracted once (line art as bright dots, the body
below the neck filled as a plain suit) and live in assets/uncredibles/particles.json;
the drawings themselves are not kept in the repo. The in-between frames of the
punch are a particle morph between the two poses.
"""
import json
import math
import random
from functools import lru_cache

from visuals import ASSETS

STEP = 6            # particle spacing in source pixels, as extracted
NECKS = {'hero': 178, 'punch': 128}  # source row where the head ends and the suit starts
FRAMES = 5          # idle, three in-betweens, punch
BODY_ROWS = 36      # the bodies are matched in this many rows, whatever their height
HEIGHT = 220        # hero height in the cover
GROUND = 276
LOOP = 6            # seconds: one round of the brawl
DT = .05
# x of each hero's feet and the way it faces (+1 right, -1 left): two duels
HEROES = ((250, 1), (400, -1), (780, 1), (930, -1))
# (time, attacker, victim, big): a big hit sends the victim flying
HITS = ((.5, 0, 1, False), (1.1, 3, 2, False), (1.9, 1, 0, False),
        (2.6, 2, 3, False), (3.4, 0, 1, True), (4.2, 3, 2, True))


@lru_cache(maxsize=None)
def particles(name):
    """[(x, y, radius, opacity)] in source pixels of one drawing, with its size."""
    pose = json.loads((ASSETS / 'uncredibles' / 'particles.json').read_text(encoding='utf-8'))[name]
    return [tuple(d) for d in pose['dots']], pose['width'], pose['height']

def anchor(dots, neck):
    """Head centre x and ground y: the two drawings are aligned on these."""
    head = [x for x, y, _, _ in dots if y <= neck]
    return (min(head) + max(head)) / 2, max(y for _, y, _, _ in dots)

def by_rows(a, b, height):
    """Pair two particle sets row by row, left to right inside each row."""
    def rows(dots):
        top, out = min(d[1] for d in dots), {}
        for d in dots:
            out.setdefault(int((d[1] - top) // height), []).append(d)
        return {k: sorted(v) for k, v in out.items()}
    ra, rb, pairs = rows(a), rows(b), []
    for k in sorted(set(ra) | set(rb)):
        x = ra.get(k) or ra[min(ra, key=lambda j: abs(j - k))]
        y = rb.get(k) or rb[min(rb, key=lambda j: abs(j - k))]
        m = max(len(x), len(y))
        pairs += [(x[i * len(x) // m], y[i * len(y) // m]) for i in range(m)]
    return pairs

@lru_cache(maxsize=None)
def frames():
    """FRAMES particle sets from idle to punch, in the idle drawing's pixels.
    Head pairs with head (so the face keeps its shape) and body with body."""
    idle, punch = particles('hero'), particles('punch')
    (ix, iy), (px, py) = anchor(idle[0], NECKS['hero']), anchor(punch[0], NECKS['punch'])
    moved = [(x - px + ix, y - py + iy, r, o) for x, y, r, o in punch[0]]
    neck = NECKS['punch'] - py + iy
    pairs = by_rows([d for d in idle[0] if d[1] <= NECKS['hero']], [d for d in moved if d[1] <= neck], STEP)
    # bodies have different heights (the punch is a crouch): match them in BODY_ROWS rows
    a, b = [d for d in idle[0] if d[1] > NECKS['hero']], [d for d in moved if d[1] > neck]
    at, bt = min(d[1] for d in a), min(d[1] for d in b)
    sa, sb = (max(d[1] for d in a) - at) / BODY_ROWS, (max(d[1] for d in b) - bt) / BODY_ROWS
    squash = lambda dots, top, step: [(x, (y - top) / step, r, o) for x, y, r, o in dots]
    for u, v in by_rows(squash(a, at, sa), squash(b, bt, sb), 1):
        pairs.append(((u[0], at + u[1] * sa, u[2], u[3]), (v[0], bt + v[1] * sb, v[2], v[3])))
    out = []
    for f in range(FRAMES):
        t = f / (FRAMES - 1)
        e = t * t * (3 - 2 * t)
        out.append([tuple(round(p + (q - p) * e, 1) for p, q in zip(u, v)) for u, v in pairs])
    return out, idle[1], idle[2]

def frame_at(hero, t):
    """Which punch frame a hero shows: wind up, hit, hold, pull back."""
    steps = ((-.2, 1), (-.16, 2), (-.12, 3), (-.08, 4), (.15, 3), (.2, 2), (.25, 1), (.3, 0))
    for when, attacker, _, _ in HITS:
        if attacker == hero and when - .2 <= t < when + .3:
            return [f for offset, f in steps if t - when >= offset - 1e-9][-1]
    return 0

def ramp(t, points):
    """Piecewise-linear value at t from [(time, value)]; 0 outside."""
    if t <= points[0][0] or t >= points[-1][0]:
        return 0
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return 0

def pose(hero, t):
    """dx, dy, angle of one hero at time t: idle bob plus every hit it takes part in."""
    facing = HEROES[hero][1]
    dx = dy = angle = 0
    dy += 2.5 * math.sin(2 * math.pi * (t / 1.2 + hero * .3))
    for when, attacker, victim, big in HITS:
        if hero == attacker:
            dx += facing * ramp(t, [(when - .2, 0), (when - .08, 42), (when + .15, 42), (when + .4, 0)])
        if hero == victim and not big:
            dx -= facing * ramp(t, [(when, 0), (when + .12, 46), (when + .7, 0)])
            angle -= facing * ramp(t, [(when, 0), (when + .12, 16), (when + .6, 0)])
        if hero == victim and big:
            dx -= facing * ramp(t, [(when, 0), (when + .35, 80), (when + .7, 95), (when + .9, 95), (when + 1.6, 0)])
            dy -= ramp(t, [(when, 0), (when + .35, 70), (when + .7, 0)])
            angle -= facing * ramp(t, [(when, 0), (when + .35, 200), (when + .7, 360)])
    return round(dx, 1), round(dy, 1), round(angle, 1)

def track(hero):
    times = [round(i * DT, 2) for i in range(int(LOOP / DT) + 1)]
    poses, turned = [], 0
    for t in times:
        dx, dy, angle = pose(hero, t)
        # after a full flip the angle snaps back to 0; keep it continuous (360 looks the same)
        while poses and angle + turned - poses[-1][2] > 180:
            turned -= 360
        while poses and angle + turned - poses[-1][2] < -180:
            turned += 360
        poses.append((dx, dy, round(angle + turned, 1)))
    keys = ';'.join(f'{t / LOOP:.4f}' for t in times)
    moves = ';'.join(f'{dx} {dy}' for dx, dy, _ in poses)
    x = HEROES[hero][0]
    turns = ';'.join(f'{a} {x} {GROUND - HEIGHT * .45:.0f}' for _, _, a in poses)
    return keys, moves, turns

def burst(when, x, y, ink):
    """A few particles fly out of the impact point."""
    rnd, out = random.Random(int(when * 100)), []
    k = lambda t: f'{min(t, LOOP) / LOOP:.4f}'
    for _ in range(12):
        angle, reach = rnd.uniform(0, 2 * math.pi), rnd.uniform(18, 46)
        ex, ey = round(math.cos(angle) * reach), round(math.sin(angle) * reach)
        out.append(f'<circle cx="{x}" cy="{y}" r="{rnd.uniform(1.2, 2.4):.1f}" fill="{ink}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k(when)};{k(when + .05)};{k(when + .4)};1" '
                   f'dur="{LOOP}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{ex} {ey};{ex} {ey}" '
                   f'keyTimes="0;{k(when)};{k(when + .4)};1" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
    return out

def visibility(hero, f):
    """Discrete opacity schedule of one frame for one hero over the loop."""
    keys, values = [], []
    for i in range(int(LOOP / .02)):
        t = round(i * .02, 2)
        v = int(frame_at(hero, t) == f)
        if not values or v != values[-1]:
            keys.append(f'{t / LOOP:.4f}')
            values.append(str(v))
    return (f'<animate attributeName="opacity" values="{";".join(values)}" keyTimes="{";".join(keys)}" '
            f'dur="{LOOP}s" calcMode="discrete" repeatCount="indefinite"/>')

def brawl(c):
    sets, w, h = frames()
    scale = HEIGHT / h
    defs = ''.join(f'<g id="hero-f{f}">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill-opacity="{o}"/>' for x, y, r, o in dots) + '</g>'
                   for f, dots in enumerate(sets))
    parts = [f'<defs>{defs}</defs>',
             f'<line x1="40" y1="{GROUND + 2}" x2="1140" y2="{GROUND + 2}" stroke="{c["line"]}" stroke-dasharray="2 6"/>']
    for i, (x, facing) in enumerate(HEROES):
        keys, moves, turns = track(i)
        # the sketches face left; mirror them for heroes facing right
        place = f'translate({x} {GROUND}) scale({-facing * scale:.4f} {scale:.4f}) translate({-w / 2:.0f} {-h})'
        uses = ''
        for f in range(FRAMES):
            hidden = '' if f == 0 else ' opacity="0"'
            uses += f'<use href="#hero-f{f}" transform="{place}"{hidden}>{visibility(i, f)}</use>'
        parts.append(f'<ellipse cx="{x}" cy="{GROUND + 2}" rx="38" ry="5" fill="{c["accent"]}" opacity=".12"/>'
                     f'<g><animateTransform attributeName="transform" type="translate" values="{moves}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<g fill="{c["accent"]}"><animateTransform attributeName="transform" type="rotate" values="{turns}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     + uses +
                     f'<text x="{x}" y="{GROUND - HEIGHT - 10}" fill="{c["muted"]}" font-size="13" font-weight="700" text-anchor="middle">P{i + 1}</text>'
                     '</g></g>')
    # bursts where the fist lands: the punch reaches this far past the attacker's feet
    tip = min(x for x, _, _, _ in sets[-1])
    fist = [y for x, y, _, _ in sets[-1] if x < tip + 12]
    reach = (w / 2 - tip) * scale + 42
    height = (h - sum(fist) / len(fist)) * scale
    for when, attacker, victim, _ in HITS:
        x, facing = HEROES[attacker]
        parts += burst(when, round(x + facing * reach), round(GROUND - height), c['text'])
    return parts
