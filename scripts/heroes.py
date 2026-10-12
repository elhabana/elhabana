"""UN-CREDIBLES cover: four identical particle heroes brawling in two duels.

Every pose comes from the team's concept sketches: standing (side view), punch,
hit reaction, backflip, superhero landing and a selfie (taken by the puncher, with
the victim flying behind). Their particles were extracted
once (line art as bright dots, the body filled in as a plain suit) and live in
assets/uncredibles/particles.json; the drawings are not kept in the repo. The
in-between frames are particle morphs from the standing pose to each drawing.
"""
import json
import math
import random
from functools import lru_cache

from visuals import ASSETS

# head of each drawing as an ellipse (cx, cy, rx, ry) in its own pixels: heads pair
# with heads during a morph, so the face keeps its shape
HEADS = {'hero': (87, 89, 84, 90), 'punch': (151, 66, 84, 68), 'flip': (218, 90, 84, 88),
         'hit': (378, 95, 84, 85), 'land': (133, 98, 85, 92), 'selfie': (201, 85, 82, 80)}
# how each drawing is placed over the standing one: head over head, the supporting
# foot over the feet (the hit reaction leans far back), or centre of mass (in the air)
ALIGN = {'punch': 'head', 'land': 'head', 'hit': 'feet', 'flip': 'centre', 'selfie': 'head'}
STEP = 6            # particle spacing in source pixels, as extracted
BODY_ROWS = 36      # bodies are matched in this many rows, whatever their height
HEIGHT = 220        # standing hero height in the cover
GROUND = 276
LOOP = 6            # seconds: one round of the brawl
DT = .05
# x of each hero's feet and the way it faces (+1 right, -1 left): two duels
HEROES = ((265, 1), (385, -1), (795, 1), (915, -1))
# (time, attacker, victim, big): a big hit sends the victim into a backflip
HITS = ((.5, 0, 1, False), (1.1, 3, 2, False), (1.9, 1, 0, False),
        (2.6, 2, 3, False), (3.4, 0, 1, True), (4.2, 3, 2, True))
# morph steps from standing to each drawing (8 for the punch: smoother, not blurrier)
STEPS = {'punch': 8, 'hit': 4, 'flip': 6, 'land': 4, 'selfie': 4}

def frames_of(name):
    """In-between names from standing towards a drawing, e.g. punch1..punch7, punch."""
    n = STEPS[name]
    return [f'{name}{i}' for i in range(1, n)] + [name]

def sweep(names, start, end):
    """Spread frames evenly over [start, end): [(offset, name)]."""
    return [(round(start + (end - start) * i / len(names), 3), n) for i, n in enumerate(names)]

# which frame each hero shows, relative to the moment of a hit
PUNCH = (sweep(frames_of('punch'), -.3, -.06) + sweep(frames_of('punch')[-2::-1], .15, .39)
         + [(.39, 'idle')])
STAGGER = sweep(frames_of('hit'), 0, .06) + sweep(frames_of('hit')[-2::-1], .24, .33) + [(.33, 'idle')]
# a big hit goes straight into the backflip (no stagger first), lands like a hero, walks back
BACKFLIP = (sweep(frames_of('flip'), 0, .12) + sweep(frames_of('flip')[-2:-5:-1], .5, .56)
            + sweep(frames_of('land'), .56, .68) + sweep(frames_of('land')[-2::-1], 1.0, 1.09)
            + [(1.09, 'idle')])
# after a big hit the puncher pulls the arm back, turns its back on the flying victim
# and takes a selfie with it in the background; turns round again once it has landed
SELFIE = ([(o, n) for o, n in PUNCH if o < 0] + [(-.09 + 1e-3, 'punch'), (.06, 'punch5'), (.08, 'punch3'), (.1, 'punch1'),
          (.12, 'turned')] + sweep(frames_of('selfie'), .14, .22) + sweep(frames_of('selfie')[-2::-1], .62, .68)
          + [(.68, 'turned'), (.74, 'idle')])
FLASH = .36         # seconds after a big hit: the victim is at the top of its flip, click
LANDING = .66       # seconds after a big hit: feet (and fist) hit the ground (land frame at .65)


@lru_cache(maxsize=None)
def drawing(name):
    """[(x, y, radius, opacity)] in source pixels of one drawing, with its size."""
    pose = json.loads((ASSETS / 'uncredibles' / 'particles.json').read_text(encoding='utf-8'))[name]
    return [tuple(d) for d in pose['dots']], pose['width'], pose['height']

def in_head(name, x, y, margin=1.1):
    cx, cy, rx, ry = HEADS[name]
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < margin

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

def match_bodies(a, b):
    """Bodies differ in height (a crouch, a lean): match them in BODY_ROWS rows."""
    def squash(dots):
        top, bottom = min(d[1] for d in dots), max(d[1] for d in dots)
        step = (bottom - top) / BODY_ROWS
        return [(x, (y - top) / step, r, o) for x, y, r, o in dots], top, step
    (sa, at, ha), (sb, bt, hb) = squash(a), squash(b)
    return [((u[0], at + u[1] * ha, u[2], u[3]), (v[0], bt + v[1] * hb, v[2], v[3])) for u, v in by_rows(sa, sb, 1)]

@lru_cache(maxsize=None)
def morph(target):
    """Particle pairs (standing, target), with the target placed in the standing drawing's pixels."""
    idle, _, _ = drawing('hero')
    dots, _, _ = drawing(target)
    mean = lambda values: sum(values) / len(values)
    feet = lambda ds: mean([x for x, y, _, _ in ds if y > max(d[1] for d in ds) - 12])
    if ALIGN[target] == 'centre':
        ox = mean([d[0] for d in idle]) - mean([d[0] for d in dots])
        oy = mean([d[1] for d in idle]) - mean([d[1] for d in dots])
    else:
        ox = HEADS['hero'][0] - HEADS[target][0] if ALIGN[target] == 'head' else feet(idle) - feet(dots)
        oy = max(d[1] for d in idle) - max(d[1] for d in dots)
    head_b = [(x + ox, y + oy, r, o) for x, y, r, o in dots if in_head(target, x, y)]
    body_b = [(x + ox, y + oy, r, o) for x, y, r, o in dots if not in_head(target, x, y)]
    head_a = [d for d in idle if in_head('hero', d[0], d[1])]
    body_a = [d for d in idle if not in_head('hero', d[0], d[1])]
    return by_rows(head_a, head_b, STEP) + match_bodies(body_a, body_b)

def blend(pairs, t):
    e = t * t * (3 - 2 * t)
    # unequal sets pair some particles twice; identical copies would only add bytes
    return list(dict.fromkeys(tuple(round(p + (q - p) * e, 1) for p, q in zip(u, v)) for u, v in pairs))

@lru_cache(maxsize=None)
def poses():
    """Every particle set the heroes switch between, by name, in standing-drawing pixels."""
    idle, w, h = drawing('hero')
    out = {'idle': idle}
    for target, steps in STEPS.items():
        pairs = morph(target)
        for i, name in enumerate(frames_of(target), 1):
            out[name] = blend(pairs, i / steps)
    # the selfie is taken with the hero's back to its opponent: mirror it in place
    mirror = lambda dots: [(round(w - x, 1), y, r, o) for x, y, r, o in dots]
    out['turned'] = mirror(idle)
    for name in frames_of('selfie'):
        out[name] = mirror(out[name])
    return out, w, h

def geometry():
    """Distances in the cover: how far the fist sticks out, where the victim's body starts, fist height."""
    sets, w, h = poses()
    scale = HEIGHT / h
    tip = min(x for x, _, _, _ in sets['punch'])
    fist = [y for x, y, _, _ in sets['punch'] if x < tip + 12]
    fist_y = sum(fist) / len(fist)
    front = min(x for x, y, _, _ in sets['idle'] if abs(y - fist_y) < 15)
    return (w / 2 - tip) * scale, (w / 2 - front) * scale, (h - fist_y) * scale

def lunge(attacker, victim):
    """Step forward so the fist tip lands right on the victim's body, not short of it."""
    tip, front, _ = geometry()
    return abs(HEROES[victim][0] - HEROES[attacker][0]) - tip - front + 3

def frame_at(hero, t):
    """Which particle set a hero shows at t."""
    for when, attacker, victim, big in HITS:
        steps = BACKFLIP if big else STAGGER
        if victim == hero and when <= t < when + steps[-1][0]:
            return [name for offset, name in steps if t - when >= offset - 1e-9][-1]
    for when, attacker, _, big in HITS:
        steps = SELFIE if big else PUNCH
        if attacker == hero and when + steps[0][0] <= t < when + steps[-1][0]:
            return [name for offset, name in steps if t - when >= offset - 1e-9][-1]
    return 'idle'

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
            step = lunge(attacker, victim)
            dx += facing * ramp(t, [(when - .3, 0), (when, step), (when + .15, step), (when + .4, 0)])
        if hero == victim and not big:
            dx -= facing * ramp(t, [(when, 0), (when + .12, 46), (when + .7, 0)])
            angle -= facing * ramp(t, [(when, 0), (when + .12, 6), (when + .5, 0)])
        if hero == victim and big:
            land = when + LANDING
            dx -= facing * ramp(t, [(when, 0), (when + .35, 80), (land, 95), (when + 1.1, 95), (when + 1.8, 0)])
            dy -= ramp(t, [(when, 0), (when + .33, 75), (land, 0)])
            angle -= facing * ramp(t, [(when, 0), (land - .06, 360), (land, 360)])
    return round(dx, 1), round(dy, 1), round(angle, 1)

def track(hero):
    times = [round(i * DT, 2) for i in range(int(LOOP / DT) + 1)]
    steps, turned = [], 0
    for t in times:
        dx, dy, angle = pose(hero, t)
        # after a full flip the angle snaps back to 0; keep it continuous (360 looks the same)
        while steps and angle + turned - steps[-1][2] > 180:
            turned -= 360
        while steps and angle + turned - steps[-1][2] < -180:
            turned += 360
        steps.append((dx, dy, round(angle + turned, 1)))
    x = HEROES[hero][0]
    return {'keys': ';'.join(f'{t / LOOP:.4f}' for t in times),
            'moves': ';'.join(f'{dx} {dy}' for dx, dy, _ in steps),
            'turns': ';'.join(f'{a} {x} {GROUND - HEIGHT * .45:.0f}' for _, _, a in steps),
            # the shadow stays on the ground, follows dx and shrinks while airborne
            'shadow': ';'.join(f'{dx} 0' for dx, _, _ in steps),
            'shadow_rx': ';'.join(f'{38 * max(.45, 1 + min(0, dy) / 110):.1f}' for _, dy, _ in steps)}

def burst(when, x, y, ink, ground=False):
    """Particles flying out of an impact point, or a puff of dust along the ground."""
    rnd, out = random.Random(int(when * 100) + ground), []
    k = lambda t: f'{min(t, LOOP) / LOOP:.4f}'
    for _ in range(16 if ground else 12):
        if ground:
            ex, ey = round(rnd.choice((-1, 1)) * rnd.uniform(16, 62)), round(-rnd.uniform(2, 22))
        else:
            angle, reach = rnd.uniform(0, 2 * math.pi), rnd.uniform(18, 46)
            ex, ey = round(math.cos(angle) * reach), round(math.sin(angle) * reach)
        out.append(f'<circle cx="{x}" cy="{y}" r="{rnd.uniform(1.2, 2.4):.1f}" fill="{ink}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k(when)};{k(when + .05)};{k(when + .45)};1" '
                   f'dur="{LOOP}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{ex} {ey};{ex} {ey}" '
                   f'keyTimes="0;{k(when)};{k(when + .45)};1" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
    return out

def schedule(attribute, value_at):
    """A looping discrete animation from a function of time, keeping only the changes."""
    keys, values = [], []
    for i in range(int(LOOP / .01)):
        t = round(i * .01, 2)
        v = str(value_at(t))
        if not values or v != values[-1]:
            keys.append(f'{t / LOOP:.4f}')
            values.append(v)
    return (f'<animate attributeName="{attribute}" values="{";".join(values)}" keyTimes="{";".join(keys)}" '
            f'dur="{LOOP}s" calcMode="discrete" repeatCount="indefinite"/>')

def dots_path(dots):
    """Particles as round-capped zero-length strokes, one path per brightness level:
    about a quarter of the bytes of one <circle> per particle."""
    groups = {}
    for x, y, r, o in dots:
        groups.setdefault((round(r / .3) * .3, round(o / .15) * .15), []).append(f'M{x:g} {y:g}h0')
    return ''.join(f'<path stroke-width="{2 * r:.2f}" stroke-opacity="{o:.2f}" d="{"".join(d)}"/>'
                   for (r, o), d in sorted(groups.items()))

def brawl(c):
    sets, w, h = poses()
    scale = HEIGHT / h
    defs = ''.join(f'<g id="hero-{name}">{dots_path(dots)}</g>' for name, dots in sets.items())
    parts = [f'<defs>{defs}</defs>',
             f'<line x1="40" y1="{GROUND + 2}" x2="1140" y2="{GROUND + 2}" stroke="{c["line"]}" stroke-dasharray="2 6"/>']
    for i, (x, facing) in enumerate(HEROES):
        tr = track(i)
        keys = tr['keys']
        # the sketches face left; mirror them for heroes facing right
        place = f'translate({x} {GROUND}) scale({-facing * scale:.4f} {scale:.4f}) translate({-w / 2:.0f} {-h})'
        uses = ''
        for name in sets:
            hidden = '' if name == 'idle' else ' opacity="0"'
            shown = schedule('opacity', lambda t, name=name: int(frame_at(i, t) == name))
            uses += f'<use href="#hero-{name}" transform="{place}"{hidden}>{shown}</use>'
        hit_by = lambda t: any(v == i and when <= t < when + .1 for when, _, v, _ in HITS)
        flash = schedule('stroke', lambda t: c['text'] if hit_by(t) else c['accent'])
        parts.append(f'<ellipse cx="{x}" cy="{GROUND + 2}" rx="38" ry="5" fill="{c["accent"]}" opacity=".12">'
                     f'<animateTransform attributeName="transform" type="translate" values="{tr["shadow"]}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="rx" values="{tr["shadow_rx"]}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/></ellipse>'
                     f'<g><animateTransform attributeName="transform" type="translate" values="{tr["moves"]}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<g><animateTransform attributeName="transform" type="rotate" values="{tr["turns"]}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<g stroke="{c["accent"]}" stroke-linecap="round" fill="none">{flash}{uses}</g></g>'
                     # the label follows the hero but never spins with it
                     f'<text x="{x}" y="{GROUND - HEIGHT - 10}" fill="{c["muted"]}" font-size="13" font-weight="700" text-anchor="middle">P{i + 1}</text>'
                     '</g>')
    tip, _, fist_height = geometry()
    # where the phone is in the selfie (its most forward particles), for the flash
    front = max(x for x, _, _, _ in sets['selfie'])
    phone = [(x, y) for x, y, _, _ in sets['selfie'] if x > front - 30]
    px, py = sum(x for x, _ in phone) / len(phone), sum(y for _, y in phone) / len(phone)
    for when, attacker, victim, big in HITS:
        if big:
            x, facing = HEROES[attacker]
            t = round(when + FLASH, 2)
            dx, dy, _ = pose(attacker, t)
            fx, fy = round(x + dx - facing * scale * (px - w / 2)), round(GROUND + dy + scale * (py - h))
            k = lambda u: f'{min(u, LOOP) / LOOP:.4f}'
            parts.append(f'<circle cx="{fx}" cy="{fy}" r="2" fill="{c["text"]}" opacity="0">'
                         f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k(t)};{k(t + .03)};{k(t + .2)};1" dur="{LOOP}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="r" values="2;2;22;30;2" keyTimes="0;{k(t)};{k(t + .06)};{k(t + .2)};1" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
    for when, attacker, victim, big in HITS:
        x, facing = HEROES[attacker]
        parts += burst(when, round(x + facing * (tip + lunge(attacker, victim))), round(GROUND - fist_height), c['text'])
        if big:
            # dust where the landing fist slams into the ground
            vx, vfacing = HEROES[victim]
            parts += burst(round(when + LANDING, 2), round(vx - vfacing * 95 + vfacing * 30), GROUND, c['text'], ground=True)
    return parts
